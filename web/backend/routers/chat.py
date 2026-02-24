"""Chat consultation endpoints — multi-turn AI doctor chats with file uploads."""
import json
import logging
import os
import uuid
from typing import AsyncIterator

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agents.specializations import get_specialization
from src.safety.disclaimers import DisclaimerType, get_disclaimer
from src.safety.red_flags import RedFlagDetector
from src.utils.database import (
    add_chat_message,
    close_consultation,
    create_chat_consultation,
    get_chat_attachment,
    get_chat_messages,
    get_consultation_by_id,
    get_patient_chat_consultations,
    load_patient,
    save_chat_attachment,
)
from ..auth import get_current_user
from ..services import chat_service
from ..services.audit_service import AuditLogService

logger = logging.getLogger("aibolit.chat")
router = APIRouter(prefix="/chat", tags=["chat"])

_red_flag_detector = RedFlagDetector()

# Attachment limits
_MAX_FILES = 5
_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
_ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf",
    "text/plain",
}

# Base path for file attachments
_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "data",
)


def _build_referral_event(ai_text: str, current_specialty: str) -> list[dict]:
    """Detect specialist referrals in AI response and enrich with display names."""
    raw = chat_service.detect_referrals(ai_text, current_specialty)
    if not raw:
        return []
    enriched: list[dict] = []
    for ref in raw:
        ref_spec = get_specialization(ref["specialty_id"])
        if ref_spec:
            enriched.append({
                "specialty_id": ref_spec.id,
                "name": f"AI-{ref_spec.name_ru}",
                "specialty_name": ref_spec.name_ru,
            })
    return enriched


class ChatCreateRequest(BaseModel):
    specialty: str
    complaints: str


# ── POST /chat/create ─────────────────────────────────────

@router.post("/create")
async def create_chat(
    req: ChatCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new chat consultation and stream the first AI response."""
    if not req.complaints or len(req.complaints.strip()) < 3:
        raise HTTPException(400, "Опишите жалобы (минимум 3 символа)")

    spec = get_specialization(req.specialty)
    if not spec:
        raise HTTPException(404, "Специализация не найдена")

    if not chat_service.is_available():
        raise HTTPException(503, "AI-сервис временно недоступен (Claude CLI не найден)")

    patient_id = current_user.get("patient_id")
    logger.info(
        "[CHAT_CREATE] patient=%s, specialty=%s, complaints_len=%d",
        patient_id, req.specialty, len(req.complaints),
    )

    patient_context = "Карта пациента не загружена"
    if patient_id:
        patient = load_patient(patient_id)
        if patient:
            patient_context = patient.summary()
            logger.info("[CHAT_CREATE] Patient card loaded: %d chars", len(patient_context))

    session_id = str(uuid.uuid4())
    safe_complaints = chat_service.sanitize_user_input(req.complaints.strip())

    # Create consultation in DB
    title = safe_complaints[:80]
    consultation_id = create_chat_consultation(
        patient_id=patient_id,
        specialty=req.specialty,
        complaints=safe_complaints,
        session_id=session_id,
        title=title,
    )

    # Save user message
    add_chat_message(consultation_id, "user", safe_complaints)

    AuditLogService.log_medical(
        "chat_consultation_created",
        data={"consultation_id": consultation_id, "patient_id": patient_id,
              "specialty": req.specialty, "session_id": session_id},
        actor=current_user,
    )

    # Red flags
    flags = _red_flag_detector.detect(safe_complaints)
    red_flags_data = None
    emergency_data = None

    logger.info(
        "[CHAT_CREATE] session=%s, red_flags=%d, emergency=%s",
        session_id, len(flags) if flags else 0, False,
    )

    if flags:
        red_flags_data = [
            {"category": f.category, "description": f.description, "urgency": int(f.urgency), "action": f.action}
            for f in flags
        ]
        immediate = [f for f in flags if f.urgency >= 5]
        if immediate:
            emergency_data = {
                "call": "103 / 112",
                "message": "Обнаружены признаки, требующие экстренной медицинской помощи!",
                "flags": [{"category": f.category, "description": f.description, "action": f.action} for f in immediate],
            }

        AuditLogService.log_medical(
            "red_flag_detected",
            data={"consultation_id": consultation_id, "patient_id": patient_id,
                  "flags_count": len(flags), "emergency": bool(immediate),
                  "categories": [f.category for f in flags]},
            actor="system",
            level="WARNING",
        )

    # Build disclaimers
    disclaimers = [DisclaimerType.GENERAL, DisclaimerType.DIAGNOSIS]
    if req.specialty == "pediatrician":
        disclaimers.append(DisclaimerType.CHILDREN)
    disclaimer_text = " ".join(get_disclaimer(d) for d in disclaimers)
    if emergency_data:
        disclaimer_text = get_disclaimer(DisclaimerType.EMERGENCY) + " " + disclaimer_text

    # Doctor info
    doctor_info = {
        "specialty_id": spec.id,
        "name": f"AI-{spec.name_ru}",
        "qualification": spec.description,
    }

    system_prompt = chat_service.build_system_prompt(
        specialty_name=spec.name_ru,
        patient_context=patient_context,
        specialization=spec,
    )

    async def event_stream() -> AsyncIterator[str]:
        # Send meta event first
        meta = {
            "consultation_id": consultation_id,
            "doctor": doctor_info,
            "disclaimer": disclaimer_text,
        }
        if red_flags_data:
            meta["red_flags"] = red_flags_data
        if emergency_data:
            meta["emergency"] = emergency_data
        yield f"event: meta\ndata: {json.dumps(meta, ensure_ascii=False)}\n\n"

        full_text_parts: list[str] = []
        try:
            async for chunk in chat_service.start_session(session_id, system_prompt, safe_complaints):
                full_text_parts.append(chunk)
                yield f"event: delta\ndata: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
        except Exception:
            logger.exception("Error streaming chat response for consultation=%s", consultation_id)
            yield f"event: error\ndata: {json.dumps({'error': 'Ошибка генерации ответа'}, ensure_ascii=False)}\n\n"
            return

        full_text = "".join(full_text_parts)
        if full_text:
            msg_id = add_chat_message(consultation_id, "assistant", full_text)
            logger.info(
                "[CHAT_CREATE_DONE] consultation=%s, response_len=%d, msg_id=%s",
                consultation_id, len(full_text), msg_id,
            )

            AuditLogService.log_medical(
                "ai_chat_response_generated",
                data={"consultation_id": consultation_id, "message_id": msg_id,
                      "response_len": len(full_text), "specialty": req.specialty},
                actor="system",
            )

            yield f"event: done\ndata: {json.dumps({'message_id': msg_id, 'full_text': full_text}, ensure_ascii=False)}\n\n"

            # Detect referrals to other specialists
            referral_events = _build_referral_event(full_text, req.specialty)
            if referral_events:
                yield f"event: referral\ndata: {json.dumps({'referrals': referral_events}, ensure_ascii=False)}\n\n"
        else:
            logger.warning("[CHAT_CREATE_EMPTY] consultation=%s, empty AI response", consultation_id)
            yield f"event: error\ndata: {json.dumps({'error': 'Пустой ответ от AI'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── POST /chat/{id}/message ───────────────────────────────

@router.post("/{consultation_id}/message")
async def send_chat_message(
    consultation_id: int,
    text: str = Form(""),
    files: list[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_current_user),
):
    """Send a message (text + optional files) and stream AI response."""
    consultation = get_consultation_by_id(consultation_id)
    if not consultation:
        raise HTTPException(404, "Консультация не найдена")

    patient_id = current_user.get("patient_id")
    if consultation["patient_id"] != patient_id:
        raise HTTPException(403, "Нет доступа к этой консультации")

    if consultation.get("status") != "active":
        raise HTTPException(400, "Консультация закрыта")

    session_id = consultation.get("session_id")
    if not session_id:
        raise HTTPException(400, "Консультация не поддерживает чат")

    logger.info(
        "[CHAT_MSG] consultation=%s, session=%s, patient=%s, text_len=%d, files=%d",
        consultation_id, session_id, patient_id, len(text.strip()), len(files),
    )

    if not text.strip() and not files:
        raise HTTPException(400, "Сообщение не может быть пустым")

    safe_text = chat_service.sanitize_user_input(text.strip()) if text.strip() else ""

    # Validate and save files
    if len(files) > _MAX_FILES:
        raise HTTPException(400, f"Максимум {_MAX_FILES} файлов за раз")

    saved_files: list[dict] = []
    att_dir = os.path.join(_DATA_DIR, "attachments", str(consultation_id))

    for f in files:
        if not f.filename:
            continue
        if f.content_type and f.content_type not in _ALLOWED_TYPES:
            raise HTTPException(400, f"Неподдерживаемый тип файла: {f.content_type}")

        content = await f.read()
        if len(content) > _MAX_FILE_SIZE:
            raise HTTPException(400, f"Файл {f.filename} превышает 10 МБ")

        os.makedirs(att_dir, exist_ok=True)
        # Sanitize filename
        safe_name = f.filename.replace("/", "_").replace("\\", "_").replace("..", "_")
        # Add uuid prefix to avoid collisions
        unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
        file_path = os.path.join(att_dir, unique_name)
        with open(file_path, "wb") as fp:
            fp.write(content)

        saved_files.append({
            "file_name": safe_name,
            "file_type": f.content_type or "application/octet-stream",
            "file_size": len(content),
            "file_path": file_path,
        })

    # Save user message to DB
    user_msg_id = add_chat_message(consultation_id, "user", safe_text or "[файл]")

    AuditLogService.log_medical(
        "chat_message_sent",
        data={"consultation_id": consultation_id, "patient_id": patient_id,
              "message_id": user_msg_id, "has_files": bool(saved_files)},
        actor=current_user,
    )

    # Save attachments
    for sf in saved_files:
        save_chat_attachment(
            consultation_id=consultation_id,
            message_id=user_msg_id,
            file_name=sf["file_name"],
            file_type=sf["file_type"],
            file_size=sf["file_size"],
            file_path=sf["file_path"],
        )

    # Build prompt for Claude
    prompt_parts: list[str] = []
    if safe_text:
        prompt_parts.append(safe_text)
    for sf in saved_files:
        prompt_parts.append(
            f"\nПациент прикрепил файл: {sf['file_path']} (имя: {sf['file_name']}, тип: {sf['file_type']}). "
            "Проанализируй содержимое этого файла."
        )

    full_prompt = "\n".join(prompt_parts)

    # Prepare fallback context in case session was lost (container rebuild)
    spec = get_specialization(consultation["specialty"])
    fallback_patient_context = "Карта пациента не загружена"
    if patient_id:
        p = load_patient(patient_id)
        if p:
            fallback_patient_context = p.summary()
    fallback_system_prompt = chat_service.build_system_prompt(
        specialty_name=spec.name_ru if spec else consultation["specialty"],
        patient_context=fallback_patient_context,
        specialization=spec,
    )
    # Load chat history for session recovery
    history_rows = get_chat_messages(consultation_id)
    chat_history = [{"role": m["role"], "text": m.get("content", "")} for m in history_rows]

    # Red flags on user text
    flags = _red_flag_detector.detect(safe_text) if safe_text else []
    red_flags_data = None
    emergency_data = None
    if flags:
        red_flags_data = [
            {"category": f.category, "description": f.description, "urgency": int(f.urgency), "action": f.action}
            for f in flags
        ]
        immediate = [f for f in flags if f.urgency >= 5]
        if immediate:
            emergency_data = {
                "call": "103 / 112",
                "message": "Обнаружены признаки, требующие экстренной медицинской помощи!",
                "flags": [{"category": f.category, "description": f.description, "action": f.action} for f in immediate],
            }

        AuditLogService.log_medical(
            "red_flag_detected",
            data={"consultation_id": consultation_id, "patient_id": patient_id,
                  "flags_count": len(flags), "emergency": bool(immediate),
                  "categories": [f.category for f in flags]},
            actor="system",
            level="WARNING",
        )

    async def event_stream() -> AsyncIterator[str]:
        # Meta event with red flags if any
        if red_flags_data or emergency_data:
            meta: dict = {}
            if red_flags_data:
                meta["red_flags"] = red_flags_data
            if emergency_data:
                meta["emergency"] = emergency_data
            yield f"event: meta\ndata: {json.dumps(meta, ensure_ascii=False)}\n\n"

        full_text_parts: list[str] = []
        try:
            async for chunk in chat_service.send_message(
                session_id,
                full_prompt,
                system_prompt=fallback_system_prompt,
                chat_history=chat_history,
            ):
                full_text_parts.append(chunk)
                yield f"event: delta\ndata: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
        except Exception:
            logger.exception("Error streaming message for consultation=%s", consultation_id)
            yield f"event: error\ndata: {json.dumps({'error': 'Ошибка генерации ответа'}, ensure_ascii=False)}\n\n"
            return

        full_text = "".join(full_text_parts)
        if full_text:
            msg_id = add_chat_message(consultation_id, "assistant", full_text)
            logger.info(
                "[CHAT_MSG_DONE] consultation=%s, response_len=%d, msg_id=%s",
                consultation_id, len(full_text), msg_id,
            )
            AuditLogService.log_medical(
                "ai_chat_response_generated",
                data={"consultation_id": consultation_id, "patient_id": patient_id,
                      "message_id": msg_id, "response_length": len(full_text)},
                actor="system",
            )
            yield f"event: done\ndata: {json.dumps({'message_id': msg_id, 'full_text': full_text}, ensure_ascii=False)}\n\n"

            # Detect referrals to other specialists
            referral_events = _build_referral_event(full_text, consultation["specialty"])
            if referral_events:
                yield f"event: referral\ndata: {json.dumps({'referrals': referral_events}, ensure_ascii=False)}\n\n"
        else:
            logger.warning("[CHAT_MSG_EMPTY] consultation=%s, empty AI response", consultation_id)
            yield f"event: error\ndata: {json.dumps({'error': 'Пустой ответ от AI'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── GET /chat/{id}/messages ───────────────────────────────

@router.get("/{consultation_id}/messages")
def list_messages(
    consultation_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get all messages for a consultation."""
    consultation = get_consultation_by_id(consultation_id)
    if not consultation:
        raise HTTPException(404, "Консультация не найдена")
    if consultation["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(403, "Нет доступа к этой консультации")
    return get_chat_messages(consultation_id)


# ── GET /chat/{id} ────────────────────────────────────────

@router.get("/{consultation_id}")
def get_chat_info(
    consultation_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get consultation metadata."""
    consultation = get_consultation_by_id(consultation_id)
    if not consultation:
        raise HTTPException(404, "Консультация не найдена")
    if consultation["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(403, "Нет доступа к этой консультации")

    spec = get_specialization(consultation["specialty"])
    return {
        "id": consultation["id"],
        "specialty": consultation["specialty"],
        "status": consultation.get("status", "legacy"),
        "title": consultation.get("title", ""),
        "complaints": consultation["complaints"],
        "date": consultation["date"],
        "session_id": consultation.get("session_id"),
        "doctor": {
            "specialty_id": spec.id if spec else consultation["specialty"],
            "name": f"AI-{spec.name_ru}" if spec else f"AI-{consultation['specialty']}",
            "qualification": spec.description if spec else "",
        },
    }


# ── GET /chat/my ──────────────────────────────────────────

@router.get("")
def my_chats(
    current_user: dict = Depends(get_current_user),
):
    """Get all consultations for the current user."""
    patient_id = current_user.get("patient_id")
    if not patient_id:
        return []

    rows = get_patient_chat_consultations(patient_id)
    results = []
    for r in rows:
        spec = get_specialization(r["specialty"])
        results.append({
            "id": r["id"],
            "specialty": r["specialty"],
            "status": r.get("status") or "legacy",
            "title": r.get("title") or r["complaints"][:80],
            "date": r["date"],
            "last_message_preview": (r.get("last_message") or "")[:120],
            "message_count": r.get("message_count", 0),
            "doctor": {
                "specialty_id": spec.id if spec else r["specialty"],
                "name": f"AI-{spec.name_ru}" if spec else f"AI-{r['specialty']}",
                "qualification": spec.description if spec else "",
            },
        })
    return results


# ── POST /chat/{id}/close ─────────────────────────────────

@router.post("/{consultation_id}/close")
def close_chat(
    consultation_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Close a consultation."""
    consultation = get_consultation_by_id(consultation_id)
    if not consultation:
        raise HTTPException(404, "Консультация не найдена")
    if consultation["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(403, "Нет доступа к этой консультации")
    if close_consultation(consultation_id):
        AuditLogService.log_medical(
            "chat_consultation_closed",
            data={"consultation_id": consultation_id, "patient_id": current_user.get("patient_id")},
            actor=current_user,
        )
        return {"status": "closed"}
    raise HTTPException(400, "Консультация уже закрыта или не найдена")


# ── GET /chat/attachments/{id} ────────────────────────────

@router.get("/attachments/{attachment_id}")
def download_attachment(
    attachment_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Download a chat attachment."""
    att = get_chat_attachment(attachment_id)
    if not att:
        raise HTTPException(404, "Файл не найден")

    # Verify ownership
    consultation = get_consultation_by_id(att["consultation_id"])
    if not consultation or consultation["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(403, "Нет доступа")

    file_path = att["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(404, "Файл не найден на диске")

    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        filename=att["file_name"],
        media_type=att["file_type"],
    )
