"""Reference data endpoints (specializations)."""
from fastapi import APIRouter

from src.agents.specializations import SPECIALIZATIONS

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/specializations")
def specializations():
    result = []
    for spec_id, spec in SPECIALIZATIONS.items():
        result.append({
            "id": spec_id,
            "name_ru": spec.name_ru,
            "name_en": spec.name_en,
            "description": spec.description,
            "skills": [
                {"name": s.name, "description": s.description}
                for s in spec.skills
            ],
        })
    return result
