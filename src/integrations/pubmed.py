"""PubMed/NCBI integration for evidence-based medicine research."""
import httpx
from typing import Any

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_SEARCH = f"{PUBMED_BASE}/esearch.fcgi"
PUBMED_FETCH = f"{PUBMED_BASE}/efetch.fcgi"
PUBMED_SUMMARY = f"{PUBMED_BASE}/esummary.fcgi"


async def search_pubmed(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search PubMed for medical literature.

    Uses NCBI E-utilities (free, no API key required for <3 req/sec).
    """
    async with httpx.AsyncClient(timeout=30) as client:
        # Step 1: Search for article IDs
        search_resp = await client.get(PUBMED_SEARCH, params={
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
        })
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


async def fetch_abstract(pmid: str) -> str:
    """Fetch article abstract from PubMed."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(PUBMED_FETCH, params={
            "db": "pubmed",
            "id": pmid,
            "rettype": "abstract",
            "retmode": "text",
        })
        return resp.text


async def search_clinical_trials(condition: str, max_results: int = 5) -> list[dict]:
    """Search ClinicalTrials.gov for active trials."""
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
            trials.append({
                "nct_id": ident.get("nctId", ""),
                "title": ident.get("briefTitle", ""),
                "status": status.get("overallStatus", ""),
                "url": f"https://clinicaltrials.gov/study/{ident.get('nctId', '')}",
            })
        return trials
