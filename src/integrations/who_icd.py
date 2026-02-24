"""WHO ICD-11 and disease information integration."""
import logging
import os
import time
import httpx
from typing import Any

logger = logging.getLogger("aibolit.integrations.icd")

# WHO ICD-11 API
ICD_API_BASE = "https://id.who.int/icd"
ICD_TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"

# OAuth2 credentials (optional — without them, fallback to local ICD-10)
_CLIENT_ID = os.environ.get("WHO_ICD_CLIENT_ID", "")
_CLIENT_SECRET = os.environ.get("WHO_ICD_CLIENT_SECRET", "")

# Cached token
_token_cache: dict[str, Any] = {"token": "", "expires_at": 0}


async def _get_access_token(client: httpx.AsyncClient) -> str:
    """Get OAuth2 Bearer token from WHO ICD API, with caching."""
    if not _CLIENT_ID or not _CLIENT_SECRET:
        return ""

    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]

    try:
        resp = await client.post(
            ICD_TOKEN_URL,
            data={
                "client_id": _CLIENT_ID,
                "client_secret": _CLIENT_SECRET,
                "grant_type": "client_credentials",
                "scope": "icdapi_access",
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            _token_cache["token"] = data["access_token"]
            _token_cache["expires_at"] = now + data.get("expires_in", 3600)
            return _token_cache["token"]
        else:
            logger.warning("WHO ICD token request failed: %d", resp.status_code)
            return ""
    except Exception:
        logger.warning("WHO ICD token request error", exc_info=True)
        return ""


async def search_icd11(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search ICD-11 for disease classification codes."""
    if not _CLIENT_ID:
        return _fallback_icd_search(query)

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            token = await _get_access_token(client)
            if not token:
                return _fallback_icd_search(query)

            headers = {
                "Accept": "application/json",
                "Accept-Language": "en",
                "API-Version": "v2",
                "Authorization": f"Bearer {token}",
            }
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
                headers=headers,
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
            logger.warning("WHO ICD-11 search failed for query=%s, using fallback", query, exc_info=True)
            return _fallback_icd_search(query)


async def get_disease_info(name: str) -> dict[str, Any]:
    """Get disease information by searching ICD-11 and returning structured data."""
    results = await search_icd11(name, max_results=5)
    return {
        "name": name,
        "icd_codes": results,
        "description": results[0].get("definition", "") if results else "",
        "symptoms": [],
        "risk_factors": [],
    }


def _fallback_icd_search(query: str) -> list[dict]:
    """Fallback ICD search using local ICD-10 database."""
    from ..models.medical_refs import ICD10_COMMON
    query_lower = query.lower()
    results = []
    for code, name in ICD10_COMMON.items():
        if query_lower in name.lower() or query_lower in code.lower():
            results.append({"code": code, "title": name, "source": "ICD-10 (local)"})
    return results
