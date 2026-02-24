"""Audit log viewing endpoints."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text

from src.utils.database import engine
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
    """Получить список аудит-логов с фильтрацией и пагинацией."""
    conditions = []
    params: dict = {}

    if category:
        conditions.append("category = :category")
        params["category"] = category
    if action:
        conditions.append("action = :action")
        params["action"] = action
    if level:
        conditions.append("level = :level")
        params["level"] = level.upper()
    if entity_type:
        conditions.append("entity_type = :entity_type")
        params["entity_type"] = entity_type
    if entity_id:
        conditions.append("entity_id = :entity_id")
        params["entity_id"] = entity_id
    if actor_id:
        conditions.append("actor_id = :actor_id")
        params["actor_id"] = actor_id
    if date_from:
        conditions.append("timestamp >= :date_from")
        params["date_from"] = date_from
    if date_to:
        conditions.append("timestamp <= :date_to")
        params["date_to"] = date_to + "T23:59:59" if "T" not in date_to else date_to
    if search:
        conditions.append("(message LIKE :search OR action LIKE :search OR entity_id LIKE :search OR request_id LIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    with engine.connect() as conn:
        # Total count
        total = conn.execute(
            text(f"SELECT COUNT(*) FROM audit_log WHERE {where_clause}"),
            params,
        ).scalar()

        # Records
        params["lim"] = limit
        params["off"] = offset
        rows = conn.execute(
            text(f"""
                SELECT id, timestamp, level, category, action, message,
                       entity_type, entity_id, actor_type, actor_id, actor_name,
                       data, request_id, ip_address, user_agent
                FROM audit_log
                WHERE {where_clause}
                ORDER BY timestamp DESC, id DESC
                LIMIT :lim OFFSET :off
            """),
            params,
        ).mappings().all()

    logs = []
    for row in rows:
        entry = dict(row)
        # Convert datetime to string for JSON
        if isinstance(entry.get("timestamp"), datetime):
            entry["timestamp"] = entry["timestamp"].isoformat()
        logs.append(entry)

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
    with engine.connect() as conn:
        category_rows = conn.execute(
            text("SELECT category, COUNT(*) as cnt FROM audit_log GROUP BY category ORDER BY cnt DESC")
        ).mappings().all()

        level_rows = conn.execute(
            text("SELECT level, COUNT(*) as cnt FROM audit_log GROUP BY level ORDER BY cnt DESC")
        ).mappings().all()

        recent_count = conn.execute(
            text("SELECT COUNT(*) FROM audit_log WHERE timestamp >= NOW() - INTERVAL '1 day'")
        ).scalar()

    return {
        "by_category": {row["category"]: row["cnt"] for row in category_rows},
        "by_level": {row["level"]: row["cnt"] for row in level_rows},
        "last_24h": recent_count,
        "total": sum(row["cnt"] for row in category_rows),
    }
