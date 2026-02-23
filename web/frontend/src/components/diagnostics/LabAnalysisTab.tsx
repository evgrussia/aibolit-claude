import { useState, useCallback } from 'react';
import { FlaskConical } from 'lucide-react';
import Card from '../shared/Card.tsx';
import InfoBanner from '../shared/InfoBanner.tsx';
import HelpTooltip from '../shared/HelpTooltip.tsx';
import MedicalDisclaimer from '../shared/MedicalDisclaimer.tsx';
import { statusBadge } from './statusBadge.tsx';
import { COMMON_LABS } from '../../constants/medical.ts';
import { analyzeLabs, type LabInput, type LabAnalysisResponse } from '../../api/diagnostics.ts';

export default function LabAnalysisTab() {
  const [values, setValues] = useState<Record<string, string>>({});
  const [gender, setGender] = useState('male');
  const [result, setResult] = useState<LabAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = useCallback(async () => {
    const inputs: LabInput[] = COMMON_LABS
      .filter(l => values[l.code] && !isNaN(Number(values[l.code])))
      .map(l => ({ test: l.code, value: Number(values[l.code]) }));
    if (inputs.length === 0) { setError('Введите хотя бы один показатель'); return; }
    setLoading(true); setError('');
    try {
      setResult(await analyzeLabs(inputs, gender));
    } catch { setError('Ошибка анализа. Проверьте подключение к серверу.'); }
    finally { setLoading(false); }
  }, [values, gender]);

  return (
    <div className="space-y-4">
      <InfoBanner variant="info" title="Как пользоваться анализатором" collapsible defaultOpen>
        <p className="mb-2">
          Введите числовые значения из лабораторных результатов в соответствующие поля.
          Можно заполнить один или несколько показателей — незаполненные поля игнорируются.
        </p>
        <p className="mb-2">
          Система поддерживает <strong>67 лабораторных показателей</strong> (ОАК, биохимия, гормоны, онкомаркёры).
          На этой странице доступны 8 наиболее распространённых.
        </p>
        <p>
          <strong>Не вводите</strong> единицы измерения — только числа.
          Норма зависит от пола, поэтому обязательно укажите его.
        </p>
      </InfoBanner>

      <Card title="Введите результаты анализов" icon={<FlaskConical size={16} />}>
        <fieldset>
          <legend className="sr-only">Пол пациента</legend>
          <div className="mb-4">
            <span className="text-sm font-medium text-gray-700 mr-3">Пол:</span>
            {['male', 'female'].map(g => (
              <label key={g} className="mr-4 cursor-pointer">
                <input type="radio" name="lab-gender" value={g} checked={gender === g} onChange={() => setGender(g)} className="mr-1" />
                {g === 'male' ? 'Мужской' : 'Женский'}
              </label>
            ))}
          </div>
        </fieldset>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {COMMON_LABS.map(l => {
            const norm = gender === 'male' ? l.normM : l.normF;
            const inputId = `lab-${l.code}`;
            return (
              <div key={l.code}>
                <label htmlFor={inputId} className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                  {l.label}
                  <span className="text-gray-400">({l.unit})</span>
                  <HelpTooltip text={`Норма: ${norm} ${l.unit}`} />
                </label>
                <input
                  id={inputId}
                  type="number" step="any" min="0"
                  value={values[l.code] ?? ''}
                  onChange={e => setValues(v => ({ ...v, [l.code]: e.target.value }))}
                  placeholder={`норма: ${norm}`}
                  className="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300"
                />
              </div>
            );
          })}
        </div>
        {error && <p role="alert" className="text-red-500 text-sm mb-3">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}
          className="bg-medical-teal text-white px-6 py-2 rounded-lg hover:bg-medical-navy transition-colors disabled:opacity-50">
          {loading ? 'Анализирую...' : 'Анализировать'}
        </button>
      </Card>

      {result && (
      <>
        <Card title="Результаты анализа">
          {result.critical_flags?.length > 0 && (
            <div role="alert" className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
              <p className="text-red-700 font-semibold text-sm mb-1">Критические отклонения:</p>
              {result.critical_flags.map((f, i) => <p key={i} className="text-red-600 text-sm">{f}</p>)}
            </div>
          )}
          {result.patterns?.length > 0 && (
            <div className="mb-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
              <p className="text-amber-700 font-semibold text-sm mb-1">Выявленные паттерны:</p>
              {result.patterns.map((p, i) => <p key={i} className="text-amber-600 text-sm">{p}</p>)}
            </div>
          )}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <caption className="sr-only">Результаты лабораторного анализа</caption>
              <thead>
                <tr className="border-b border-gray-100">
                  <th scope="col" className="text-left py-2 text-gray-500 font-medium">Показатель</th>
                  <th scope="col" className="text-right py-2 text-gray-500 font-medium">Значение</th>
                  <th scope="col" className="text-center py-2 text-gray-500 font-medium">Статус</th>
                  <th scope="col" className="text-left py-2 text-gray-500 font-medium pl-4">Интерпретация</th>
                </tr>
              </thead>
              <tbody>
                {result.results?.map((r, i) => (
                  <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 font-medium text-gray-700">{r.test}</td>
                    <td className="py-2 text-right font-mono">{r.value}</td>
                    <td className="py-2 text-center">{statusBadge(r.status)}</td>
                    <td className="py-2 text-gray-600 text-xs pl-4">{r.interpretation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {result.summary && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
              <strong>Заключение:</strong> {result.summary}
            </div>
          )}
        </Card>
        <MedicalDisclaimer type="lab_analysis" />
      </>
      )}
    </div>
  );
}
