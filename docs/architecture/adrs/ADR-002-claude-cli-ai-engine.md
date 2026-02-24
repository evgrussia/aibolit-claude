---
title: "ADR-002: Использование Claude CLI с session-id вместо прямого API"
created_by: "Architect Agent"
created_at: "2025-02-24"
version: "1.0"
---

# ADR-002: Использование Claude CLI с session-id вместо прямого API

## Статус

Accepted

## Контекст

Aibolit AI требует AI-движок для:
1. **Мультитерновых консультаций** — пациент ведёт диалог с AI-врачом, AI помнит контекст разговора.
2. **Потокового вывода (streaming)** — ответ AI показывается посимвольно в реальном времени.
3. **Анализа файлов** — пациент может прикрепить фото, PDF с анализами.
4. **35 специализаций** — каждый AI-врач имеет уникальный system prompt с компетенциями и МКБ-10 кодами.

Claude CLI (Anthropic's official CLI для Claude) предоставляет:
- `--session-id` / `--resume` для сохранения контекста между сообщениями
- `--output-format stream-json` для потокового JSON-вывода
- Встроенную обработку файлов (изображения, PDF)
- Автоматическое управление контекстным окном
- Аутентификацию через `CLAUDE_CODE_OAUTH_TOKEN`

## Решение

AI-движок реализован через **Claude CLI как subprocess**, вызываемый через `asyncio.create_subprocess_exec()`.

### Архитектура

```
FastAPI Backend
    |
    |-- chat_service.py
    |       |
    |       |-- start_session(session_id, system_prompt, message)
    |       |       claude --print --verbose
    |       |              --model sonnet
    |       |              --session-id <uuid>
    |       |              --max-turns 3
    |       |              --output-format stream-json
    |       |              "<prompt>"
    |       |
    |       |-- send_message(session_id, message)
    |       |       claude --print --verbose
    |       |              --resume <session_id>
    |       |              --max-turns 3
    |       |              --output-format stream-json
    |       |              "<message>"
    |       |
    |       |-- _run_claude_stream(cmd) → AsyncIterator[str]
    |               |-- asyncio.create_subprocess_exec(*cmd)
    |               |-- readline() + json.loads()
    |               |-- yield text from content_block_delta
    |               |-- yield text from result
```

### Параметры CLI

| Параметр | Значение | Назначение |
|----------|----------|------------|
| `--print` | — | Режим вывода (не интерактивный) |
| `--verbose` | — | Расширенный JSON-вывод |
| `--model` | sonnet (env: CLAUDE_MODEL) | Модель Claude |
| `--session-id` | UUID | Создание новой сессии |
| `--resume` | session_id | Продолжение сессии |
| `--max-turns` | 3 | Лимит рекурсии инструментов |
| `--output-format` | stream-json | Потоковый JSON (NDJSON) |
| `--timeout` | 120s (env: CLAUDE_TIMEOUT) | Таймаут ожидания |

### Формат stream-json

```jsonl
{"type":"content_block_delta","delta":{"type":"text_delta","text":"Здравствуйте"}}
{"type":"content_block_delta","delta":{"type":"text_delta","text":"! Рас"}}
{"type":"content_block_delta","delta":{"type":"text_delta","text":"скажите"}}
{"type":"result","result":"полный текст ответа"}
```

### Управление окружением

```python
def _clean_env() -> dict[str, str]:
    """Убираем CLAUDECODE* переменные для nested CLI invocation."""
    skip = {"CLAUDECODE", "CLAUDE_CODE_SSE_PORT", "CLAUDE_CODE_ENTRYPOINT"}
    return {k: v for k, v in os.environ.items() if k not in skip}
```

Это необходимо, потому что backend сам может запускаться внутри Claude Code, и переменные окружения Claude Code конфликтуют с nested вызовом CLI.

## Альтернативы

### 1. Прямой Anthropic API (anthropic Python SDK)

**Плюсы:**
- Полный контроль над параметрами
- Нативный Python streaming через `client.messages.stream()`
- Нет зависимости от установленного CLI
- Лучшая обработка ошибок
- API keys вместо OAuth token

**Минусы:**
- Нужно самостоятельно управлять conversation history
- Нужно считать и контролировать контекстное окно
- Нужно реализовать обработку файлов (base64 encoding)
- Платный API (за использование)
- Больше кода для session management

**Отклонено для MVP:** CLI даёт session management бесплатно.

### 2. LangChain / LangGraph

**Плюсы:**
- Абстракция над LLM-провайдерами
- Встроенные chains, memory, tools
- Поддержка RAG из коробки
- Агентные фреймворки

**Минусы:**
- Значительный overhead и зависимости
- Сложная конфигурация
- Версионирование и breaking changes
- Избыточен для текущего use case (нет RAG, нет tool calling)

**Отклонено:** Избыточная абстракция для прямого диалога с Claude.

### 3. Ollama / локальные модели

**Плюсы:**
- Бесплатно (нет API costs)
- Полный контроль данных
- Работа offline

**Минусы:**
- Качество медицинских ответов значительно ниже Claude
- Требует GPU (дорогая инфраструктура)
- Нет гарантий медицинской безопасности
- Нет session management

**Отклонено:** Качество медицинских ответов критично, Claude — лучший вариант.

## Последствия

### Положительные

1. **Session management бесплатно** — CLI автоматически сохраняет и восстанавливает контекст через `--session-id` / `--resume`.
2. **Обработка файлов** — CLI нативно обрабатывает изображения и PDF, переданные в prompt.
3. **Минимум кода** — вся логика AI-диалога в ~150 строках (`chat_service.py`).
4. **Streaming** — `stream-json` формат позволяет показывать ответ в реальном времени.
5. **Быстрая смена модели** — через env var `CLAUDE_MODEL`.

### Отрицательные

1. **Зависимость от CLI** — требуется установка `claude` CLI на сервере, невозможно через pip.
2. **Один процесс на запрос** — каждая консультация порождает subprocess, ограничивая concurrency.
3. **Непрозрачность** — CLI — чёрный ящик, сложно контролировать exact tokens, costs, prompts.
4. **OAuth token** — CLI использует OAuth, не API key (менее гибко).
5. **Хрупкий парсинг** — формат `stream-json` может меняться между версиями CLI.
6. **Нет контроля context window** — CLI сам решает, что включать в контекст при `--resume`.

### План миграции на прямой API

При масштабировании (>50 concurrent users) рекомендуется миграция:

```yaml
Этапы:
  1. Установить anthropic Python SDK
  2. Реализовать ConversationManager с хранением истории сообщений
  3. Реализовать streaming через client.messages.stream()
  4. Реализовать обработку файлов (base64 encoding)
  5. Мигрировать start_session() и send_message()
  6. Удалить зависимость от CLI
  7. Обновить аутентификацию (ANTHROPIC_API_KEY вместо OAuth)

Трудозатраты: 2-3 дня
```

---

*Документ создан: Architect Agent | Дата: 2025-02-24*
