export const COMMON_LABS: { code: string; label: string; unit: string; normM: string; normF: string }[] = [
  { code: 'hemoglobin',        label: 'Гемоглобин',       unit: 'г/л',      normM: '130–170', normF: '120–150' },
  { code: 'glucose_fasting',   label: 'Глюкоза натощак',  unit: 'ммоль/л',  normM: '3.9–6.1', normF: '3.9–6.1' },
  { code: 'alt',               label: 'АЛТ',              unit: 'Ед/л',     normM: '≤41',     normF: '≤31' },
  { code: 'ast',               label: 'АСТ',              unit: 'Ед/л',     normM: '≤40',     normF: '≤35' },
  { code: 'creatinine',        label: 'Креатинин',        unit: 'мкмоль/л', normM: '62–115',  normF: '44–97' },
  { code: 'total_cholesterol', label: 'Холестерин общий', unit: 'ммоль/л',  normM: '3.0–5.2', normF: '3.0–5.2' },
  { code: 'tsh',               label: 'ТТГ',              unit: 'мкМЕ/мл',  normM: '0.4–4.0', normF: '0.4–4.0' },
  { code: 'hba1c',             label: 'HbA1c',            unit: '%',        normM: '<6.0',    normF: '<6.0' },
];

export const VITALS_FIELDS: { key: string; label: string; unit: string; norm: string; example: string }[] = [
  { key: 'systolic_bp',      label: 'АД систолическое', unit: 'мм рт.ст.', norm: '90–130',   example: '120' },
  { key: 'diastolic_bp',     label: 'АД диастолическое', unit: 'мм рт.ст.', norm: '60–85',   example: '80' },
  { key: 'heart_rate',       label: 'ЧСС',              unit: 'уд/мин',    norm: '60–100',   example: '72' },
  { key: 'temperature',      label: 'Температура',      unit: '°C',        norm: '36.0–37.0', example: '36.6' },
  { key: 'spo2',             label: 'SpO₂',             unit: '%',         norm: '95–100',   example: '98' },
  { key: 'respiratory_rate', label: 'ЧД',               unit: '/мин',      norm: '12–20',    example: '16' },
  { key: 'blood_glucose',    label: 'Глюкоза',          unit: 'ммоль/л',   norm: '3.9–6.1',  example: '5.2' },
];

export const CKD_COLORS = ['#10b981', '#84cc16', '#f59e0b', '#f97316', '#dc2626', '#7f1d1d'];

export const CKD_STAGES = [
  { stage: 'G1', range: '≥ 90', label: 'Норма или высокая СКФ' },
  { stage: 'G2', range: '60–89', label: 'Лёгкое снижение' },
  { stage: 'G3a', range: '45–59', label: 'Умеренное снижение' },
  { stage: 'G3b', range: '30–44', label: 'Значимое снижение' },
  { stage: 'G4', range: '15–29', label: 'Выраженное снижение' },
  { stage: 'G5', range: '< 15', label: 'Почечная недостаточность' },
];

export const VITALS_THRESHOLDS = {
  bp: { warning: 140, danger: 180 },
  hr: { lowDanger: 50, lowWarning: 60, highWarning: 100, highDanger: 120 },
  temp: { warning: 37.5 },
  spo2: { danger: 95 },
} as const;
