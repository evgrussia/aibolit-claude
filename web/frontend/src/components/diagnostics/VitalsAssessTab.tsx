import { useState, useCallback } from 'react';
import { HeartPulse } from 'lucide-react';
import Card from '../shared/Card.tsx';
import InfoBanner from '../shared/InfoBanner.tsx';
import HelpTooltip from '../shared/HelpTooltip.tsx';
import MedicalDisclaimer from '../shared/MedicalDisclaimer.tsx';
import EmergencyBanner from '../shared/EmergencyBanner.tsx';
import { statusBadge } from './statusBadge.tsx';
import { VITALS_FIELDS } from '../../constants/medical.ts';
import { assessVitals, type VitalsAssessResponse } from '../../api/diagnostics.ts';

export default function VitalsAssessTab() {
  const [form, setForm] = useState<Record<string, string>>({});
  const [result, setResult] = useState<VitalsAssessResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = useCallback(async () => {
    const data: Record<string, number> = {};
    for (const f of VITALS_FIELDS) {
      if (form[f.key] && !isNaN(Number(form[f.key]))) data[f.key] = Number(form[f.key]);
    }
    if (Object.keys(data).length === 0) { setError('Введите хотя бы один показатель'); return; }
    setLoading(true); setError('');
    try { setResult(await assessVitals(data)); }
    catch { setError('Ошибка оценки. Проверьте подключение к серверу.'); }
    finally { setLoading(false); }
  }, [form]);

  return (
    <div className="space-y-4">
      <InfoBanner variant="info" title="О витальных показателях" collapsible defaultOpen>
        <p className="mb-2">
          Введите измеренные показатели. Можно вводить только те, что есть —
          система оценит каждый в отдельности и в совокупности.
        </p>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2 text-xs">
          <span><strong>SpO₂ &lt;90%</strong> — критическая гипоксия</span>
          <span><strong>АД &gt;180/110</strong> — гипертонический криз</span>
          <span><strong>ЧСС &gt;150</strong> — тахиаритмия</span>
          <span><strong>Температура &gt;40°C</strong> — гиперпирексия</span>
        </div>
      </InfoBanner>

      <Card title="Введите витальные показатели" icon={<HeartPulse size={16} />}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {VITALS_FIELDS.map(f => {
            const inputId = `vitals-${f.key}`;
            return (
              <div key={f.key}>
                <label htmlFor={inputId} className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                  {f.label}
                  <span className="text-gray-400">({f.unit})</span>
                  <HelpTooltip text={`Норма: ${f.norm} ${f.unit}`} />
                </label>
                <input
                  id={inputId}
                  type="number" step="any"
                  min={f.key === 'temperature' ? '30' : '0'}
                  max={f.key === 'temperature' ? '45' : f.key === 'spo2' ? '100' : f.key.includes('bp') ? '300' : f.key === 'heart_rate' ? '300' : undefined}
                  value={form[f.key] ?? ''}
                  onChange={e => setForm(v => ({ ...v, [f.key]: e.target.value }))}
                  placeholder={`пример: ${f.example}`}
                  className="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300"
                />
              </div>
            );
          })}
        </div>
        {error && <p role="alert" className="text-red-500 text-sm mb-3">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}
          className="bg-medical-teal text-white px-6 py-2 rounded-lg hover:bg-medical-navy transition-colors disabled:opacity-50">
          {loading ? 'Оцениваю...' : 'Оценить'}
        </button>
      </Card>

      {result && (
        <>
          {result.emergency_flags?.length > 0 && (
            <EmergencyBanner />
          )}
          <Card title="Оценка витальных показателей">
            {result.emergency_flags?.length > 0 && (
              <div role="alert" className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
                <p className="text-red-700 font-semibold text-sm">Требует немедленного внимания:</p>
                {result.emergency_flags.map((f, i) => <p key={i} className="text-red-600 text-sm">{f}</p>)}
              </div>
            )}
            <div className="grid gap-2 mb-4">
              {result.findings?.map((f, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50">
                  <div className="flex-1">
                    <span className="font-medium text-sm text-gray-800">{f.parameter}: </span>
                    <span className="font-mono text-sm">{f.value}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {statusBadge(f.status)}
                    <span className="text-xs text-gray-500">{f.message}</span>
                  </div>
                </div>
              ))}
            </div>
            {result.recommendations?.length > 0 && (
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-sm font-semibold text-blue-800 mb-2">Рекомендации:</p>
                {result.recommendations.map((r, i) => <p key={i} className="text-blue-700 text-sm">{r}</p>)}
              </div>
            )}
          </Card>
          <MedicalDisclaimer type="general" />
        </>
      )}
    </div>
  );
}
