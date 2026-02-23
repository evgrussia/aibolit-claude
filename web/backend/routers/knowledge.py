"""Knowledge endpoints — ICD search, disease info, PubMed literature."""
import logging

from fastapi import APIRouter, HTTPException, Query

from src.integrations.who_icd import search_icd11, get_disease_info
from src.integrations.pubmed import search_pubmed, fetch_abstract

logger = logging.getLogger("aibolit.knowledge")
router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/icd-search")
async def icd_search(q: str = Query(..., min_length=1)):
    try:
        return await search_icd11(q)
    except Exception:
        logger.exception("ICD search failed for q=%s", q)
        raise HTTPException(503, "Сервис классификации болезней временно недоступен")


@router.get("/disease-info")
async def disease_info(name: str = Query(..., min_length=1)):
    try:
        return await get_disease_info(name)
    except Exception:
        logger.exception("Disease info failed for name=%s", name)
        raise HTTPException(503, "Сервис информации о заболеваниях временно недоступен")


@router.get("/literature")
async def literature(q: str = Query(..., min_length=1), max_results: int = Query(10, le=30)):
    try:
        return await search_pubmed(q, max_results)
    except Exception:
        logger.exception("PubMed search failed for q=%s", q)
        raise HTTPException(503, "Сервис медицинской литературы временно недоступен")


@router.get("/article/{pmid}")
async def article(pmid: str):
    try:
        return {"pmid": pmid, "abstract": await fetch_abstract(pmid)}
    except Exception:
        logger.exception("Abstract fetch failed for pmid=%s", pmid)
        raise HTTPException(503, "Ошибка получения статьи")
