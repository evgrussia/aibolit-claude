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
