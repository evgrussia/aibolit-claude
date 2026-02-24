"""Audit log viewing endpoints."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.utils.database import get_connection
from ..auth import get_current_user

logger = logging.getLogger("aibolit.audit.api")

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs")
def get_audit_logs(
    category: Optional[str] = Query(None, description="Фильтр по категории (general, medical, security, business, task)"),
    action: Optional[str] = Query(None, description="Фильтр по действию"),
    level: Optional[str] = Query(None, description="Фильтр по уровню (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    entity_type: Optional[str] = Query(None, description="Фильтр по типу сущности"),
    entity_id: Optional[str] = Query(None, description="Фильтр по ID сущности"),
    actor_id: Optional[str] = Query(None, description="Фильтр по ID актора"),
    date_from: Optional[str] = Query(None, description="Дата начала (ISO формат, например 2025-01-01)"),
    date_to: Optional[str] = Query(None, description="Дата окончания (ISO формат, например 2025-12-31)"),
    search: Optional[str] = Query(None, description="Поиск по message, action, entity_id"),
    limit: int = Query(50, ge=1, le=500, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    current_user: dict = Depends(get_current_user),
):
    """Получить список аудит-логов с фильтрацией и пагинацией.

    Доступ только для авторизованных пользователей.
    """
    conn = get_connection()

    # Строим WHERE clause динамически
    conditions = []
    params = []

    if category:
        conditions.append("category = ?")
        params.append(category)
    if action:
        conditions.append("action = ?")
        params.append(action)
    if level:
        conditions.append("level = ?")
        params.append(level.upper())
    if entity_type:
        conditions.append("entity_type = ?")
        params.append(entity_type)
    if entity_id:
        conditions.append("entity_id = ?")
        params.append(entity_id)
    if actor_id:
        conditions.append("actor_id = ?")
        params.append(actor_id)
    if date_from:
        conditions.append("timestamp >= ?")
        params.append(date_from)
    if date_to:
        # Добавляем время конца дня, чтобы включить весь день
        conditions.append("timestamp <= ?")
        params.append(date_to + "T23:59:59" if "T" not in date_to else date_to)
    if search:
        conditions.append("(message LIKE ? OR action LIKE ? OR entity_id LIKE ? OR request_id LIKE ?)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Получаем общее количество
    count_sql = f"SELECT COUNT(*) FROM audit_log WHERE {where_clause}"
    total = conn.execute(count_sql, params).fetchone()[0]

    # Получаем записи
    query_sql = f"""
        SELECT id, timestamp, level, category, action, message,
               entity_type, entity_id, actor_type, actor_id, actor_name,
               data, request_id, ip_address, user_agent
        FROM audit_log
        WHERE {where_clause}
        ORDER BY timestamp DESC, id DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    rows = conn.execute(query_sql, params).fetchall()

    logs = []
    for row in rows:
        log_entry = {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "level": row["level"],
            "category": row["category"],
            "action": row["action"],
            "message": row["message"],
            "entity_type": row["entity_type"],
            "entity_id": row["entity_id"],
            "actor_type": row["actor_type"],
            "actor_id": row["actor_id"],
            "actor_name": row["actor_name"],
            "data": row["data"],
            "request_id": row["request_id"],
            "ip_address": row["ip_address"],
            "user_agent": row["user_agent"],
        }
        logs.append(log_entry)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": logs,
    }


@router.get("/logs/stats")
def get_audit_stats(
    current_user: dict = Depends(get_current_user),
):
    """Получить статистику аудит-логов по категориям и уровням."""
    conn = get_connection()

    # По категориям
    category_rows = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM audit_log GROUP BY category ORDER BY cnt DESC"
    ).fetchall()

    # По уровням
    level_rows = conn.execute(
        "SELECT level, COUNT(*) as cnt FROM audit_log GROUP BY level ORDER BY cnt DESC"
    ).fetchall()

    # Последние 24 часа
    recent_count = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE timestamp >= datetime('now', '-1 day')"
    ).fetchone()[0]

    return {
        "by_category": {row["category"]: row["cnt"] for row in category_rows},
        "by_level": {row["level"]: row["cnt"] for row in level_rows},
        "last_24h": recent_count,
        "total": sum(row["cnt"] for row in category_rows),
    }
