"""Diagnostic tools - lab analysis, vitals monitoring, clinical calculators."""
from __future__ import annotations
import math
from typing import Any

from ..models.medical_refs import LAB_REFERENCE_RANGES, interpret_lab_value, DRUG_INTERACTIONS_CRITICAL


def analyze_lab_results(results: list[dict], gender: str = "male") -> dict[str, Any]:
    """Analyze a panel of lab results and provide interpretation.

    Args:
        results: List of {"test": "glucose_fasting", "value": 6.2}
        gender: "male" or "female" for gender-specific ranges
    """
    interpretations = []
    abnormal_count = 0
    critical_count = 0
    patterns = []

    for r in results:
        test_key = r["test"]
        value = r["value"]

        # Try gender-specific key first
        gender_key = f"{test_key}_{gender}"
        if gender_key in LAB_REFERENCE_RANGES:
            test_key = gender_key

        interp = interpret_lab_value(test_key, value)
        interpretations.append(interp)

        if interp["status"] != "normal":
            abnormal_count += 1
        if interp["severity"] == "critical":
            critical_count += 1

    # Pattern detection
    test_map = {r["test"]: r["value"] for r in results}

    # Anemia pattern
    hb_key = f"hemoglobin_{gender}"
    if test_map.get("hemoglobin", 0) or test_map.get(hb_key, 0):
        hb = test_map.get("hemoglobin", test_map.get(hb_key, 999))
        ref = LAB_REFERENCE_RANGES.get(hb_key, {})
        if ref and hb < ref.get("min", 0):
            iron = test_map.get("iron", test_map.get(f"iron_{gender}"))
            ferritin = test_map.get("ferritin", test_map.get(f"ferritin_{gender}"))
            mcv = test_map.get("mcv")

            if mcv and mcv < 80:
                if iron and iron < 9:
                    patterns.append("Железодефицитная анемия (↓Hb, ↓MCV, ↓Fe)")
                else:
                    patterns.append("Микроцитарная анемия (↓Hb, ↓MCV) — дифференцировать талассемию, ЖДА, хр.заболевание")
            elif mcv and mcv > 100:
                patterns.append("Макроцитарная анемия (↓Hb, ↑MCV) — проверить B12, фолаты")
            else:
                patterns.append("Нормоцитарная анемия — проверить ретикулоциты, ферритин, СРБ")

    # Liver damage pattern
    alt_val = test_map.get("alt")
    ast_val = test_map.get("ast")
    if alt_val and ast_val:
        alt_ref = LAB_REFERENCE_RANGES["alt"]["max"]
        ast_ref = LAB_REFERENCE_RANGES["ast"]["max"]
        if alt_val > alt_ref and ast_val > ast_ref:
            ratio = ast_val / alt_val if alt_val > 0 else 0
            if ratio > 2:
                patterns.append(f"Цитолиз с АСТ/АЛТ={ratio:.1f} — характерно для алкогольного поражения печени")
            elif alt_val > 10 * alt_ref:
                patterns.append("Выраженный цитолиз (АЛТ >10N) — острый гепатит, токсическое поражение")
            else:
                patterns.append("Цитолитический синдром (↑АЛТ, ↑АСТ)")

    # Kidney damage pattern
    creat = test_map.get("creatinine", test_map.get(f"creatinine_{gender}"))
    urea = test_map.get("urea")
    if creat and urea:
        creat_ref = LAB_REFERENCE_RANGES.get(f"creatinine_{gender}", {})
        if creat_ref and creat > creat_ref.get("max", 999):
            patterns.append("Нарушение функции почек (↑креатинин, ↑мочевина) — рассчитать СКФ")

    # Inflammation pattern
    crp_val = test_map.get("crp")
    wbc = test_map.get("leukocytes")
    esr = test_map.get("esr", test_map.get(f"esr_{gender}"))
    if crp_val and crp_val > 5:
        if wbc and wbc > 9:
            patterns.append("Воспалительный синдром (↑СРБ, ↑лейкоциты) — бактериальная инфекция?")
        else:
            patterns.append("Повышение СРБ без лейкоцитоза — вирусная инфекция? аутоиммунное?")

    # DIC pattern
    dd = test_map.get("d_dimer")
    fib = test_map.get("fibrinogen")
    plt = test_map.get("platelets")
    if dd and dd > 0.5 and fib and plt:
        if fib < 2 and plt < 150:
            patterns.append("КРИТИЧНО: Подозрение на ДВС-синдром (↑D-димер, ↓фибриноген, ↓тромбоциты)")

    # Diabetes
    glucose = test_map.get("glucose_fasting")
    hba1c = test_map.get("hba1c")
    if glucose and glucose >= 7.0:
        patterns.append("Гипергликемия натощак ≥7.0 — диагностический критерий сахарного диабета")
    elif glucose and glucose >= 5.6:
        patterns.append("Нарушение гликемии натощак (5.6–6.9) — преддиабет")
    if hba1c and hba1c >= 6.5:
        patterns.append(f"HbA1c {hba1c}% ≥6.5% — диагностический критерий сахарного диабета")
    elif hba1c and hba1c >= 5.7:
        patterns.append(f"HbA1c {hba1c}% (5.7–6.4%) — преддиабет")

    # Thyroid
    tsh = test_map.get("tsh")
    ft4 = test_map.get("free_t4")
    if tsh:
        if tsh > 4.0:
            if ft4 and ft4 < 9.0:
                patterns.append("Первичный гипотиреоз (↑ТТГ, ↓свТ4)")
            else:
                patterns.append("Субклинический гипотиреоз (↑ТТГ, нормальный свТ4)")
        elif tsh < 0.4:
            if ft4 and ft4 > 22:
                patterns.append("Тиреотоксикоз (↓ТТГ, ↑свТ4)")
            else:
                patterns.append("Субклинический тиреотоксикоз (↓ТТГ, нормальный свТ4)")

    return {
        "interpretations": interpretations,
        "abnormal_count": abnormal_count,
        "critical_count": critical_count,
        "total_tests": len(results),
        "patterns_detected": patterns,
        "summary": _build_lab_summary(interpretations, patterns, critical_count),
    }


def _build_lab_summary(interpretations: list, patterns: list, critical: int) -> str:
    parts = []
    if critical > 0:
        parts.append(f"⚠️ КРИТИЧЕСКИЕ ОТКЛОНЕНИЯ: {critical}")
    abnormal = [i for i in interpretations if i["status"] != "normal" and i.get("test_name")]
    if abnormal:
        parts.append("Отклонения от нормы:")
        for a in abnormal:
            arrow = "↑" if a["status"] == "high" else "↓"
            parts.append(f"  {arrow} {a['test_name']}: {a['value']} {a['unit']} (норма {a['reference']})")
    if patterns:
        parts.append("\nВыявленные паттерны:")
        for p in patterns:
            parts.append(f"  • {p}")
    if not abnormal and not patterns:
        parts.append("Все показатели в пределах нормы.")
    return "\n".join(parts)


def calculate_gfr(creatinine: float, age: int, gender: str, race: str = "other") -> dict:
    """Calculate eGFR using CKD-EPI 2021 formula (without race coefficient)."""
    # CKD-EPI 2021 (race-free)
    if gender == "female":
        if creatinine <= 0.7 * 88.4:  # convert µmol/L conceptually
            cr_mg = creatinine / 88.4
        else:
            cr_mg = creatinine / 88.4
        kappa = 0.7
        alpha = -0.241 if cr_mg <= kappa else -1.2
        gfr = 142 * (min(cr_mg / kappa, 1) ** alpha) * (max(cr_mg / kappa, 1) ** -1.2) * (0.9938 ** age) * 1.012
    else:
        cr_mg = creatinine / 88.4
        kappa = 0.9
        alpha = -0.302 if cr_mg <= kappa else -1.2
        gfr = 142 * (min(cr_mg / kappa, 1) ** alpha) * (max(cr_mg / kappa, 1) ** -1.2) * (0.9938 ** age)

    gfr = round(gfr, 1)

    # CKD staging
    if gfr >= 90:
        stage = "G1 — нормальная или высокая СКФ"
    elif gfr >= 60:
        stage = "G2 — незначительно снижена"
    elif gfr >= 45:
        stage = "G3a — умеренно снижена"
    elif gfr >= 30:
        stage = "G3b — существенно снижена"
    elif gfr >= 15:
        stage = "G4 — резко снижена"
    else:
        stage = "G5 — терминальная почечная недостаточность"

    return {
        "gfr": gfr,
        "unit": "мл/мин/1.73м²",
        "stage": stage,
        "creatinine_mg_dl": round(cr_mg, 2),
        "recommendation": _gfr_recommendation(gfr),
    }


def _gfr_recommendation(gfr: float) -> str:
    if gfr >= 90:
        return "Мониторинг при наличии факторов риска ХБП"
    elif gfr >= 60:
        return "Контроль СКФ каждые 12 мес, коррекция факторов риска"
    elif gfr >= 45:
        return "Контроль СКФ каждые 6 мес, нефропротекция, коррекция дозировок"
    elif gfr >= 30:
        return "Контроль каждые 3 мес, нефролог, подготовка к ЗПТ при прогрессировании"
    elif gfr >= 15:
        return "Наблюдение нефролога, подготовка к диализу/трансплантации"
    else:
        return "КРИТИЧНО: Показана заместительная почечная терапия (диализ/трансплантация)"


def calculate_cardiovascular_risk(
    age: int, gender: str, systolic_bp: int,
    total_cholesterol: float, hdl: float,
    smoker: bool = False, diabetic: bool = False,
    on_bp_treatment: bool = False,
) -> dict:
    """Simplified cardiovascular risk estimation (Framingham-like)."""
    risk_points = 0

    # Age points
    if gender == "male":
        if age < 35: risk_points += 0
        elif age < 40: risk_points += 2
        elif age < 45: risk_points += 5
        elif age < 50: risk_points += 7
        elif age < 55: risk_points += 8
        elif age < 60: risk_points += 10
        elif age < 65: risk_points += 11
        elif age < 70: risk_points += 12
        else: risk_points += 13
    else:
        if age < 35: risk_points += 0
        elif age < 40: risk_points += 2
        elif age < 45: risk_points += 4
        elif age < 50: risk_points += 5
        elif age < 55: risk_points += 7
        elif age < 60: risk_points += 8
        elif age < 65: risk_points += 9
        elif age < 70: risk_points += 10
        else: risk_points += 11

    # Cholesterol
    if total_cholesterol > 7.2: risk_points += 3
    elif total_cholesterol > 6.2: risk_points += 2
    elif total_cholesterol > 5.2: risk_points += 1

    # HDL
    if hdl < 1.0: risk_points += 2
    elif hdl < 1.3: risk_points += 1
    elif hdl > 1.6: risk_points -= 1

    # BP
    if on_bp_treatment:
        if systolic_bp >= 160: risk_points += 3
        elif systolic_bp >= 140: risk_points += 2
        elif systolic_bp >= 130: risk_points += 1
    else:
        if systolic_bp >= 160: risk_points += 2
        elif systolic_bp >= 140: risk_points += 1

    if smoker: risk_points += 3
    if diabetic: risk_points += 3

    # Convert to approximate 10-year risk percentage
    risk_percent = min(max(risk_points * 1.5, 1), 50)

    if risk_percent < 5:
        category = "Низкий риск"
        color = "green"
    elif risk_percent < 10:
        category = "Умеренный риск"
        color = "yellow"
    elif risk_percent < 20:
        category = "Высокий риск"
        color = "orange"
    else:
        category = "Очень высокий риск"
        color = "red"

    recommendations = []
    if smoker:
        recommendations.append("Отказ от курения — первоочередная мера")
    if total_cholesterol > 5.2:
        recommendations.append("Контроль липидного спектра, рассмотреть статины")
    if systolic_bp > 140:
        recommendations.append("Коррекция артериального давления")
    if diabetic:
        recommendations.append("Строгий контроль гликемии (HbA1c <7%)")
    if hdl < 1.0:
        recommendations.append("Повышение физической активности для повышения ЛПВП")

    return {
        "risk_points": risk_points,
        "ten_year_risk_percent": round(risk_percent, 1),
        "category": category,
        "color": color,
        "recommendations": recommendations,
    }


def check_drug_interactions_local(drugs: list[str]) -> list[dict]:
    """Check drug interactions using local critical interaction database."""
    interactions_found = []
    drugs_lower = [d.lower() for d in drugs]

    for i, d1 in enumerate(drugs_lower):
        for d2 in drugs_lower[i + 1:]:
            for (k1, k2), warning in DRUG_INTERACTIONS_CRITICAL.items():
                if (k1 in d1 and k2 in d2) or (k2 in d1 and k1 in d2):
                    interactions_found.append({
                        "drug1": drugs[i],
                        "drug2": drugs[drugs_lower.index(d2)],
                        "warning": warning,
                        "severity": "critical",
                    })

    return interactions_found


def assess_vitals(
    systolic_bp: int | None = None,
    diastolic_bp: int | None = None,
    heart_rate: int | None = None,
    temperature: float | None = None,
    spo2: float | None = None,
    respiratory_rate: int | None = None,
    blood_glucose: float | None = None,
) -> dict:
    """Assess vital signs and return alerts."""
    from ..models.patient import VitalSigns
    v = VitalSigns(
        systolic_bp=systolic_bp, diastolic_bp=diastolic_bp,
        heart_rate=heart_rate, temperature=temperature,
        spo2=spo2, respiratory_rate=respiratory_rate,
        blood_glucose=blood_glucose,
    )
    alerts = v.assess()
    map_p = v.map_pressure()

    severity = "normal"
    if any("КРИТИЧНО" in a for a in alerts):
        severity = "critical"
    elif len(alerts) > 2:
        severity = "warning"
    elif alerts:
        severity = "attention"

    return {
        "alerts": alerts,
        "severity": severity,
        "mean_arterial_pressure": map_p,
        "values": {
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "heart_rate": heart_rate,
            "temperature": temperature,
            "spo2": spo2,
            "respiratory_rate": respiratory_rate,
            "blood_glucose": blood_glucose,
        },
    }
