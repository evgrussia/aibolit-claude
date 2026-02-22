"""Service for calling Claude Code CLI to generate AI consultations."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil

logger = logging.getLogger("aibolit.claude_service")

# Path to MCP config inside Docker container
_MCP_CONFIG = os.environ.get(
    "CLAUDE_MCP_CONFIG",
    "/app/config/claude_code_docker.json",
)

# Max time (seconds) to wait for Claude response
_TIMEOUT = int(os.environ.get("CLAUDE_TIMEOUT", "120"))

# Max agentic turns (limits MCP tool-call rounds and cost)
_MAX_TURNS = int(os.environ.get("CLAUDE_MAX_TURNS", "3"))


def is_available() -> bool:
    """Check if claude CLI is installed."""
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
            "--max-turns", str(_MAX_TURNS),
            "--mcp-config", _MCP_CONFIG,
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "CLAUDE_CODE_DISABLE_NONESSENTIAL": "1"},
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=_TIMEOUT,
        )

        if proc.returncode != 0:
            logger.error("Claude CLI failed (rc=%s): %s", proc.returncode, stderr.decode()[:500])
            return None

        text = stdout.decode().strip()
        if not text:
            logger.warning("Claude CLI returned empty response")
            return None

        return text

    except asyncio.TimeoutError:
        logger.error("Claude CLI timed out after %ss", _TIMEOUT)
        if proc:
            proc.kill()
        return None
    except Exception:
        logger.exception("Claude CLI unexpected error")
        return None


def _build_prompt(specialty_name: str, complaints: str, patient_context: str) -> str:
    """Build the system prompt for Claude."""
    parts = [
        f"Ты — AI-{specialty_name} в виртуальной клинике Aibolit.",
        f"Пациент обратился с жалобами: {complaints}",
    ]

    if patient_context and patient_context != "Карта пациента не загружена":
        parts.append(f"\nДанные пациента:\n{patient_context}")

    parts.append("""
Проведи полноценную медицинскую консультацию:

1. Проанализируй жалобы с точки зрения своей специализации
2. Если есть ID пациента — загрузи его карту (get_patient) и учти анамнез, диагнозы, лекарства
3. Предложи дифференциальный диагноз с кодами МКБ-10
4. Рекомендуй конкретные обследования и анализы
5. Дай рекомендации по лечению (препараты, дозировки, немедикаментозные меры)
6. Укажи, когда необходимо срочно обратиться к врачу

Отвечай на русском языке. Будь конкретен, структурируй ответ.
⚠️ В конце обязательно напомни: все рекомендации носят информационный характер и не заменяют очную консультацию врача.""")

    return "\n".join(parts)
