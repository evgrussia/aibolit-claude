"""Chat service for multi-turn AI consultations via Claude CLI.

Uses --session-id / --resume for conversation continuity,
and --output-format stream-json for SSE streaming.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
from typing import AsyncIterator

from src.agents.specializations import Specialization

logger = logging.getLogger("aibolit.chat_service")

_TIMEOUT = int(os.environ.get("CLAUDE_TIMEOUT", "120"))
_MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")


def is_available() -> bool:
    """Check if claude CLI is installed."""
    return shutil.which("claude") is not None


def _clean_env() -> dict[str, str]:
    """Build env without CLAUDECODE* vars to allow nested CLI invocation."""
    skip = {"CLAUDECODE", "CLAUDE_CODE_SSE_PORT", "CLAUDE_CODE_ENTRYPOINT"}
    return {k: v for k, v in os.environ.items() if k not in skip}


def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent prompt injection."""
    text = re.sub(
        r'(?i)(ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?))',
        '[removed]', text,
    )
    text = re.sub(
        r'(?i)(you\s+are\s+now|act\s+as|pretend\s+(to\s+be|you\s+are)|system\s*:)',
        '[removed]', text,
    )
    text = re.sub(r'<[^>]{0,50}>', '', text)
    return text[:5000].strip()


def build_system_prompt(
    specialty_name: str,
    patient_context: str,
    specialization: Specialization | None = None,
) -> str:
    """Build the system prompt for a chat consultation session."""
    parts: list[str] = []

    parts.append(f"Ты — AI-{specialty_name} в виртуальной клинике Aibolit.")
    parts.append(
        "Ты ведёшь диалог с пациентом. Ты — квалифицированный AI-ассистент, "
        "который помогает пациентам разобраться в их симптомах. "
        "Ты НЕ ставишь диагнозы и НЕ назначаешь лечение — "
        "ты предоставляешь информацию для обсуждения с лечащим врачом."
    )

    if specialization:
        skills_text = ", ".join(s.name for s in specialization.skills[:6])
        if skills_text:
            parts.append(f"\nТвои компетенции: {skills_text}.")
        if specialization.related_icd_prefixes:
            icd = ", ".join(specialization.related_icd_prefixes[:8])
            parts.append(f"Ключевые группы МКБ-10: {icd}.")

    if patient_context and patient_context != "Карта пациента не загружена":
        parts.append(f"\nДанные из медицинской карты пациента:\n{patient_context}")
        parts.append(
            "\nУчитывай данные карты при анализе: аллергии, текущие препараты, "
            "хронические заболевания и предыдущие результаты обследований."
        )

    parts.append("""
Правила:
- Отвечай на русском языке
- Веди диалог: задавай уточняющие вопросы по одному-два за раз
- Будь конкретен и профессионален
- Используй формулировки "ВОЗМОЖНО", "МОЖЕТ БЫТЬ СВЯЗАНО С", "РЕКОМЕНДУЕТСЯ ОБСУДИТЬ С ВРАЧОМ"
- НИКОГДА не используй формулировки "У вас [диагноз]", "Вам нужно принимать [лекарство]"
- Если пациент прикрепил файл (изображение, PDF), прочитай и проанализируй его
- В конце каждого ответа напоминай: рекомендации носят информационный характер
""")

    return "\n".join(parts)


async def start_session(
    session_id: str,
    system_prompt: str,
    initial_message: str,
) -> AsyncIterator[str]:
    """Start a new Claude CLI session and stream the response."""
    prompt = f"{system_prompt}\n\nПациент: {initial_message}"

    cmd = [
        "claude", "--print", "--verbose",
        "--model", _MODEL,
        "--session-id", session_id,
        "--max-turns", "3",
        "--output-format", "stream-json",
        prompt,
    ]

    async for chunk in _run_claude_stream(cmd):
        yield chunk


async def send_message(session_id: str, message: str) -> AsyncIterator[str]:
    """Continue an existing session with a new message (streaming)."""
    cmd = [
        "claude", "--print", "--verbose",
        "--resume", session_id,
        "--max-turns", "3",
        "--output-format", "stream-json",
        message,
    ]

    async for chunk in _run_claude_stream(cmd):
        yield chunk


async def send_message_sync(session_id: str, message: str) -> str:
    """Non-streaming variant — collect full response."""
    chunks: list[str] = []
    async for chunk in send_message(session_id, message):
        chunks.append(chunk)
    return "".join(chunks)


async def _run_claude_stream(cmd: list[str]) -> AsyncIterator[str]:
    """Execute Claude CLI and yield text chunks from stream-json output."""
    env = _clean_env()
    proc = None

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            limit=100 * 1024 * 1024,  # 100 MB — default 64KB too small for large JSON lines
        )

        assert proc.stdout is not None

        full_text: list[str] = []

        async def _read_stream():
            while True:
                line = await asyncio.wait_for(
                    proc.stdout.readline(),
                    timeout=_TIMEOUT,
                )
                if not line:
                    break
                yield line.decode(errors="replace").strip()

        async for raw_line in _read_stream():
            if not raw_line:
                continue

            try:
                data = json.loads(raw_line)
            except json.JSONDecodeError:
                # Some lines may not be JSON (stderr leaking, etc.)
                continue

            msg_type = data.get("type", "")

            # Extract text from assistant message content blocks
            if msg_type == "content_block_delta":
                delta = data.get("delta", {})
                if delta.get("type") == "text_delta":
                    text = delta.get("text", "")
                    if text:
                        full_text.append(text)
                        yield text

            # Also handle assistant result type (complete message)
            elif msg_type == "result":
                result_text = ""
                # Try to extract from result.content
                content = data.get("result", "")
                if isinstance(content, str) and content and not full_text:
                    result_text = content
                elif isinstance(content, dict):
                    # Nested content blocks
                    blocks = content.get("content", [])
                    if isinstance(blocks, list):
                        for block in blocks:
                            if isinstance(block, dict) and block.get("type") == "text":
                                result_text += block.get("text", "")
                if result_text and not full_text:
                    yield result_text

        # Wait for process to complete
        await asyncio.wait_for(proc.wait(), timeout=10)

        if proc.returncode != 0:
            stderr = ""
            if proc.stderr:
                stderr = (await proc.stderr.read()).decode(errors="replace")[:500]
            logger.error("Claude CLI failed (rc=%s): %s", proc.returncode, stderr)

    except asyncio.TimeoutError:
        logger.error("Claude CLI stream timed out after %ss", _TIMEOUT)
        if proc is not None:
            try:
                proc.kill()
                await proc.wait()
            except Exception as e:
                logger.warning("Failed to kill timed-out Claude process: %s", e)
    except Exception:
        logger.exception("Claude CLI stream unexpected error")
        if proc is not None:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
