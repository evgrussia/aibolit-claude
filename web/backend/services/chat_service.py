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
import time
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
    original_len = len(text)
    text = re.sub(
        r'(?i)(ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?))',
        '[removed]', text,
    )
    text = re.sub(
        r'(?i)(you\s+are\s+now|act\s+as|pretend\s+(to\s+be|you\s+are)|system\s*:)',
        '[removed]', text,
    )
    text = re.sub(r'<[^>]{0,50}>', '', text)
    result = text[:5000].strip()
    if len(result) != original_len:
        logger.info(
            "[SANITIZE] Input modified: %d→%d chars, truncated=%s",
            original_len, len(result), original_len > 5000,
        )
    return result


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

    prompt = "\n".join(parts)
    logger.info(
        "[PROMPT] Built system prompt: specialty=%s, patient_context=%s, prompt_len=%d",
        specialty_name,
        "loaded" if patient_context != "Карта пациента не загружена" else "none",
        len(prompt),
    )
    return prompt


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

    logger.info(
        "[SESSION_START] session=%s, model=%s, prompt_len=%d, message_len=%d",
        session_id, _MODEL, len(system_prompt), len(initial_message),
    )

    async for chunk in _run_claude_stream(cmd, session_id=session_id, action="start"):
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

    logger.info(
        "[SESSION_RESUME] session=%s, message_len=%d",
        session_id, len(message),
    )

    async for chunk in _run_claude_stream(cmd, session_id=session_id, action="resume"):
        yield chunk


async def send_message_sync(session_id: str, message: str) -> str:
    """Non-streaming variant — collect full response."""
    chunks: list[str] = []
    async for chunk in send_message(session_id, message):
        chunks.append(chunk)
    return "".join(chunks)


async def _run_claude_stream(
    cmd: list[str],
    *,
    session_id: str = "",
    action: str = "unknown",
) -> AsyncIterator[str]:
    """Execute Claude CLI and yield text chunks from stream-json output."""
    env = _clean_env()
    proc = None
    t0 = time.time()

    # Log command (mask prompt content for security)
    safe_cmd = [c if len(c) < 200 else f"{c[:80]}...({len(c)} chars)" for c in cmd]
    logger.debug("[CLI_CMD] %s", " ".join(safe_cmd))

    stderr_lines: list[str] = []

    async def _drain_stderr():
        """Read stderr concurrently so it doesn't block and is available for error logging."""
        assert proc is not None and proc.stderr is not None
        while True:
            line = await proc.stderr.readline()
            if not line:
                break
            decoded = line.decode(errors="replace").strip()
            if decoded:
                stderr_lines.append(decoded)
                logger.debug("[CLI_STDERR] %s", decoded)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            limit=100 * 1024 * 1024,
        )

        logger.info(
            "[CLI_STARTED] pid=%s, action=%s, session=%s",
            proc.pid, action, session_id,
        )

        assert proc.stdout is not None

        # Start draining stderr in background
        stderr_task = asyncio.create_task(_drain_stderr())

        full_text: list[str] = []
        chunk_count = 0
        json_errors = 0
        event_types_seen: dict[str, int] = {}

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
                json_errors += 1
                logger.warning("[CLI_PARSE] Non-JSON line: %.200s", raw_line)
                continue

            msg_type = data.get("type", "")
            event_types_seen[msg_type] = event_types_seen.get(msg_type, 0) + 1

            # Log errors from stream
            if msg_type == "result" and data.get("is_error"):
                errors = data.get("errors", [])
                logger.error(
                    "[CLI_RESULT_ERROR] session=%s, errors=%s",
                    session_id, errors,
                )

            # Log cost and usage from result
            if msg_type == "result":
                cost = data.get("total_cost_usd", 0)
                usage = data.get("usage", {})
                logger.info(
                    "[CLI_RESULT] session=%s, success=%s, cost=$%.4f, "
                    "input_tokens=%s, output_tokens=%s, duration_api_ms=%s",
                    session_id,
                    data.get("subtype", "?"),
                    cost,
                    usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0),
                    usage.get("output_tokens", 0),
                    data.get("duration_api_ms", "?"),
                )

            # Extract text from assistant message content blocks
            if msg_type == "content_block_delta":
                delta = data.get("delta", {})
                if delta.get("type") == "text_delta":
                    text = delta.get("text", "")
                    if text:
                        chunk_count += 1
                        full_text.append(text)
                        yield text

            # Also handle assistant result type (complete message)
            elif msg_type == "result":
                result_text = ""
                content = data.get("result", "")
                if isinstance(content, str) and content and not full_text:
                    result_text = content
                elif isinstance(content, dict):
                    blocks = content.get("content", [])
                    if isinstance(blocks, list):
                        for block in blocks:
                            if isinstance(block, dict) and block.get("type") == "text":
                                result_text += block.get("text", "")
                if result_text and not full_text:
                    yield result_text

        # Wait for process and stderr drain
        await asyncio.wait_for(proc.wait(), timeout=10)
        stderr_task.cancel()
        try:
            await stderr_task
        except asyncio.CancelledError:
            pass

        elapsed = time.time() - t0
        total_chars = sum(len(c) for c in full_text)

        if proc.returncode != 0:
            stderr_text = "\n".join(stderr_lines)[:1000]
            logger.error(
                "[CLI_FAILED] session=%s, action=%s, rc=%s, elapsed=%.1fs, "
                "stderr=%s, events=%s",
                session_id, action, proc.returncode, elapsed,
                stderr_text or "(empty)",
                dict(event_types_seen),
            )
        else:
            logger.info(
                "[CLI_DONE] session=%s, action=%s, rc=0, elapsed=%.1fs, "
                "chunks=%d, chars=%d, json_errors=%d, events=%s",
                session_id, action, elapsed,
                chunk_count, total_chars, json_errors,
                dict(event_types_seen),
            )

    except asyncio.TimeoutError:
        elapsed = time.time() - t0
        logger.error(
            "[CLI_TIMEOUT] session=%s, action=%s, timeout=%ss, elapsed=%.1fs",
            session_id, action, _TIMEOUT, elapsed,
        )
        if proc is not None:
            try:
                proc.kill()
                await proc.wait()
            except Exception as e:
                logger.warning("[CLI_KILL_FAIL] %s", e)
    except Exception:
        elapsed = time.time() - t0
        logger.exception(
            "[CLI_EXCEPTION] session=%s, action=%s, elapsed=%.1fs",
            session_id, action, elapsed,
        )
        if proc is not None:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
