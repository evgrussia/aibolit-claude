import { useState, useCallback } from 'react';
import { Droplets } from 'lucide-react';
import Card from '../shared/Card.tsx';
import InfoBanner from '../shared/InfoBanner.tsx';
import HelpTooltip from '../shared/HelpTooltip.tsx';
import MedicalDisclaimer from '../shared/MedicalDisclaimer.tsx';
import { CKD_COLORS, CKD_STAGES } from '../../constants/medical.ts';
import { calculateGfr, type GfrResponse } from '../../api/diagnostics.ts';

export default function GfrCalculatorTab() {
  const [creatinine, setCreatinine] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('male');
  const [result, setResult] = useState<GfrResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = useCallback(async () => {
    if (!creatinine || !age) { setError('Заполните все поля'); return; }
    setLoading(true); setError('');
    try { setResult(await calculateGfr(Number(creatinine), Number(age), gender)); }
    catch { setError('Ошибка расчёта. Проверьте подключение к серверу.'); }
    finally { setLoading(false); }
  }, [creatinine, age, gender]);

  const color = result ? CKD_COLORS[Math.min((result.stage_number ?? 1) - 1, 5)] : '#10b981';

  return (
    <div className="space-y-4">
      <InfoBanner variant="info" title="О расчёте СКФ" collapsible defaultOpen>
        <p className="mb-2">
          СКФ (скорость клубочковой фильтрации) — основной показатель функции почек.
          Рассчитывается по формуле <strong>CKD-EPI 2021</strong> на основе уровня креатинина,
          возраста и пола.
        </p>
        <div className="grid grid-cols-3 gap-1 mt-2">
          {CKD_STAGES.map((s, i) => (
            <div key={s.stage} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full shrink-0" style={{ background: CKD_COLORS[i] }} />
              <span><strong>{s.stage}</strong> ({s.range}): {s.label}</span>
            </div>
          ))}
        </div>
      </InfoBanner>

      <Card title="Расчёт скорости клубочковой фильтрации (CKD-EPI)" icon={<Droplets size={16} />}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label htmlFor="gfr-creatinine" className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              Креатинин (мкмоль/л)
              <HelpTooltip text="Норма: мужчины 62–115, женщины 44–97 мкмоль/л. Повышение может указывать на снижение функции почек." />
            </label>
            <input id="gfr-creatinine" type="number" min="0" value={creatinine} onChange={e => setCreatinine(e.target.value)}
              placeholder="например: 92"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
          <div>
            <label htmlFor="gfr-age" className="block text-xs text-gray-500 mb-1">Возраст (лет)</label>
            <input id="gfr-age" type="number" min="0" max="150" value={age} onChange={e => setAge(e.target.value)}
              placeholder="например: 39"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
          <div>
            <label htmlFor="gfr-gender" className="block text-xs text-gray-500 mb-1">Пол</label>
            <select id="gfr-gender" value={gender} onChange={e => setGender(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal">
              <option value="male">Мужской</option>
              <option value="female">Женский</option>
            </select>
          </div>
        </div>
        {error && <p role="alert" className="text-red-500 text-sm mb-3">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}
          className="bg-medical-teal text-white px-6 py-2 rounded-lg hover:bg-medical-navy transition-colors disabled:opacity-50">
          {loading ? 'Рассчитываю...' : 'Рассчитать СКФ'}
        </button>
      </Card>

      {result && (
        <>
          <Card title="Результат">
            <div className="flex items-center gap-8">
              <div className="text-center">
                <div className="text-5xl font-bold" style={{ color }}>{result.gfr}</div>
                <div className="text-sm text-gray-500 mt-1">мл/мин/1.73м²</div>
              </div>
              <div>
                <div className="text-xl font-semibold text-gray-800 mb-1">{result.stage}</div>
                <div className="text-gray-600 mb-3">{result.description}</div>
                {result.recommendations?.length > 0 && (
                  <ul className="space-y-1">
                    {result.recommendations.map((r, i) => <li key={i} className="text-sm text-blue-700">{r}</li>)}
                  </ul>
                )}
              </div>
            </div>
          </Card>
          <MedicalDisclaimer type="lab_analysis" />
        </>
      )}
    </div>
  );
}
