"""Additional free medical API integrations."""
import logging
import httpx
from typing import Any

logger = logging.getLogger("aibolit.integrations.medical")


async def search_rxnorm(drug_name: str) -> dict[str, Any]:
    """Search RxNorm for drug normalization and interactions (NLM free API)."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Get RxCUI (RxNorm Concept Unique Identifier)
            resp = await client.get(
                "https://rxnav.nlm.nih.gov/REST/rxcui.json",
                params={"name": drug_name},
            )
            if resp.status_code != 200:
                return {"error": "RxNorm API недоступен"}

            data = resp.json()
            rxcui_group = data.get("idGroup", {})
            rxcui_list = rxcui_group.get("rxnormId", [])

            if not rxcui_list:
                return {"error": f"Препарат '{drug_name}' не найден в RxNorm"}

            rxcui = rxcui_list[0]

            # Get drug properties
            props_resp = await client.get(
                f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json"
            )
            props = props_resp.json().get("properties", {}) if props_resp.status_code == 200 else {}

            return {
                "rxcui": rxcui,
                "name": props.get("name", drug_name),
                "synonym": props.get("synonym", ""),
                "tty": props.get("tty", ""),
            }
    except Exception:
        logger.warning("RxNorm search failed for drug=%s", drug_name, exc_info=True)
        return {"error": f"Ошибка сети при поиске '{drug_name}' в RxNorm"}


async def check_drug_interactions(rxcui_list: list[str]) -> list[dict]:
    """Check drug-drug interactions via RxNorm Interaction API."""
    if len(rxcui_list) < 2:
        return []

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://rxnav.nlm.nih.gov/REST/interaction/list.json",
                params={"rxcuis": "+".join(rxcui_list)},
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            interactions = []
            for group in data.get("fullInteractionTypeGroup", []):
                for itype in group.get("fullInteractionType", []):
                    for pair in itype.get("interactionPair", []):
                        interactions.append({
                            "severity": pair.get("severity", ""),
                            "description": pair.get("description", ""),
                            "drugs": [
                                concept.get("minConceptItem", {}).get("name", "")
                                for concept in pair.get("interactionConcept", [])
                            ],
                        })
            return interactions
    except Exception:
        logger.warning("RxNorm interactions check failed", exc_info=True)
        return []


async def search_snomed(term: str) -> list[dict]:
    """Search SNOMED CT via free Snowstorm API."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://snowstorm.ihtsdotools.org/snowstorm/snomed-ct/MAIN/concepts",
                params={"term": term, "limit": 10, "activeFilter": True},
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return [
                    {
                        "conceptId": item.get("conceptId", ""),
                        "term": item.get("fsn", {}).get("term", ""),
                        "active": item.get("active", False),
                    }
                    for item in data.get("items", [])
                ]
    except Exception:
        logger.warning("SNOMED search failed for term=%s", term, exc_info=True)
    return []


async def get_gene_info(gene_symbol: str) -> dict[str, Any]:
    """Get gene information from NCBI Gene database (free API)."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Search for gene
            search_resp = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={
                    "db": "gene",
                    "term": f"{gene_symbol}[Gene Name] AND Homo sapiens[Organism]",
                    "retmode": "json",
                },
            )
            if search_resp.status_code != 200:
                return {"error": "NCBI Gene API недоступен"}

            search_data = search_resp.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])

            if not id_list:
                return {"error": f"Ген '{gene_symbol}' не найден"}

            # Get gene summary
            summary_resp = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "gene", "id": id_list[0], "retmode": "json"},
            )
            if summary_resp.status_code != 200:
                return {"error": "Ошибка получения данных о гене"}

            summary_data = summary_resp.json()
            gene_data = summary_data.get("result", {}).get(id_list[0], {})

            return {
                "gene_id": id_list[0],
                "symbol": gene_data.get("name", gene_symbol),
                "full_name": gene_data.get("description", ""),
                "chromosome": gene_data.get("chromosome", ""),
                "summary": gene_data.get("summary", ""),
                "aliases": gene_data.get("otheraliases", ""),
            }
    except Exception:
        logger.warning("NCBI Gene search failed for gene=%s", gene_symbol, exc_info=True)
        return {"error": f"Ошибка сети при поиске гена '{gene_symbol}'"}


async def search_omim(query: str) -> list[dict]:
    """Search OMIM for genetic disorders via NCBI."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={
                    "db": "omim",
                    "term": query,
                    "retmax": 5,
                    "retmode": "json",
                },
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])

            if not id_list:
                return []

            summary_resp = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "omim", "id": ",".join(id_list), "retmode": "json"},
            )
            results = []
            if summary_resp.status_code == 200:
                summary_data = summary_resp.json()
                for uid in id_list:
                    item = summary_data.get("result", {}).get(uid, {})
                    results.append({
                        "omim_id": uid,
                        "title": item.get("title", ""),
                    })
            return results
    except Exception:
        logger.warning("OMIM search failed for query=%s", query, exc_info=True)
        return []


async def search_open_targets(disease: str) -> list[dict]:
    """Search Open Targets for drug-disease associations (free GraphQL API)."""
    query = """
    query SearchDisease($q: String!) {
      search(queryString: $q, entityNames: ["disease"], page: {index: 0, size: 5}) {
        hits {
          id
          name
          description
          entity
        }
      }
    }
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.platform.opentargets.org/api/v4/graphql",
                json={"query": query, "variables": {"q": disease}},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", {}).get("search", {}).get("hits", [])
    except Exception:
        logger.warning("Open Targets search failed for disease=%s", disease, exc_info=True)
    return []
