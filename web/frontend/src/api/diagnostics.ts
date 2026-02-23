import api from './client';

// ─── Frontend types (normalized) ─────────────────────────────────────────────
export interface LabInput { test: string; value: number }

export interface LabAnalysisResult {
  test: string; value: number; status: string; interpretation: string; unit?: string;
}
export interface LabAnalysisResponse {
  results: LabAnalysisResult[]; summary: string; critical_flags: string[]; patterns: string[];
}

export interface VitalsAssessResponse {
  overall_status: string;
  findings: Array<{ parameter: string; value: number | string; status: string; message: string }>;
  recommendations: string[]; emergency_flags: string[];
}

export interface GfrResponse {
  gfr: number; stage: string; stage_number: number; description: string; recommendations: string[];
}

export interface CvRiskResponse {
  risk_percent: number; risk_category: string; risk_level: string;
  contributing_factors: string[]; recommendations: string[];
}

// ─── Normalizers ─────────────────────────────────────────────────────────────
function normalizeLabs(raw: {
  interpretations?: Array<{ test_name: string; value: number; unit: string; status: string; severity: string }>;
  patterns_detected?: string[]; summary?: string;
}): LabAnalysisResponse {
  const interps = raw.interpretations ?? [];
  return {
    results: interps.map(i => ({
      test: i.test_name, value: i.value, unit: i.unit,
      status: i.status === 'normal' ? 'Норма' : i.status === 'high' ? 'Повышен' : i.status === 'low' ? 'Понижен' : i.status,
      interpretation: i.severity === 'critical' ? '⚠️ Критическое отклонение' :
        i.severity === 'significant' ? '⚠️ Значительное отклонение' :
        i.severity === 'mild' ? 'Незначительное отклонение' :
        i.status !== 'normal' ? 'Требует внимания' : 'В пределах нормы',
    })),
    summary: raw.summary ?? '',
    critical_flags: interps.filter(i => i.severity === 'critical').map(i => `${i.test_name}: ${i.value} ${i.unit}`),
    patterns: raw.patterns_detected ?? [],
  };
}

const PARAM_LABELS: Record<string, string> = {
  systolic_bp: 'АД систолическое', diastolic_bp: 'АД диастолическое',
  heart_rate: 'ЧСС', temperature: 'Температура',
  spo2: 'SpO₂', respiratory_rate: 'ЧД', blood_glucose: 'Глюкоза',
};

function normalizeVitals(raw: {
  alerts?: string[]; severity?: string; values?: Record<string, number | null>;
}): VitalsAssessResponse {
  const values = raw.values ?? {};
  const alerts = raw.alerts ?? [];
  const severity = raw.severity ?? 'normal';

  const findings = Object.entries(values)
    .filter(([, v]) => v !== null && v !== undefined)
    .map(([key, val]) => {
      const alertMsg = alerts.find(a =>
        (key === 'systolic_bp' && (a.includes('Гипертен') || a.includes('систолическое'))) ||
        (key === 'heart_rate' && (a.includes('Тахикард') || a.includes('Брадикард') || a.includes('ЧСС'))) ||
        (key === 'temperature' && (a.includes('Лихорад') || a.includes('°C'))) ||
        (key === 'spo2' && (a.includes('Гипоксем') || a.includes('SpO2')))
      );
      return {
        parameter: PARAM_LABELS[key] ?? key, value: val as number,
        status: alertMsg ? (a => a.includes('КРИТИЧНО') ? 'Критично' : 'Внимание')(alertMsg) : 'Норма',
        message: alertMsg ?? '',
      };
    });

  const emergency = alerts.filter(a => a.startsWith('КРИТИЧНО'));
  return {
    overall_status: severity === 'critical' ? 'Критическое состояние' :
      severity === 'warning' ? 'Внимание' :
      severity === 'attention' ? 'Обратите внимание' : 'Норма',
    findings,
    emergency_flags: emergency,
    recommendations: emergency.length > 0 ? ['Требуется экстренная медицинская помощь'] :
      severity === 'warning' ? ['Рекомендуется консультация врача'] : ['Витальные показатели в норме'],
  };
}

function normalizeGfr(raw: { gfr: number; stage: string; recommendation?: string }): GfrResponse {
  const m = raw.stage?.match(/G(\d)/);
  return {
    gfr: raw.gfr, stage: raw.stage,
    stage_number: m ? parseInt(m[1]) : 1,
    description: '',
    recommendations: raw.recommendation ? [raw.recommendation] : [],
  };
}

function normalizeCvRisk(raw: {
  ten_year_risk_percent?: number; category?: string; color?: string; recommendations?: string[];
}): CvRiskResponse {
  const level = raw.color === 'green' ? 'Низкий' : raw.color === 'yellow' ? 'Умеренный' :
    raw.color === 'orange' ? 'Высокий' : raw.color === 'red' ? 'Очень высокий' : '';
  return {
    risk_percent: raw.ten_year_risk_percent ?? 0,
    risk_category: raw.category ?? '', risk_level: level,
    contributing_factors: [], recommendations: raw.recommendations ?? [],
  };
}

// ─── API calls ────────────────────────────────────────────────────────────────
export const analyzeLabs = (results: LabInput[], gender?: string) =>
  api.post('/diagnostics/analyze-labs', { results, gender }).then(r => normalizeLabs(r.data));

export const assessVitals = (data: Record<string, number>) =>
  api.post('/diagnostics/assess-vitals', data).then(r => normalizeVitals(r.data));

export const calculateGfr = (creatinine: number, age: number, gender: string) =>
  api.post('/diagnostics/calculate-gfr', { creatinine, age, gender }).then(r => normalizeGfr(r.data));

export const calculateCvRisk = (data: Record<string, unknown>) =>
  api.post('/diagnostics/cardiovascular-risk', data).then(r => normalizeCvRisk(r.data));
