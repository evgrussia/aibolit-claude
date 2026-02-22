"""OpenFDA integration for drug information and adverse events."""
import httpx
from typing import Any

FDA_BASE = "https://api.fda.gov"


async def search_drug(drug_name: str) -> dict[str, Any]:
    """Search OpenFDA for drug information (labels, side effects, interactions)."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Drug label search
            resp = await client.get(f"{FDA_BASE}/drug/label.json", params={
                "search": f'openfda.brand_name:"{drug_name}"+openfda.generic_name:"{drug_name}"',
                "limit": 1,
            })

            if resp.status_code != 200:
                return {"error": f"Препарат '{drug_name}' не найден в базе FDA"}

            data = resp.json()
            results = data.get("results", [])
            if not results:
                return {"error": f"Препарат '{drug_name}' не найден"}

            drug = results[0]
            openfda = drug.get("openfda", {})

            return {
                "brand_name": openfda.get("brand_name", [""])[0] if openfda.get("brand_name") else drug_name,
                "generic_name": openfda.get("generic_name", [""])[0] if openfda.get("generic_name") else "",
                "manufacturer": openfda.get("manufacturer_name", [""])[0] if openfda.get("manufacturer_name") else "",
                "route": openfda.get("route", []),
                "substance_name": openfda.get("substance_name", []),
                "indications": _extract_first(drug.get("indications_and_usage", [])),
                "dosage": _extract_first(drug.get("dosage_and_administration", [])),
                "contraindications": _extract_first(drug.get("contraindications", [])),
                "warnings": _extract_first(drug.get("warnings", [])),
                "adverse_reactions": _extract_first(drug.get("adverse_reactions", [])),
                "drug_interactions": _extract_first(drug.get("drug_interactions", [])),
                "pregnancy": _extract_first(drug.get("pregnancy", [])),
                "overdosage": _extract_first(drug.get("overdosage", [])),
                "mechanism_of_action": _extract_first(drug.get("mechanism_of_action", [])),
                "pharmacodynamics": _extract_first(drug.get("pharmacodynamics", [])),
            }
    except Exception:
        return {"error": f"Ошибка сети при поиске '{drug_name}' в OpenFDA"}


async def get_adverse_events(drug_name: str, limit: int = 10) -> list[dict]:
    """Get adverse event reports for a drug."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{FDA_BASE}/drug/event.json", params={
                "search": f'patient.drug.openfda.brand_name:"{drug_name}"',
                "limit": limit,
            })

            if resp.status_code != 200:
                return []

            data = resp.json()
            events = []
            for result in data.get("results", []):
                reactions = [r.get("reactionmeddrapt", "") for r in result.get("patient", {}).get("reaction", [])]
                patient = result.get("patient", {})
                events.append({
                    "serious": result.get("serious", ""),
                    "reactions": reactions,
                    "patient_onset_age": patient.get("patientonsetage", ""),
                    "patient_sex": patient.get("patientsex", ""),
                    "outcome": result.get("seriousnessdeath", ""),
                })
            return events
    except Exception:
        return []


async def check_drug_recall(drug_name: str) -> list[dict]:
    """Check for drug recalls."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{FDA_BASE}/drug/enforcement.json", params={
                "search": f'product_description:"{drug_name}"',
                "limit": 5,
                "sort": "report_date:desc",
            })

            if resp.status_code != 200:
                return []

            return [
                {
                    "reason": r.get("reason_for_recall", ""),
                    "classification": r.get("classification", ""),
                    "status": r.get("status", ""),
                    "date": r.get("report_date", ""),
                }
                for r in resp.json().get("results", [])
            ]
    except Exception:
        return []


def _extract_first(lst: list) -> str:
    """Extract first element from list, truncate if too long."""
    if not lst:
        return ""
    text = lst[0]
    if len(text) > 2000:
        return text[:2000] + "..."
    return text
