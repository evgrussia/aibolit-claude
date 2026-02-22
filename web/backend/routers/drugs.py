"""Drug information and interaction endpoints (async — calls OpenFDA)."""
import asyncio

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.integrations.openfda import search_drug, get_adverse_events
from src.tools.diagnostic import check_drug_interactions_local

router = APIRouter(prefix="/drugs", tags=["drugs"])


class InteractionRequest(BaseModel):
    drugs: list[str]


@router.get("/{drug_name}")
async def drug_info(drug_name: str):
    return await search_drug(drug_name)


@router.get("/{drug_name}/adverse-events")
async def adverse_events(drug_name: str, limit: int = Query(10, le=50)):
    return await get_adverse_events(drug_name, limit)


@router.post("/interactions")
def drug_interactions(req: InteractionRequest):
    return check_drug_interactions_local(req.drugs)
