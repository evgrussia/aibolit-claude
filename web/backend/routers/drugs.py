"""Drug information and interaction endpoints (async — calls OpenFDA)."""
import logging
from collections import Counter

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.integrations.openfda import search_drug, get_adverse_events
from src.tools.diagnostic import check_drug_interactions_local

logger = logging.getLogger("aibolit.drugs")
router = APIRouter(prefix="/drugs", tags=["drugs"])


class InteractionRequest(BaseModel):
    drugs: list[str]


@router.get("/{drug_name}")
async def drug_info(drug_name: str):
    try:
        raw = await search_drug(drug_name)
    except Exception:
        logger.exception("OpenFDA search_drug failed for %s", drug_name)
        raise HTTPException(503, "Сервис информации о препаратах временно недоступен")
    if "error" in raw:
        raise HTTPException(404, raw["error"])
    # Normalize field names for frontend consistency
    raw["name"] = raw.get("brand_name", drug_name)
    raw["brand_names"] = [raw["name"]] if raw.get("brand_name") else []
    raw.setdefault("drug_class", "")
    return raw


@router.get("/{drug_name}/adverse-events")
async def adverse_events(drug_name: str, limit: int = Query(10, le=50)):
    try:
        raw = await get_adverse_events(drug_name, limit)
    except Exception:
        logger.exception("OpenFDA adverse_events failed for %s", drug_name)
        raise HTTPException(503, "Сервис побочных эффектов временно недоступен")
    # Aggregate reactions across reports for the frontend
    reaction_counts: Counter[str] = Counter()
    for report in raw:
        for reaction in report.get("reactions", []):
            if reaction:
                reaction_counts[reaction] += 1
    events = [
        {"reaction": r, "count": c, "outcome": ""}
        for r, c in reaction_counts.most_common(50)
    ]
    return {"drug": drug_name, "events": events}


@router.post("/interactions")
def drug_interactions(req: InteractionRequest):
    return check_drug_interactions_local(req.drugs)
