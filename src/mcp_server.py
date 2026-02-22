"""
Aibolit AI Medical Clinic — MCP Server.

This is the main entry point. It registers all medical tools that Claude
can call through the Model Context Protocol (MCP).

Run:
    python -m src.mcp_server          (stdio transport for Claude Desktop / Claude Code)
    python -m src.mcp_server --sse    (SSE transport for web)
"""
from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ── Internal imports ──────────────────────────────────────────────
from .agents.specializations import (
    SPECIALIZATIONS, list_specializations, get_specialization, find_specialist_for_icd,
)
from .tools.diagnostic import (
    analyze_lab_results, calculate_gfr, calculate_cardiovascular_risk,
    check_drug_interactions_local, assess_vitals,
)
from .tools.documentation import (
    generate_medical_record, generate_referral,
    generate_prescription, generate_discharge_summary,
)
from .integrations.pubmed import search_pubmed, fetch_abstract, search_clinical_trials
from .integrations.openfda import search_drug, get_adverse_events, check_drug_recall
from .integrations.who_icd import search_icd11
from .integrations.medical_apis import (
    search_rxnorm, check_drug_interactions, search_snomed,
    get_gene_info, search_omim, search_open_targets,
)
from .models.medical_refs import LAB_REFERENCE_RANGES, ICD10_COMMON, interpret_lab_value
from .utils.database import (
    save_patient, load_patient, list_patients, delete_patient,
    add_vitals as db_add_vitals,
    add_lab_result as db_add_lab_result,
    add_diagnosis as db_add_diagnosis,
    add_medication as db_add_medication,
    save_consultation, get_consultation_history,
    get_lab_trends, get_vitals_trends,
    search_patients, get_patients_by_diagnosis,
    init_db,
)
from .models.patient import (
    Patient, VitalSigns, Allergy, Medication, LabResult, Diagnosis, Gender, BloodType,
)

# ══════════════════════════════════════════════════════════════════
# Server instance
# ══════════════════════════════════════════════════════════════════
app = Server("aibolit-clinic")


# ══════════════════════════════════════════════════════════════════
# Tool Registry
# ══════════════════════════════════════════════════════════════════

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the full catalogue of available medical tools."""
    tools = [
        # ── Clinic navigation ──
        Tool(
            name="clinic_reception",
            description=(
                "Ресепшн клиники Aibolit. Приветствует пациента, помогает выбрать специалиста, "
                "описывает возможности клиники. Вызывай этот инструмент при первом обращении пациента."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Запрос или жалобы пациента"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="list_doctors",
            description="Показать список всех AI-врачей клиники с их специализациями и навыками.",
            inputSchema={
                "type": "object",
                "properties": {
                    "specialty_filter": {"type": "string", "description": "Фильтр по специальности (опционально)"},
                },
            },
        ),
        Tool(
            name="consult_doctor",
            description=(
                "Консультация у AI-врача определённой специализации. "
                "Врач проведёт осмотр, соберёт анамнез, поставит предварительный диагноз и назначит лечение."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "specialty": {
                        "type": "string",
                        "description": "ID специализации врача (therapist, cardiologist, neurologist и т.д.)",
                    },
                    "complaints": {"type": "string", "description": "Жалобы пациента"},
                    "patient_id": {"type": "string", "description": "ID пациента (если есть карта)"},
                },
                "required": ["specialty", "complaints"],
            },
        ),

        # ── Diagnostics ──
        Tool(
            name="analyze_lab_results",
            description=(
                "Расшифровка лабораторных анализов. Интерпретирует результаты ОАК, биохимии, "
                "коагулограммы, гормонов, онкомаркёров с выявлением паттернов заболеваний."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "test": {"type": "string", "description": "Код теста (glucose_fasting, hemoglobin, alt, tsh и т.д.)"},
                                "value": {"type": "number", "description": "Числовое значение результата"},
                            },
                            "required": ["test", "value"],
                        },
                        "description": "Массив результатов анализов",
                    },
                    "gender": {"type": "string", "enum": ["male", "female"], "description": "Пол пациента"},
                },
                "required": ["results"],
            },
        ),
        Tool(
            name="assess_vitals",
            description=(
                "Оценка витальных показателей пациента: давление, пульс, температура, "
                "сатурация, ЧД, глюкоза крови. Выявляет отклонения и критические состояния."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "systolic_bp": {"type": "integer", "description": "Систолическое АД (мм рт.ст.)"},
                    "diastolic_bp": {"type": "integer", "description": "Диастолическое АД (мм рт.ст.)"},
                    "heart_rate": {"type": "integer", "description": "ЧСС (уд/мин)"},
                    "temperature": {"type": "number", "description": "Температура тела (°C)"},
                    "spo2": {"type": "number", "description": "Сатурация кислорода (%)"},
                    "respiratory_rate": {"type": "integer", "description": "Частота дыхания (/мин)"},
                    "blood_glucose": {"type": "number", "description": "Глюкоза крови (ммоль/л)"},
                },
            },
        ),
        Tool(
            name="calculate_gfr",
            description="Рассчитать скорость клубочковой фильтрации (СКФ) по CKD-EPI и определить стадию ХБП.",
            inputSchema={
                "type": "object",
                "properties": {
                    "creatinine": {"type": "number", "description": "Креатинин (мкмоль/л)"},
                    "age": {"type": "integer", "description": "Возраст пациента"},
                    "gender": {"type": "string", "enum": ["male", "female"]},
                },
                "required": ["creatinine", "age", "gender"],
            },
        ),
        Tool(
            name="cardiovascular_risk",
            description="Оценка 10-летнего риска сердечно-сосудистых событий (аналог SCORE/Framingham).",
            inputSchema={
                "type": "object",
                "properties": {
                    "age": {"type": "integer"},
                    "gender": {"type": "string", "enum": ["male", "female"]},
                    "systolic_bp": {"type": "integer", "description": "Систолическое АД"},
                    "total_cholesterol": {"type": "number", "description": "Общий холестерин (ммоль/л)"},
                    "hdl": {"type": "number", "description": "ЛПВП (ммоль/л)"},
                    "smoker": {"type": "boolean", "default": False},
                    "diabetic": {"type": "boolean", "default": False},
                    "on_bp_treatment": {"type": "boolean", "default": False},
                },
                "required": ["age", "gender", "systolic_bp", "total_cholesterol", "hdl"],
            },
        ),

        # ── Drug & Interaction Tools ──
        Tool(
            name="drug_info",
            description=(
                "Полная информация о лекарственном препарате из базы FDA: "
                "показания, дозировки, противопоказания, побочные эффекты, взаимодействия."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "Название препарата (на английском)"},
                },
                "required": ["drug_name"],
            },
        ),
        Tool(
            name="check_drug_interactions",
            description=(
                "Проверка лекарственных взаимодействий между несколькими препаратами. "
                "Использует базу критических взаимодействий и RxNorm API."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "drugs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Список названий препаратов для проверки",
                    },
                },
                "required": ["drugs"],
            },
        ),
        Tool(
            name="drug_adverse_events",
            description="Получить отчёты о побочных эффектах препарата из базы FDA FAERS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["drug_name"],
            },
        ),
        Tool(
            name="check_drug_recall",
            description="Проверить отзывы препарата из базы FDA.",
            inputSchema={
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string"},
                },
                "required": ["drug_name"],
            },
        ),

        # ── Medical Research ──
        Tool(
            name="search_medical_literature",
            description=(
                "Поиск медицинской литературы в PubMed/NCBI. "
                "Доказательная медицина: статьи, мета-анализы, клинические руководства."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Поисковый запрос (на английском для лучших результатов)"},
                    "max_results": {"type": "integer", "default": 10},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_article_abstract",
            description="Получить абстракт статьи из PubMed по PMID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pmid": {"type": "string", "description": "PubMed ID статьи"},
                },
                "required": ["pmid"],
            },
        ),
        Tool(
            name="search_clinical_trials",
            description="Поиск клинических исследований на ClinicalTrials.gov.",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "Заболевание или состояние"},
                    "max_results": {"type": "integer", "default": 5},
                },
                "required": ["condition"],
            },
        ),

        # ── Classification & Coding ──
        Tool(
            name="search_icd",
            description="Поиск кодов МКБ-10/МКБ-11 по названию заболевания.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Название заболевания или симптома"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="search_snomed",
            description="Поиск клинических терминов в SNOMED CT.",
            inputSchema={
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                },
                "required": ["term"],
            },
        ),

        # ── Genetics ──
        Tool(
            name="gene_info",
            description="Информация о гене из NCBI Gene (для фармакогенетики и генетического консультирования).",
            inputSchema={
                "type": "object",
                "properties": {
                    "gene_symbol": {"type": "string", "description": "Символ гена (напр. BRCA1, CYP2D6)"},
                },
                "required": ["gene_symbol"],
            },
        ),
        Tool(
            name="search_genetic_disorders",
            description="Поиск наследственных заболеваний в OMIM.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="search_drug_targets",
            description="Поиск мишеней для лекарственной терапии заболевания (Open Targets).",
            inputSchema={
                "type": "object",
                "properties": {
                    "disease": {"type": "string"},
                },
                "required": ["disease"],
            },
        ),

        # ── Documentation ──
        Tool(
            name="generate_medical_record",
            description=(
                "Сгенерировать медицинскую карту пациента: история болезни с жалобами, "
                "анамнезом, осмотром, диагнозом и планом лечения."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "patient_age": {"type": "integer"},
                    "gender": {"type": "string", "enum": ["male", "female"]},
                    "complaints": {"type": "string"},
                    "anamnesis": {"type": "string"},
                    "examination": {"type": "string"},
                    "diagnoses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "icd10_code": {"type": "string"},
                                "confidence": {"type": "number"},
                            },
                        },
                    },
                    "plan": {"type": "string"},
                    "doctor_specialty": {"type": "string"},
                    "vitals": {"type": "object"},
                    "lab_results": {"type": "array"},
                },
                "required": ["patient_name", "patient_age", "gender", "complaints",
                             "anamnesis", "examination", "diagnoses", "plan"],
            },
        ),
        Tool(
            name="generate_referral",
            description="Сгенерировать направление к другому специалисту.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "patient_age": {"type": "integer"},
                    "from_specialty": {"type": "string"},
                    "to_specialty": {"type": "string"},
                    "reason": {"type": "string"},
                    "current_diagnoses": {"type": "array", "items": {"type": "string"}},
                    "relevant_results": {"type": "string"},
                    "urgency": {"type": "string", "enum": ["routine", "urgent", "emergency"]},
                },
                "required": ["patient_name", "patient_age", "from_specialty", "to_specialty",
                             "reason", "current_diagnoses"],
            },
        ),
        Tool(
            name="generate_prescription",
            description="Сгенерировать лист назначений (рецепт).",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "medications": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "dosage": {"type": "string"},
                                "frequency": {"type": "string"},
                                "route": {"type": "string"},
                                "duration": {"type": "string"},
                                "notes": {"type": "string"},
                            },
                            "required": ["name"],
                        },
                    },
                    "diagnoses": {"type": "array", "items": {"type": "string"}},
                    "doctor_specialty": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["patient_name", "medications", "diagnoses"],
            },
        ),
        Tool(
            name="generate_discharge_summary",
            description="Сгенерировать выписной эпикриз.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "patient_age": {"type": "integer"},
                    "gender": {"type": "string"},
                    "admission_date": {"type": "string"},
                    "discharge_date": {"type": "string"},
                    "admission_diagnosis": {"type": "string"},
                    "final_diagnosis": {"type": "string"},
                    "treatment_summary": {"type": "string"},
                    "discharge_condition": {"type": "string"},
                    "discharge_medications": {"type": "array"},
                    "follow_up": {"type": "string"},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["patient_name", "patient_age", "gender", "admission_date",
                             "discharge_date", "admission_diagnosis", "final_diagnosis",
                             "treatment_summary", "discharge_condition", "follow_up", "recommendations"],
            },
        ),

        # ── Patient Management ──
        Tool(
            name="register_patient",
            description="Зарегистрировать нового пациента в системе.",
            inputSchema={
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "date_of_birth": {"type": "string", "description": "YYYY-MM-DD"},
                    "gender": {"type": "string", "enum": ["male", "female", "other"]},
                    "blood_type": {"type": "string", "description": "A+, A-, B+, B-, AB+, AB-, O+, O-"},
                    "allergies": {"type": "array", "items": {"type": "string"}},
                    "family_history": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["first_name", "last_name", "date_of_birth", "gender"],
            },
        ),
        Tool(
            name="get_patient",
            description="Получить карту пациента по ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="list_patients",
            description="Показать список всех зарегистрированных пациентов.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="add_vitals",
            description="Записать витальные показатели пациента.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "systolic_bp": {"type": "integer"},
                    "diastolic_bp": {"type": "integer"},
                    "heart_rate": {"type": "integer"},
                    "temperature": {"type": "number"},
                    "spo2": {"type": "number"},
                    "respiratory_rate": {"type": "integer"},
                    "weight": {"type": "number"},
                    "height": {"type": "number"},
                    "blood_glucose": {"type": "number"},
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="add_lab_result",
            description="Добавить результат анализа в карту пациента.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "test_name": {"type": "string"},
                    "value": {"type": "number"},
                    "unit": {"type": "string"},
                    "reference_range": {"type": "string"},
                },
                "required": ["patient_id", "test_name", "value"],
            },
        ),
        Tool(
            name="add_diagnosis",
            description="Добавить диагноз в карту пациента.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "icd10_code": {"type": "string"},
                    "name": {"type": "string"},
                    "status": {"type": "string", "enum": ["active", "resolved", "chronic"]},
                    "confidence": {"type": "number", "description": "AI confidence 0-1"},
                },
                "required": ["patient_id", "icd10_code", "name"],
            },
        ),
        Tool(
            name="add_medication",
            description="Назначить лекарственный препарат пациенту.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "name": {"type": "string"},
                    "dosage": {"type": "string"},
                    "frequency": {"type": "string"},
                    "route": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["patient_id", "name", "dosage", "frequency"],
            },
        ),

        # ── History & Analytics ──
        Tool(
            name="get_consultation_history",
            description="Получить историю консультаций пациента или по специализации врача.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string", "description": "ID пациента (опционально)"},
                    "specialty": {"type": "string", "description": "ID специализации (опционально)"},
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="get_lab_trends",
            description="Получить динамику лабораторного показателя пациента за всё время.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "test_name": {"type": "string", "description": "Название теста (или часть)"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["patient_id", "test_name"],
            },
        ),
        Tool(
            name="get_vitals_history",
            description="Получить историю витальных показателей пациента.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="search_patients",
            description="Поиск пациентов по имени или фамилии.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Строка поиска (часть имени/фамилии)"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_patients_by_diagnosis",
            description="Найти пациентов по коду МКБ-10 (диагнозу).",
            inputSchema={
                "type": "object",
                "properties": {
                    "icd10_prefix": {"type": "string", "description": "Начало кода МКБ-10 (напр. I10, E11, J45)"},
                },
                "required": ["icd10_prefix"],
            },
        ),

        # ── Lab Reference ──
        Tool(
            name="lab_reference_ranges",
            description="Справочник референсных значений лабораторных анализов.",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "Код теста или 'all' для полного списка"},
                },
                "required": ["test_name"],
            },
        ),
    ]

    return tools


# ══════════════════════════════════════════════════════════════════
# Tool Handlers
# ══════════════════════════════════════════════════════════════════

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch tool calls to implementations."""
    try:
        result = await _dispatch(name, arguments)
        text = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, (dict, list)) else str(result)
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=f"Ошибка: {type(e).__name__}: {e}")]


async def _dispatch(name: str, args: dict) -> Any:
    """Route tool call to the correct handler."""

    # ── Clinic ──
    if name == "clinic_reception":
        return _handle_reception(args["query"])

    elif name == "list_doctors":
        return _handle_list_doctors(args.get("specialty_filter"))

    elif name == "consult_doctor":
        return _handle_consultation(args["specialty"], args["complaints"], args.get("patient_id"))

    # ── Diagnostics ──
    elif name == "analyze_lab_results":
        return analyze_lab_results(args["results"], args.get("gender", "male"))

    elif name == "assess_vitals":
        return assess_vitals(**{k: v for k, v in args.items() if v is not None})

    elif name == "calculate_gfr":
        return calculate_gfr(args["creatinine"], args["age"], args["gender"])

    elif name == "cardiovascular_risk":
        return calculate_cardiovascular_risk(
            age=args["age"], gender=args["gender"],
            systolic_bp=args["systolic_bp"],
            total_cholesterol=args["total_cholesterol"],
            hdl=args["hdl"],
            smoker=args.get("smoker", False),
            diabetic=args.get("diabetic", False),
            on_bp_treatment=args.get("on_bp_treatment", False),
        )

    # ── Drugs ──
    elif name == "drug_info":
        return await search_drug(args["drug_name"])

    elif name == "check_drug_interactions":
        drugs = args["drugs"]
        local = check_drug_interactions_local(drugs)
        # Also try RxNorm API
        rxcuis = []
        for d in drugs:
            info = await search_rxnorm(d)
            if "rxcui" in info:
                rxcuis.append(info["rxcui"])
        api_interactions = await check_drug_interactions(rxcuis) if len(rxcuis) >= 2 else []
        return {
            "critical_local": local,
            "rxnorm_interactions": api_interactions,
            "drugs_checked": drugs,
        }

    elif name == "drug_adverse_events":
        return await get_adverse_events(args["drug_name"], args.get("limit", 10))

    elif name == "check_drug_recall":
        return await check_drug_recall(args["drug_name"])

    # ── Research ──
    elif name == "search_medical_literature":
        return await search_pubmed(args["query"], args.get("max_results", 10))

    elif name == "get_article_abstract":
        return await fetch_abstract(args["pmid"])

    elif name == "search_clinical_trials":
        return await search_clinical_trials(args["condition"], args.get("max_results", 5))

    # ── Classification ──
    elif name == "search_icd":
        return await search_icd11(args["query"])

    elif name == "search_snomed":
        return await search_snomed(args["term"])

    # ── Genetics ──
    elif name == "gene_info":
        return await get_gene_info(args["gene_symbol"])

    elif name == "search_genetic_disorders":
        return await search_omim(args["query"])

    elif name == "search_drug_targets":
        return await search_open_targets(args["disease"])

    # ── Documentation ──
    elif name == "generate_medical_record":
        return generate_medical_record(**args)

    elif name == "generate_referral":
        return generate_referral(**args)

    elif name == "generate_prescription":
        return generate_prescription(**args)

    elif name == "generate_discharge_summary":
        return generate_discharge_summary(**args)

    # ── Patient Management ──
    elif name == "register_patient":
        return _handle_register_patient(args)

    elif name == "get_patient":
        return _handle_get_patient(args["patient_id"])

    elif name == "list_patients":
        return list_patients()

    elif name == "add_vitals":
        return _handle_add_vitals(args)

    elif name == "add_lab_result":
        return _handle_add_lab_result(args)

    elif name == "add_diagnosis":
        return _handle_add_diagnosis(args)

    elif name == "add_medication":
        return _handle_add_medication(args)

    # ── History & Analytics ──
    elif name == "get_consultation_history":
        return get_consultation_history(
            patient_id=args.get("patient_id"),
            specialty=args.get("specialty"),
            limit=args.get("limit", 20),
        )

    elif name == "get_lab_trends":
        return get_lab_trends(args["patient_id"], args["test_name"], args.get("limit", 20))

    elif name == "get_vitals_history":
        return get_vitals_trends(args["patient_id"], args.get("limit", 20))

    elif name == "search_patients":
        return search_patients(args["query"])

    elif name == "get_patients_by_diagnosis":
        return get_patients_by_diagnosis(args["icd10_prefix"])

    elif name == "lab_reference_ranges":
        return _handle_lab_reference(args["test_name"])

    else:
        return {"error": f"Unknown tool: {name}"}


# ══════════════════════════════════════════════════════════════════
# Handler implementations
# ══════════════════════════════════════════════════════════════════

def _handle_reception(query: str) -> dict:
    """Welcome patient and suggest appropriate specialist."""
    specializations = list_specializations()
    keyword_map = {
        "серд": "cardiologist", "давлен": "cardiologist", "аритм": "cardiologist", "боль в груди": "cardiologist",
        "голов": "neurologist", "нерв": "neurologist", "инсульт": "neurologist", "мигрен": "neurologist",
        "кож": "dermatologist", "сыпь": "dermatologist", "родинк": "dermatologist", "прыщ": "dermatologist",
        "желуд": "gastroenterologist", "живот": "gastroenterologist", "печен": "gastroenterologist", "тошнот": "gastroenterologist",
        "лёгк": "pulmonologist", "кашел": "pulmonologist", "одышк": "pulmonologist", "дыхан": "pulmonologist",
        "сахар": "endocrinologist", "диабет": "endocrinologist", "щитовид": "endocrinologist", "гормон": "endocrinologist",
        "почк": "nephrologist", "моч": "urologist", "простат": "urologist",
        "суста": "rheumatologist", "артрит": "rheumatologist",
        "кост": "orthopedist", "перелом": "orthopedist", "спин": "orthopedist",
        "глаз": "ophthalmologist", "зрен": "ophthalmologist",
        "ух": "ent", "горл": "ent", "нос": "ent",
        "зуб": "dentist", "дёсен": "dentist",
        "ребён": "pediatrician", "дет": "pediatrician",
        "депресс": "psychiatrist", "тревог": "psychiatrist", "сон": "psychiatrist",
        "опухол": "oncologist", "рак": "oncologist", "образован": "oncologist",
        "кров": "hematologist", "анем": "hematologist",
        "аллерг": "allergist", "крапивниц": "allergist",
        "инфекц": "infectionist", "температур": "infectionist", "вирус": "infectionist",
        "берем": "gynecologist", "менструа": "gynecologist", "гинеколог": "gynecologist",
        "похуд": "nutritionist", "диет": "nutritionist", "вес": "nutritionist",
        "реабилит": "rehabilitation", "восстановлен": "rehabilitation",
        "генетик": "geneticist", "наследств": "geneticist",
        "спорт": "sports_medicine", "трениров": "sports_medicine",
        "пожил": "geriatrician", "старч": "geriatrician",
        "скор": "emergency", "экстрен": "emergency", "неотлож": "emergency",
    }

    suggested = []
    query_lower = query.lower()
    for keyword, spec_id in keyword_map.items():
        if keyword in query_lower and spec_id not in suggested:
            suggested.append(spec_id)

    if not suggested:
        suggested = ["therapist"]

    suggested_details = []
    for sid in suggested[:3]:
        spec = get_specialization(sid)
        if spec:
            suggested_details.append({
                "id": spec.id,
                "name": spec.name_ru,
                "description": spec.description,
                "skills": [s.name for s in spec.skills],
            })

    return {
        "greeting": (
            "🏥 Добро пожаловать в клинику Aibolit!\n\n"
            "Я — AI-администратор клиники. У нас работают 35 AI-врачей "
            "по всем медицинским специализациям.\n\n"
            "⚠️ ВАЖНО: AI-система предоставляет информационную поддержку и НЕ заменяет "
            "консультацию реального врача. Все рекомендации требуют верификации специалистом."
        ),
        "your_query": query,
        "suggested_specialists": suggested_details,
        "how_to_consult": "Для консультации используйте инструмент consult_doctor с ID специалиста.",
        "total_specialists": len(SPECIALIZATIONS),
    }


def _handle_list_doctors(filter_text: str | None = None) -> dict:
    specs = list_specializations()
    if filter_text:
        filter_lower = filter_text.lower()
        specs = [s for s in specs if filter_lower in s["name_ru"].lower()
                 or filter_lower in s["name_en"].lower()
                 or filter_lower in s["description"].lower()]

    # Group by category
    categories = {
        "Терапевтические": ["therapist", "cardiologist", "neurologist", "pulmonologist",
                            "gastroenterologist", "endocrinologist", "nephrologist", "rheumatologist",
                            "hematologist", "infectionist", "allergist", "geriatrician"],
        "Хирургические": ["surgeon", "cardiac_surgeon", "neurosurgeon", "vascular_surgeon",
                          "orthopedist", "urologist"],
        "Диагностические": ["radiologist", "pathologist", "pharmacologist"],
        "Специализированные": ["dermatologist", "ophthalmologist", "ent", "gynecologist",
                               "pediatrician", "psychiatrist", "oncologist", "dentist",
                               "nutritionist", "sports_medicine", "rehabilitation", "geneticist"],
        "Экстренные": ["emergency", "intensivist"],
    }

    result = {"total": len(specs), "categories": {}}
    for cat_name, ids in categories.items():
        cat_specs = [s for s in specs if s["id"] in ids]
        if cat_specs:
            result["categories"][cat_name] = cat_specs

    return result


def _handle_consultation(specialty: str, complaints: str, patient_id: str | None = None) -> dict:
    """Generate a structured AI doctor consultation."""
    spec = get_specialization(specialty)
    if not spec:
        available = [s.id for s in SPECIALIZATIONS.values()]
        return {"error": f"Специализация '{specialty}' не найдена. Доступные: {', '.join(available)}"}

    patient_summary = ""
    if patient_id:
        patient = load_patient(patient_id)
        if patient:
            patient_summary = patient.summary()

    # Build human-readable summary based on complaints and specialization data
    summary = _build_consultation_summary(spec, complaints, patient_summary)

    result = {
        "doctor": {
            "specialty_id": spec.id,
            "name": f"AI-{spec.name_ru}",
            "qualification": spec.description,
        },
        "consultation": {
            "complaints": complaints,
            "patient_context": patient_summary or "Карта пациента не загружена",
            "summary": summary,
            "available_skills": [
                {"name": s.name, "description": s.description, "tool": s.tool_name}
                for s in spec.skills
            ],
            "relevant_icd_prefixes": spec.related_icd_prefixes[:10],
            "recommended_tests": spec.required_lab_tests,
        },
        "instructions": (
            f"Вы — AI-{spec.name_ru}. Проведите консультацию по жалобам пациента.\n"
            f"1. Соберите детальный анамнез (уточняющие вопросы)\n"
            f"2. Используйте доступные навыки для диагностики\n"
            f"3. Сформулируйте предварительный диагноз с кодом МКБ-10\n"
            f"4. Назначьте обследования и лечение\n"
            f"5. При необходимости направьте к другому специалисту\n\n"
            f"⚠️ Все рекомендации носят информационный характер."
        ),
        "disclaimer": "AI-консультация не заменяет визит к реальному врачу.",
    }

    # Persist consultation to database
    save_consultation(
        specialty=specialty,
        complaints=complaints,
        response=result,
        patient_id=patient_id,
    )

    return result


def _build_consultation_summary(spec, complaints: str, patient_summary: str) -> str:
    """Build a human-readable doctor consultation summary."""
    lines: list[str] = []

    # 1. Acknowledge complaints
    lines.append(f"Здравствуйте! Я AI-{spec.name_ru}.")
    lines.append(f"Вы обратились с жалобами: {complaints}")
    lines.append("")

    # 2. Patient context
    if patient_summary and patient_summary != "Карта пациента не загружена":
        lines.append("Данные из вашей медицинской карты учтены при оценке.")
        lines.append("")

    # 3. Possible conditions based on ICD prefixes
    matched_conditions = []
    for prefix in spec.related_icd_prefixes[:10]:
        for code, name in ICD10_COMMON.items():
            if code.startswith(prefix):
                matched_conditions.append(f"{code} — {name}")
                break
    if matched_conditions:
        lines.append("На основании жалоб и специализации, возможные состояния:")
        for cond in matched_conditions[:5]:
            lines.append(f"  • {cond}")
        lines.append("")

    # 4. Recommended tests
    if spec.required_lab_tests:
        test_names = []
        for key in spec.required_lab_tests[:8]:
            ref = LAB_REFERENCE_RANGES.get(key)
            test_names.append(ref["name"] if ref else key)
        lines.append("Рекомендуемые обследования:")
        for name in test_names:
            lines.append(f"  • {name}")
        lines.append("")

    # 5. General advice
    lines.append("Рекомендации:")
    lines.append("  • Обратитесь к врачу очно для подтверждения диагноза")
    lines.append("  • Пройдите рекомендованные обследования")
    lines.append("  • При ухудшении состояния вызовите скорую помощь")

    return "\n".join(lines)


def _handle_register_patient(args: dict) -> dict:
    from datetime import date as d
    import uuid
    patient_id = str(uuid.uuid4())[:8]
    patient = Patient(
        id=patient_id,
        first_name=args["first_name"],
        last_name=args["last_name"],
        date_of_birth=d.fromisoformat(args["date_of_birth"]),
        gender=Gender(args["gender"]),
        blood_type=BloodType(args["blood_type"]) if args.get("blood_type") else None,
        allergies=[Allergy(substance=a) for a in args.get("allergies", [])],
        family_history=args.get("family_history", []),
    )
    save_patient(patient)
    return {"patient_id": patient_id, "name": patient.full_name, "status": "registered"}


def _handle_get_patient(patient_id: str) -> dict:
    patient = load_patient(patient_id)
    if not patient:
        return {"error": f"Пациент {patient_id} не найден"}
    return {
        "id": patient.id,
        "name": patient.full_name,
        "age": patient.age,
        "gender": patient.gender.value,
        "blood_type": patient.blood_type.value if patient.blood_type else None,
        "summary": patient.summary(),
        "active_diagnoses": [{"code": d.icd10_code, "name": d.name} for d in patient.active_diagnoses],
        "medications": [{"name": m.name, "dosage": m.dosage} for m in patient.medications],
        "allergies": [a.substance for a in patient.allergies],
    }


def _handle_add_vitals(args: dict) -> dict:
    v = VitalSigns(
        systolic_bp=args.get("systolic_bp"),
        diastolic_bp=args.get("diastolic_bp"),
        heart_rate=args.get("heart_rate"),
        temperature=args.get("temperature"),
        spo2=args.get("spo2"),
        respiratory_rate=args.get("respiratory_rate"),
        weight=args.get("weight"),
        height=args.get("height"),
        blood_glucose=args.get("blood_glucose"),
    )
    try:
        db_add_vitals(args["patient_id"], v)
    except ValueError:
        return {"error": "Пациент не найден"}
    alerts = v.assess()
    return {"status": "saved", "alerts": alerts, "bmi": v.bmi()}


def _handle_add_lab_result(args: dict) -> dict:
    lr = LabResult(
        test_name=args["test_name"],
        value=args["value"],
        unit=args.get("unit", ""),
        reference_range=args.get("reference_range", ""),
    )
    try:
        db_add_lab_result(args["patient_id"], lr)
    except ValueError:
        return {"error": "Пациент не найден"}
    return {"status": "saved", "test": lr.test_name, "value": lr.value}


def _handle_add_diagnosis(args: dict) -> dict:
    diag = Diagnosis(
        icd10_code=args["icd10_code"],
        name=args["name"],
        status=args.get("status", "active"),
        confidence=args.get("confidence", 0.0),
    )
    try:
        db_add_diagnosis(args["patient_id"], diag)
    except ValueError:
        return {"error": "Пациент не найден"}
    return {"status": "saved", "diagnosis": diag.name, "code": diag.icd10_code}


def _handle_add_medication(args: dict) -> dict:
    med = Medication(
        name=args["name"],
        dosage=args["dosage"],
        frequency=args["frequency"],
        route=args.get("route", "oral"),
        notes=args.get("notes", ""),
    )
    try:
        db_add_medication(args["patient_id"], med)
    except ValueError:
        return {"error": "Пациент не найден"}
    return {"status": "saved", "medication": med.name}


def _handle_lab_reference(test_name: str) -> dict:
    if test_name == "all":
        return {k: v for k, v in LAB_REFERENCE_RANGES.items()}
    result = {}
    for key, ref in LAB_REFERENCE_RANGES.items():
        if test_name.lower() in key.lower() or test_name.lower() in ref["name"].lower():
            result[key] = ref
    if not result:
        return {"error": f"Тест '{test_name}' не найден", "available": list(LAB_REFERENCE_RANGES.keys())[:20]}
    return result


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

async def run():
    init_db()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
