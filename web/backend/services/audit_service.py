"""AuditLogService — сервис аудит-логирования для Aibolit AI.

Записывает события в таблицу audit_log (SQLite) и в Python logger.
Маскирует чувствительные данные. Не бросает исключения наружу.
"""
import asyncio
import functools
import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from src.utils.database import get_connection

logger = logging.getLogger("aibolit.audit")

# ── Context variable for request_id tracing ──────────────────
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
request_ip_var: ContextVar[str | None] = ContextVar("request_ip", default=None)
request_ua_var: ContextVar[str | None] = ContextVar("request_ua", default=None)


class AuditLogService:
    """Сервис аудит-логирования для Aibolit AI."""

    MASKED_FIELDS: set[str] = {
        "password", "token", "secret", "api_key", "private_key",
        "card_number", "cvv", "ssn", "access_token", "refresh_token",
        "yookassa_secret", "bot_token",
        # Медицинские защищённые поля
        "diagnosis_code", "diagnosis_text", "lab_results", "imaging_findings",
        "medication_list", "allergy_info", "genetic_data", "psychiatric_notes",
        "reproductive_data", "hiv_status", "substance_abuse",
    }

    MASK_VALUE = "***MASKED***"

    # ── Маскирование данных ──────────────────────────────────

    @classmethod
    def _mask_data(cls, data: dict | list | Any) -> dict | list | Any:
        """Рекурсивно маскирует чувствительные поля в словаре/списке."""
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                if key in cls.MASKED_FIELDS:
                    masked[key] = cls.MASK_VALUE
                elif isinstance(value, (dict, list)):
                    masked[key] = cls._mask_data(value)
                else:
                    masked[key] = value
            return masked
        elif isinstance(data, list):
            return [cls._mask_data(item) for item in data]
        return data

    # ── Извлечение информации об акторе ──────────────────────

    @classmethod
    def _resolve_actor(cls, actor: Any) -> tuple[str, str | None, str | None]:
        """Извлекает actor_type, actor_id, actor_name из разных форматов.

        actor может быть:
        - None → ('system', None, None)
        - str → ('system', None, actor)
        - dict с ключами user_id/patient_id/username (из get_current_user)
        """
        if actor is None:
            return "system", None, None
        if isinstance(actor, str):
            return "system" if actor == "system" else "user", None, actor
        if isinstance(actor, dict):
            actor_type = "user"
            actor_id = str(actor.get("user_id") or actor.get("patient_id") or "")
            actor_name = actor.get("username") or actor.get("name") or ""
            return actor_type, actor_id or None, actor_name or None
        return "system", None, str(actor)

    # ── Основной метод записи ────────────────────────────────

    @classmethod
    def _write_log(
        cls,
        level: str,
        category: str,
        action: str,
        message: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor_type: str = "system",
        actor_id: str | None = None,
        actor_name: str | None = None,
        data: dict | None = None,
        request: Any = None,
    ) -> None:
        """Записывает лог-событие в SQLite и в Python logger.

        Не бросает исключений наружу — при ошибке записи только логирует в stderr.
        """
        try:
            # Маскируем данные
            masked_data = cls._mask_data(data) if data else None
            data_json = json.dumps(masked_data, ensure_ascii=False, default=str) if masked_data else None

            # Получаем request_id и метаданные запроса из contextvars
            req_id = request_id_var.get(None)
            ip_address = request_ip_var.get(None)
            user_agent = request_ua_var.get(None)

            # Если передан FastAPI Request, извлекаем данные из него
            if request is not None:
                if hasattr(request, "state") and hasattr(request.state, "request_id"):
                    req_id = req_id or request.state.request_id
                if hasattr(request, "client") and request.client:
                    ip_address = ip_address or request.client.host
                if hasattr(request, "headers"):
                    user_agent = user_agent or request.headers.get("user-agent")

            # Записываем в SQLite
            conn = get_connection()
            conn.execute(
                """
                INSERT INTO audit_log
                    (level, category, action, message, entity_type, entity_id,
                     actor_type, actor_id, actor_name, data, request_id, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    level, category, action, message, entity_type, str(entity_id) if entity_id else None,
                    actor_type, actor_id, actor_name, data_json, req_id, ip_address, user_agent,
                ),
            )
            conn.commit()

            # Записываем в Python logger
            log_level = getattr(logging, level.upper(), logging.INFO)
            log_msg = f"[{category}] {action}"
            if message:
                log_msg += f": {message}"
            if entity_type:
                log_msg += f" | {entity_type}"
                if entity_id:
                    log_msg += f":{entity_id}"
            if actor_name:
                log_msg += f" | actor={actor_name}"
            logger.log(log_level, log_msg)

        except Exception:
            # Аудит-лог не должен ломать основной flow
            print(f"[Aibolit] AUDIT LOG ERROR: не удалось записать аудит-лог для {action}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)

    # ── CRUD-логирование ─────────────────────────────────────

    @classmethod
    def log_db_create(
        cls,
        entity_type: str,
        entity_id: str | int,
        data: dict | None = None,
        actor: Any = None,
        request: Any = None,
    ) -> None:
        """Логирует создание записи в БД."""
        a_type, a_id, a_name = cls._resolve_actor(actor)
        cls._write_log(
            level="INFO",
            category="general",
            action="db_create",
            message=f"Создана запись {entity_type}:{entity_id}",
            entity_type=entity_type,
            entity_id=str(entity_id),
            actor_type=a_type,
            actor_id=a_id,
            actor_name=a_name,
            data=data,
            request=request,
        )

    @classmethod
    def log_db_update(
        cls,
        entity_type: str,
        entity_id: str | int,
        old_values: dict | None = None,
        new_values: dict | None = None,
        actor: Any = None,
        request: Any = None,
    ) -> None:
        """Логирует обновление записи в БД."""
        a_type, a_id, a_name = cls._resolve_actor(actor)
        change_data = {}
        if old_values:
            change_data["old"] = old_values
        if new_values:
            change_data["new"] = new_values
        cls._write_log(
            level="INFO",
            category="general",
            action="db_update",
            message=f"Обновлена запись {entity_type}:{entity_id}",
            entity_type=entity_type,
            entity_id=str(entity_id),
            actor_type=a_type,
            actor_id=a_id,
            actor_name=a_name,
            data=change_data or None,
            request=request,
        )

    @classmethod
    def log_db_delete(
        cls,
        entity_type: str,
        entity_id: str | int,
        actor: Any = None,
        request: Any = None,
    ) -> None:
        """Логирует удаление записи из БД."""
        a_type, a_id, a_name = cls._resolve_actor(actor)
        cls._write_log(
            level="WARNING",
            category="general",
            action="db_delete",
            message=f"Удалена запись {entity_type}:{entity_id}",
            entity_type=entity_type,
            entity_id=str(entity_id),
            actor_type=a_type,
            actor_id=a_id,
            actor_name=a_name,
            request=request,
        )

    # ── Событийное логирование ───────────────────────────────

    @classmethod
    def log_event(
        cls,
        action: str,
        data: dict | None = None,
        actor: Any = None,
        request: Any = None,
    ) -> None:
        """Логирует произвольное событие."""
        a_type, a_id, a_name = cls._resolve_actor(actor)
        cls._write_log(
            level="INFO",
            category="general",
            action=action,
            actor_type=a_type,
            actor_id=a_id,
            actor_name=a_name,
            data=data,
            request=request,
        )

    # ── Бизнес-логирование ───────────────────────────────────

    @classmethod
    def log_business(
        cls,
        action: str,
        message: str | None = None,
        data: dict | None = None,
        actor: Any = None,
        request: Any = None,
    ) -> None:
        """Логирует бизнес-событие."""
        a_type, a_id, a_name = cls._resolve_actor(actor)
        cls._write_log(
            level="INFO",
            category="business",
            action=action,
            message=message,
            actor_type=a_type,
            actor_id=a_id,
            actor_name=a_name,
            data=data,
            request=request,
        )

    # ── Медицинское логирование ──────────────────────────────

    @classmethod
    def log_medical(
        cls,
        action: str,
        data: dict | None = None,
        actor: Any = None,
        request: Any = None,
        level: str = "INFO",
    ) -> None:
        """Логирует медицинское событие.

        Медицинские логи имеют увеличенный retention (5 лет).
        Уровень WARNING для red flags, CRITICAL для неработающей эскалации.
        """
        a_type, a_id, a_name = cls._resolve_actor(actor)
        cls._write_log(
            level=level,
            category="medical",
            action=action,
            actor_type=a_type,
            actor_id=a_id,
            actor_name=a_name,
            data=data,
            request=request,
        )

    # ── Логирование задач (scheduled/cron) ───────────────────

    @classmethod
    def log_task_start(cls, task_name: str, data: dict | None = None) -> None:
        """Логирует начало выполнения задачи."""
        cls._write_log(
            level="INFO",
            category="task",
            action=f"task_start:{task_name}",
            message=f"Задача '{task_name}' запущена",
            data=data,
        )

    @classmethod
    def log_task_end(
        cls,
        task_name: str,
        status: str = "success",
        data: dict | None = None,
    ) -> None:
        """Логирует завершение задачи."""
        level = "INFO" if status == "success" else "ERROR"
        cls._write_log(
            level=level,
            category="task",
            action=f"task_end:{task_name}",
            message=f"Задача '{task_name}' завершена со статусом: {status}",
            data=data,
        )

    # ── Логирование безопасности ─────────────────────────────

    @classmethod
    def log_security(
        cls,
        action: str,
        message: str | None = None,
        data: dict | None = None,
        actor: Any = None,
        request: Any = None,
    ) -> None:
        """Логирует событие безопасности (авторизация, доступ, подозрительная активность)."""
        a_type, a_id, a_name = cls._resolve_actor(actor)
        cls._write_log(
            level="WARNING",
            category="security",
            action=action,
            message=message,
            actor_type=a_type,
            actor_id=a_id,
            actor_name=a_name,
            data=data,
            request=request,
        )


# ── Декоратор для задач ──────────────────────────────────────


def audit_task(task_name: str):
    """Декоратор для автоматического логирования начала/конца задач.

    Поддерживает как синхронные, так и асинхронные функции.

    Использование::

        @audit_task('cleanup_expired_tokens')
        def cleanup():
            ...

        @audit_task('send_reminders')
        async def send_reminders():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            AuditLogService.log_task_start(task_name)
            try:
                result = func(*args, **kwargs)
                AuditLogService.log_task_end(task_name, "success")
                return result
            except Exception as e:
                AuditLogService.log_task_end(task_name, "error", {"error": str(e)})
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            AuditLogService.log_task_start(task_name)
            try:
                result = await func(*args, **kwargs)
                AuditLogService.log_task_end(task_name, "success")
                return result
            except Exception as e:
                AuditLogService.log_task_end(task_name, "error", {"error": str(e)})
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper

    return decorator
