"""WHO ICD-11 and disease information integration."""
import httpx
from typing import Any

# WHO ICD-11 API (free, requires token for production but has open endpoints)
ICD_API_BASE = "https://id.who.int/icd"


async def search_icd11(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search ICD-11 for disease classification codes."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(
                f"{ICD_API_BASE}/release/11/2024-01/mms/search",
                params={
                    "q": query,
                    "subtreeFilterUsesFoundationDescendants": "false",
                    "includeKeywordResult": "true",
                    "useFlexiSearch": "true",
                    "flatResults": "true",
                    "highlightingEnabled": "false",
                },
                headers={
                    "Accept": "application/json",
                    "Accept-Language": "en",
                    "API-Version": "v2",
                },
            )
            if resp.status_code != 200:
                return _fallback_icd_search(query)

            data = resp.json()
            results = []
            for item in data.get("destinationEntities", [])[:max_results]:
                results.append({
                    "code": item.get("theCode", ""),
                    "title": item.get("title", ""),
                    "definition": item.get("definition", ""),
                    "uri": item.get("id", ""),
                })
            return results
        except Exception:
            return _fallback_icd_search(query)


def _fallback_icd_search(query: str) -> list[dict]:
    """Fallback ICD search using local ICD-10 database."""
    from ..models.medical_refs import ICD10_COMMON
    query_lower = query.lower()
    results = []
    for code, name in ICD10_COMMON.items():
        if query_lower in name.lower() or query_lower in code.lower():
            results.append({"code": code, "title": name, "source": "ICD-10 (local)"})
    return results


async def get_disease_info(disease_name: str) -> dict[str, Any]:
    """Get comprehensive disease information from multiple free sources."""
    info = {
        "name": disease_name,
        "icd_codes": [],
        "description": "",
        "symptoms": [],
        "risk_factors": [],
        "diagnostics": [],
        "treatment_guidelines": [],
    }

    # Search ICD codes
    info["icd_codes"] = await search_icd11(disease_name, max_results=5)

    return info


async def search_who_guidelines(topic: str) -> list[dict]:
    """Search WHO guidelines and recommendations."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(
                "https://app.magicapp.org/api/v1/guidelines",
                params={"q": topic, "limit": 5},
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                return resp.json().get("results", [])
        except Exception:
            pass
    return []
