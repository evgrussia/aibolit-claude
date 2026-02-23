import { useState, useCallback, useMemo } from 'react';
import { TrendingUp } from 'lucide-react';
import Card from '../shared/Card.tsx';
import Badge from '../shared/Badge.tsx';
import InfoBanner from '../shared/InfoBanner.tsx';
import HelpTooltip from '../shared/HelpTooltip.tsx';
import MedicalDisclaimer from '../shared/MedicalDisclaimer.tsx';
import { calculateCvRisk, type CvRiskResponse } from '../../api/diagnostics.ts';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export default function CvRiskTab() {
  const [form, setForm] = useState<Record<string, string | boolean>>({
    gender: 'male', smoker: false, diabetic: false, on_bp_treatment: false,
  });
  const [result, setResult] = useState<CvRiskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const set = (key: string, val: string | boolean) => setForm(f => ({ ...f, [key]: val }));

  const handleSubmit = useCallback(async () => {
    const required = ['age', 'systolic_bp', 'total_cholesterol', 'hdl'];
    for (const k of required) if (!form[k]) { setError(`Заполните поле: ${k}`); return; }
    setLoading(true); setError('');
    try {
      setResult(await calculateCvRisk({
        age: Number(form.age), gender: form.gender as string,
        systolic_bp: Number(form.systolic_bp),
        total_cholesterol: Number(form.total_cholesterol),
        hdl: Number(form.hdl),
        smoker: Boolean(form.smoker), diabetic: Boolean(form.diabetic),
        on_bp_treatment: Boolean(form.on_bp_treatment),
      }));
    } catch { setError('Ошибка расчёта. Проверьте подключение к серверу.'); }
    finally { setLoading(false); }
  }, [form]);

  const riskColor = result
    ? result.risk_percent < 5 ? '#10b981' : result.risk_percent < 10 ? '#f59e0b' : '#dc2626'
    : '#10b981';

  const chartData = useMemo(() => result ? [
    { name: 'Риск', value: Math.min(result.risk_percent, 100) },
    { name: 'Норма', value: Math.max(100 - result.risk_percent, 0) },
  ] : [], [result]);

  return (
    <div className="space-y-4">
      <InfoBanner variant="info" title="О шкале СС-риска SCORE2" collapsible defaultOpen>
        <p className="mb-2">
          Рассчитывает вероятность фатального сердечно-сосудистого события
          (инфаркт, инсульт) в течение <strong>10 лет</strong>.
          Основан на европейской модели SCORE2.
        </p>
        <div className="grid grid-cols-3 gap-2 mt-2">
          <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-emerald-500" /><span><strong>&lt;5%</strong> — Низкий</span></div>
          <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-amber-500" /><span><strong>5–9%</strong> — Умеренный</span></div>
          <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-red-500" /><span><strong>≥10%</strong> — Высокий</span></div>
        </div>
        <p className="mt-2">
          Нормальные значения: холестерин 3.0–5.2 ммоль/л, ЛПВП: м &gt;1.0 / ж &gt;1.2 ммоль/л.
        </p>
      </InfoBanner>

      <Card title="Оценка 10-летнего сердечно-сосудистого риска" icon={<TrendingUp size={16} />}>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
          {[
            { key: 'age', label: 'Возраст', unit: 'лет', placeholder: '45', tooltip: 'Риск резко возрастает после 50 лет' },
            { key: 'systolic_bp', label: 'АД систолическое', unit: 'мм рт.ст.', placeholder: '130', tooltip: 'Целевое: <130 мм рт.ст. При лечении АД — отметьте соответствующий флажок' },
            { key: 'total_cholesterol', label: 'Холестерин общий', unit: 'ммоль/л', placeholder: '5.0', tooltip: 'Норма: 3.0–5.2 ммоль/л. Целевой при высоком риске: <4.5 ммоль/л' },
            { key: 'hdl', label: 'ЛПВП', unit: 'ммоль/л', placeholder: '1.2', tooltip: '"Хороший" холестерин. Норма: м >1.0, ж >1.2 ммоль/л. Чем выше — тем лучше' },
          ].map(f => {
            const inputId = `cvrisk-${f.key}`;
            return (
              <div key={f.key}>
                <label htmlFor={inputId} className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                  {f.label}
                  <span className="text-gray-400">({f.unit})</span>
                  <HelpTooltip text={f.tooltip} />
                </label>
                <input id={inputId} type="number" value={(form[f.key] as string) ?? ''}
                  onChange={e => set(f.key, e.target.value)}
                  placeholder={f.placeholder}
                  min={f.key === 'age' ? '0' : undefined}
                  max={f.key === 'age' ? '150' : undefined}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
              </div>
            );
          })}
          <div>
            <label htmlFor="cvrisk-gender" className="block text-xs text-gray-500 mb-1">Пол</label>
            <select id="cvrisk-gender" value={form.gender as string} onChange={e => set('gender', e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal">
              <option value="male">Мужской</option>
              <option value="female">Женский</option>
            </select>
          </div>
        </div>
        <div className="flex gap-6 mb-4">
          {[
            { key: 'smoker', label: 'Курение', tooltip: 'Курение увеличивает риск в 2–4 раза' },
            { key: 'diabetic', label: 'Сахарный диабет', tooltip: 'СД 2 типа — независимый фактор риска, приравнивается к уже перенесённому ИМ' },
            { key: 'on_bp_treatment', label: 'Лечение АД', tooltip: 'Отметьте, если пациент принимает антигипертензивные препараты — это учитывается в расчёте' },
          ].map(f => (
            <label key={f.key} className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={Boolean(form[f.key])}
                onChange={e => set(f.key, e.target.checked)}
                className="w-4 h-4 accent-medical-teal" />
              <span className="text-sm text-gray-700">{f.label}</span>
              <HelpTooltip text={f.tooltip} />
            </label>
          ))}
        </div>
        {error && <p role="alert" className="text-red-500 text-sm mb-3">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}
          className="bg-medical-teal text-white px-6 py-2 rounded-lg hover:bg-medical-navy transition-colors disabled:opacity-50">
          {loading ? 'Рассчитываю...' : 'Рассчитать риск'}
        </button>
      </Card>

      {result && (
        <>
          <Card title="Результат">
            <div className="flex flex-col md:flex-row items-center gap-8">
              <div style={{ width: 180, height: 180 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={chartData} cx="50%" cy="50%" innerRadius={55} outerRadius={80}
                      dataKey="value" startAngle={90} endAngle={-270}>
                      <Cell fill={riskColor} />
                      <Cell fill="#f1f5f9" />
                    </Pie>
                    <Tooltip formatter={(v: unknown) => `${Number(v).toFixed(1)}%`} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="text-center -mt-20">
                  <div className="text-3xl font-bold" style={{ color: riskColor }}>
                    {result.risk_percent?.toFixed(1)}%
                  </div>
                </div>
              </div>
              <div className="flex-1">
                <div className="text-xl font-semibold text-gray-800 mb-1">{result.risk_category}</div>
                <div className="text-gray-500 mb-3">{result.risk_level}</div>
                {result.contributing_factors?.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium text-gray-700 mb-1">Факторы риска:</p>
                    <div className="flex flex-wrap gap-1">
                      {result.contributing_factors.map((f, i) => <Badge key={i} variant="warning">{f}</Badge>)}
                    </div>
                  </div>
                )}
                {result.recommendations?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Рекомендации:</p>
                    {result.recommendations.map((r, i) => <p key={i} className="text-sm text-blue-700">{r}</p>)}
                  </div>
                )}
              </div>
            </div>
          </Card>
          <MedicalDisclaimer type="diagnosis" />
        </>
      )}
    </div>
  );
}
