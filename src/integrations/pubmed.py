"""PubMed/NCBI integration for evidence-based medicine research."""
import logging
import httpx
from typing import Any

logger = logging.getLogger("aibolit.integrations.pubmed")

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_SEARCH = f"{PUBMED_BASE}/esearch.fcgi"
PUBMED_FETCH = f"{PUBMED_BASE}/efetch.fcgi"
PUBMED_SUMMARY = f"{PUBMED_BASE}/esummary.fcgi"


async def search_pubmed(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search PubMed for medical literature.

    Uses NCBI E-utilities (free, no API key required for <3 req/sec).
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Step 1: Search for article IDs
            search_resp = await client.get(PUBMED_SEARCH, params={
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance",
            })
            if search_resp.status_code != 200:
                return []

            search_data = search_resp.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])

            if not id_list:
                return []

            # Step 2: Fetch summaries
            summary_resp = await client.get(PUBMED_SUMMARY, params={
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json",
            })
            if summary_resp.status_code != 200:
                return []

            summary_data = summary_resp.json()

            results = []
            for uid in id_list:
                article = summary_data.get("result", {}).get(uid, {})
                if article:
                    results.append({
                        "pmid": uid,
                        "title": article.get("title", ""),
                        "authors": [a.get("name", "") for a in article.get("authors", [])[:5]],
                        "journal": article.get("source", ""),
                        "pub_date": article.get("pubdate", ""),
                        "doi": next((eid["value"] for eid in article.get("articleids", [])
                                    if eid.get("idtype") == "doi"), ""),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                    })

            return results
    except Exception:
        logger.warning("PubMed search failed for query=%s", query, exc_info=True)
        return []


async def fetch_abstract(pmid: str) -> str:
    """Fetch article abstract from PubMed."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(PUBMED_FETCH, params={
                "db": "pubmed",
                "id": pmid,
                "rettype": "abstract",
                "retmode": "text",
            })
            if resp.status_code != 200:
                return f"Ошибка получения абстракта для PMID {pmid}"
            return resp.text
    except Exception:
        logger.warning("PubMed abstract fetch failed for PMID=%s", pmid, exc_info=True)
        return f"Ошибка сети при получении абстракта для PMID {pmid}"


async def search_clinical_trials(condition: str, max_results: int = 5) -> list[dict]:
    """Search ClinicalTrials.gov for active trials."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://clinicaltrials.gov/api/v2/studies",
                params={
                    "query.cond": condition,
                    "pageSize": max_results,
                    "sort": "LastUpdatePostDate:desc",
                    "fields": "NCTId,BriefTitle,OverallStatus,Condition,InterventionName,Phase",
                },
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            trials = []
            for study in data.get("studies", []):
                proto = study.get("protocolSection", {})
                ident = proto.get("identificationModule", {})
                status = proto.get("statusModule", {})
                conditions_mod = proto.get("conditionsModule", {})
                arms_mod = proto.get("armsInterventionsModule", {})
                design_mod = proto.get("designModule", {})
                nct_id = ident.get("nctId", "")
                interventions = [
                    i.get("name", "") for i in arms_mod.get("interventions", [])
                ]
                trials.append({
                    "nct_id": nct_id,
                    "title": ident.get("briefTitle", ""),
                    "status": status.get("overallStatus", ""),
                    "conditions": conditions_mod.get("conditions", []),
                    "interventions": interventions,
                    "phases": design_mod.get("phases", []),
                    "url": f"https://clinicaltrials.gov/study/{nct_id}",
                })
            return trials
    except Exception:
        logger.warning("ClinicalTrials.gov search failed for condition=%s", condition, exc_info=True)
        return []
