"""Service for parsing lab results from uploaded files (CSV, PDF, images).

CSV/TXT — parsed directly with Python.
PDF/images — parsed via Claude CLI (AI extraction).
"""
from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger("aibolit.lab_parser")

# Column name mappings (Russian and English)
_COL_TEST = {"анализ", "тест", "показатель", "название", "test", "test_name", "name", "parameter"}
_COL_VALUE = {"значение", "результат", "value", "result"}
_COL_UNIT = {"единицы", "ед", "ед.", "единица", "unit", "units"}
_COL_REF = {"норма", "референс", "reference", "reference_range", "ref", "ref_range", "normal"}
_COL_DATE = {"дата", "date"}

_TIMEOUT = int(os.environ.get("CLAUDE_TIMEOUT", "120"))


def _clean_env() -> dict[str, str]:
    """Build env without CLAUDECODE* vars to allow nested CLI invocation."""
    skip = {"CLAUDECODE", "CLAUDE_CODE_SSE_PORT", "CLAUDE_CODE_ENTRYPOINT"}
    return {k: v for k, v in os.environ.items() if k not in skip}


def _detect_column(header: str) -> str | None:
    """Map a CSV header to a canonical field name."""
    h = header.strip().lower()
    if h in _COL_TEST:
        return "test_name"
    if h in _COL_VALUE:
        return "value"
    if h in _COL_UNIT:
        return "unit"
    if h in _COL_REF:
        return "reference_range"
    if h in _COL_DATE:
        return "date"
    return None


def parse_csv(content: bytes, filename: str) -> dict[str, Any]:
    """Parse CSV/TSV file content and return structured lab results."""
    warnings: list[str] = []

    text = content.decode("utf-8-sig", errors="replace")

    # Detect delimiter
    delimiter = "\t" if "\t" in text.split("\n", 1)[0] else ","
    # Try semicolon as well (common in Russian Excel exports)
    first_line = text.split("\n", 1)[0]
    if first_line.count(";") > first_line.count(delimiter):
        delimiter = ";"

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)

    if len(rows) < 2:
        return {"results": [], "warnings": ["Файл пуст или содержит только заголовок"], "parse_method": "csv"}

    # Map headers
    headers = rows[0]
    col_map: dict[int, str] = {}
    for i, h in enumerate(headers):
        field = _detect_column(h)
        if field:
            col_map[i] = field

    if "test_name" not in col_map.values():
        # Fallback: try positional mapping (test, value, unit, ref)
        if len(headers) >= 2:
            col_map = {0: "test_name", 1: "value"}
            if len(headers) >= 3:
                col_map[2] = "unit"
            if len(headers) >= 4:
                col_map[3] = "reference_range"
            if len(headers) >= 5:
                col_map[4] = "date"
            warnings.append("Заголовки не распознаны — использован порядок колонок")
        else:
            return {"results": [], "warnings": ["Не удалось распознать структуру CSV"], "parse_method": "csv"}

    results: list[dict[str, Any]] = []
    for row_idx, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        entry: dict[str, Any] = {"test_name": "", "value": "", "unit": "", "reference_range": "", "date": ""}
        for col_idx, field in col_map.items():
            if col_idx < len(row):
                entry[field] = row[col_idx].strip()

        if not entry["test_name"]:
            warnings.append(f"Строка {row_idx}: пропущена (нет названия анализа)")
            continue

        # Try to parse value as number
        raw_val = entry["value"]
        try:
            entry["value"] = float(raw_val.replace(",", "."))
        except (ValueError, AttributeError):
            pass  # keep as string

        results.append(entry)

    if not results:
        warnings.append("Не найдено ни одного результата в файле")

    return {"results": results, "warnings": warnings, "parse_method": "csv"}


_AI_PROMPT = """Извлеки ВСЕ результаты лабораторных анализов из этого файла.

Верни ТОЛЬКО валидный JSON массив (без markdown, без пояснений) в формате:
[
  {
    "test_name": "Название анализа",
    "value": "числовое или текстовое значение",
    "unit": "единицы измерения",
    "reference_range": "диапазон нормы",
    "date": "дата анализа если указана, формат YYYY-MM-DD"
  }
]

Правила:
- Каждый анализ — отдельный объект
- value — число (без единиц) или текст если нечисловое
- unit — единицы измерения (г/л, ммоль/л, и т.д.)
- reference_range — диапазон нормы как строка (например "130-170")
- date — дата если указана, иначе пустая строка
- Если поле неизвестно — пустая строка
- НЕ добавляй пояснения, ТОЛЬКО JSON массив"""


async def parse_with_ai(content: bytes, filename: str, content_type: str) -> dict[str, Any]:
    """Parse PDF/image file using Claude CLI for AI extraction."""
    warnings: list[str] = []

    claude_bin = shutil.which("claude")
    if not claude_bin:
        return {
            "results": [],
            "warnings": ["Claude CLI не установлен — AI-парсинг недоступен"],
            "parse_method": "ai",
        }

    # Save file to temp directory
    suffix = Path(filename).suffix or ".bin"
    tmp_dir = tempfile.mkdtemp(prefix="aibolit_lab_")
    tmp_path = Path(tmp_dir) / f"upload{suffix}"

    try:
        tmp_path.write_bytes(content)

        prompt = (
            f"{_AI_PROMPT}\n\n"
            f"Файл с результатами анализов сохранён по пути: {tmp_path}\n"
            f"Оригинальное имя файла: {filename}\n"
            f"Тип файла: {content_type}\n"
            f"Прочитай этот файл и извлеки результаты анализов."
        )

        cmd = [
            claude_bin,
            "-p", prompt,
            "--output-format", "text",
            "--model", os.environ.get("CLAUDE_MODEL", "sonnet"),
            "--max-turns", "3",
            "--allowedTools", "Read",
        ]

        env = _clean_env()

        def _run_sync() -> subprocess.CompletedProcess[bytes]:
            return subprocess.run(
                cmd, capture_output=True, env=env, timeout=_TIMEOUT,
            )

        try:
            completed = await asyncio.to_thread(_run_sync)
        except subprocess.TimeoutExpired:
            return {
                "results": [],
                "warnings": ["Превышено время ожидания AI-парсинга"],
                "parse_method": "ai",
            }

        if completed.returncode != 0:
            err_msg = completed.stderr.decode(errors="replace").strip()[:200]
            logger.error("Claude CLI error: %s", err_msg)
            return {
                "results": [],
                "warnings": [f"Ошибка AI-парсинга: {err_msg}"],
                "parse_method": "ai",
            }

        raw = completed.stdout.decode(errors="replace").strip()

        # Extract JSON array from response (may have surrounding text)
        json_match = re.search(r'\[[\s\S]*\]', raw)
        if not json_match:
            logger.warning("No JSON array in Claude response: %s", raw[:300])
            return {
                "results": [],
                "warnings": ["AI не вернул структурированные данные"],
                "parse_method": "ai",
            }

        parsed = json.loads(json_match.group())
        if not isinstance(parsed, list):
            return {
                "results": [],
                "warnings": ["AI вернул некорректный формат данных"],
                "parse_method": "ai",
            }

        results: list[dict[str, Any]] = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            entry = {
                "test_name": str(item.get("test_name", "")).strip(),
                "value": item.get("value", ""),
                "unit": str(item.get("unit", "")).strip(),
                "reference_range": str(item.get("reference_range", "")).strip(),
                "date": str(item.get("date", "")).strip(),
            }
            if not entry["test_name"]:
                continue
            # Normalize numeric values
            if isinstance(entry["value"], str):
                try:
                    entry["value"] = float(entry["value"].replace(",", "."))
                except (ValueError, AttributeError):
                    pass
            results.append(entry)

        if not results:
            warnings.append("AI не смог извлечь результаты анализов из файла")

        return {"results": results, "warnings": warnings, "parse_method": "ai"}

    except json.JSONDecodeError:
        return {
            "results": [],
            "warnings": ["Ошибка разбора ответа AI — некорректный JSON"],
            "parse_method": "ai",
        }
    except (FileNotFoundError, OSError) as e:
        logger.error("Failed to launch Claude CLI: %s", e)
        return {
            "results": [],
            "warnings": [f"Не удалось запустить Claude CLI: {e}"],
            "parse_method": "ai",
        }
    finally:
        # Clean up temp files
        shutil.rmtree(tmp_dir, ignore_errors=True)
