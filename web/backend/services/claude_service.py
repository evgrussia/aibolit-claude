"""Service for calling Claude Code CLI to generate AI consultations.

Calls `claude --print` without MCP — all patient/specialization context
is pre-fetched by the backend and passed directly in the prompt.
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil

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
) -> str | None:
    """Call Claude Code CLI and return AI-generated consultation text.

    Returns None if Claude is unavailable or fails (caller should fallback).
    """
    if not is_available():
        logger.warning("Claude CLI not found — falling back to template")
        return None

    prompt = _build_prompt(specialty_name, complaints, patient_context)

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

        if proc.returncode != 0:
            err = stderr.decode()[:500]
            logger.error("Claude CLI failed (rc=%s): %s", proc.returncode, err)
            return None

        text = stdout.decode().strip()
        if not text:
            logger.warning("Claude CLI returned empty response")
            return None

        return text

    except asyncio.TimeoutError:
        logger.error("Claude CLI timed out after %ss", _TIMEOUT)
        try:
            proc.kill()
        except Exception:
            pass
        return None
    except Exception:
        logger.exception("Claude CLI unexpected error")
        return None


def _build_prompt(specialty_name: str, complaints: str, patient_context: str) -> str:
    """Build a rich prompt with all context pre-fetched."""
    parts = [
        f"Ты — AI-{specialty_name} в виртуальной клинике Aibolit.",
        f"\nПациент обратился с жалобами: {complaints}",
    ]

    if patient_context and patient_context != "Карта пациента не загружена":
        parts.append(f"\nДанные из медицинской карты пациента:\n{patient_context}")

    parts.append("""
Проведи полноценную медицинскую консультацию. Структурируй ответ:

1. **Оценка жалоб** — проанализируй симптомы с точки зрения своей специализации
2. **Дифференциальный диагноз** — предложи возможные диагнозы с кодами МКБ-10
3. **Рекомендуемые обследования** — конкретные анализы и исследования
4. **Рекомендации по лечению** — препараты, дозировки, немедикаментозные меры
5. **Красные флаги** — когда необходимо срочно обратиться к врачу

Отвечай на русском языке. Будь конкретен и профессионален.
В конце напомни: все рекомендации носят информационный характер и не заменяют очную консультацию врача.""")

    return "\n".join(parts)
