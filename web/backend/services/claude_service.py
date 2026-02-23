"""Service for calling Claude Code CLI to generate AI consultations.

Calls `claude --print` without MCP — all patient/specialization context
is pre-fetched by the backend and passed directly in the prompt.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil

from src.agents.specializations import Specialization

logger = logging.getLogger("aibolit.claude_service")

# Max time (seconds) to wait for Claude response
_TIMEOUT = int(os.environ.get("CLAUDE_TIMEOUT", "120"))


def is_available() -> bool:
    """Check if claude CLI is installed and authenticated."""
    return shutil.which("claude") is not None


async def generate_consultation(
    specialty_name: str,
    complaints: str,
    patient_context: str,
    specialization: Specialization | None = None,
) -> str | None:
    """Call Claude Code CLI and return AI-generated consultation text.

    Returns None if Claude is unavailable or fails.
    """
    if not is_available():
        logger.warning("Claude CLI not found")
        return None

    prompt = _build_prompt(specialty_name, complaints, patient_context, specialization)

    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            "claude",
            "--print",
            "--output-format", "text",
            "--max-turns", "1",
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=_TIMEOUT,
        )

        err_text = stderr.decode(errors="replace").strip()
        if proc.returncode != 0:
            logger.error("Claude CLI failed (rc=%s): %s", proc.returncode, err_text[:500])
            return None

        # Log stderr warnings even on success
        if err_text:
            logger.debug("Claude CLI stderr: %s", err_text[:300])

        text = stdout.decode(errors="replace").strip()
        if not text:
            logger.warning("Claude CLI returned empty response")
            return None

        return text

    except asyncio.TimeoutError:
        logger.error("Claude CLI timed out after %ss", _TIMEOUT)
        if proc is not None:
            try:
                proc.kill()
                await proc.wait()
            except Exception as e:
                logger.warning("Failed to kill timed-out Claude process: %s", e)
        return None
    except Exception:
        logger.exception("Claude CLI unexpected error")
        return None


def _sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent prompt injection.

    Strips control sequences and instruction-like patterns that could
    manipulate the AI model's behaviour.
    """
    # Remove text that looks like system/assistant instructions
    text = re.sub(
        r'(?i)(ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?))',
        '[removed]', text,
    )
    text = re.sub(
        r'(?i)(you\s+are\s+now|act\s+as|pretend\s+(to\s+be|you\s+are)|system\s*:)',
        '[removed]', text,
    )
    # Strip XML/HTML-like tags that may attempt injection
    text = re.sub(r'<[^>]{0,50}>', '', text)
    # Limit length to prevent context overflow
    return text[:5000].strip()


def _build_prompt(
    specialty_name: str,
    complaints: str,
    patient_context: str,
    specialization: Specialization | None = None,
) -> str:
    """Build a rich prompt with all context pre-fetched."""
    safe_complaints = _sanitize_user_input(complaints)

    parts: list[str] = []

    # --- Role ---
    parts.append(f"Ты — AI-{specialty_name} в виртуальной клинике Aibolit.")
    parts.append(
        "Ты — квалифицированный AI-ассистент, который помогает пациентам разобраться "
        "в их симптомах. Ты НЕ ставишь диагнозы и НЕ назначаешь лечение — "
        "ты предоставляешь информацию для обсуждения с лечащим врачом."
    )

    # --- Specialty-specific context ---
    if specialization:
        skills_text = ", ".join(s.name for s in specialization.skills[:6])
        if skills_text:
            parts.append(f"\nТвои компетенции: {skills_text}.")
        if specialization.related_icd_prefixes:
            icd = ", ".join(specialization.related_icd_prefixes[:8])
            parts.append(f"Ключевые группы МКБ-10 по твоей специализации: {icd}.")

    # --- Patient complaints ---
    parts.append(f"\nПациент обратился с жалобами: {safe_complaints}")

    # --- Patient medical history ---
    if patient_context and patient_context != "Карта пациента не загружена":
        parts.append(f"\nДанные из медицинской карты пациента:\n{patient_context}")
        parts.append(
            "\nУчитывай данные карты при анализе: аллергии, текущие препараты, "
            "хронические заболевания и предыдущие результаты обследований. "
            "Обрати внимание на возможные лекарственные взаимодействия."
        )
    else:
        parts.append(
            "\nКарта пациента не загружена. Отметь, что для более точной оценки "
            "важно знать анамнез, текущие препараты и аллергии."
        )

    # --- Instructions ---
    parts.append("""
Проведи полноценную медицинскую консультацию. Структурируй ответ:

## 1. Оценка жалоб
Проанализируй симптомы с точки зрения своей специализации. Задай уточняющие вопросы,
которые помогут врачу на очном приёме.

## 2. Возможные причины (дифференциальный диагноз)
Предложи 2–5 возможных причин симптомов. Для каждой укажи:
- Код МКБ-10
- Вероятность: ВЫСОКАЯ / УМЕРЕННАЯ / ВОЗМОЖНАЯ
- Краткое обоснование

## 3. Рекомендуемые обследования
Конкретные анализы и исследования для уточнения диагноза. Укажи приоритет:
- **Срочно**: нужно сделать в ближайшие дни
- **Плановые**: в течение 1–2 недель

## 4. Рекомендации
- Немедикаментозные меры (режим, диета, образ жизни)
- Информация о возможных препаратах (ТОЛЬКО справочно, без назначения)

## 5. Красные флаги
Перечисли симптомы, при которых нужно СРОЧНО обратиться к врачу или вызвать скорую (103/112).

Правила:
- Отвечай на русском языке
- Будь конкретен и профессионален
- Используй формулировки "ВОЗМОЖНО", "МОЖЕТ БЫТЬ СВЯЗАНО С", "РЕКОМЕНДУЕТСЯ ОБСУДИТЬ С ВРАЧОМ"
- НИКОГДА не используй формулировки "У вас [диагноз]", "Вам нужно принимать [лекарство]"
- Указывай уровень уверенности для каждого предположения
- В конце добавь напоминание: все рекомендации носят информационный характер""")

    return "\n".join(parts)
