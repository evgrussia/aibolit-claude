"""Knowledge endpoints — ICD search, disease info, PubMed literature."""
import asyncio

from fastapi import APIRouter, Query

from src.integrations.who_icd import search_icd11, get_disease_info
from src.integrations.pubmed import search_pubmed, fetch_abstract

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/icd-search")
def icd_search(q: str = Query(..., min_length=1)):
    return asyncio.run(search_icd11(q))


@router.get("/disease-info")
def disease_info(name: str = Query(..., min_length=1)):
    return asyncio.run(get_disease_info(name))


@router.get("/literature")
def literature(q: str = Query(..., min_length=1), max_results: int = Query(10, le=30)):
    return asyncio.run(search_pubmed(q, max_results))


@router.get("/article/{pmid}")
def article(pmid: str):
    return {"pmid": pmid, "abstract": asyncio.run(fetch_abstract(pmid))}
