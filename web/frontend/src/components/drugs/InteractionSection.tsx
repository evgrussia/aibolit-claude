import { useState, useCallback } from 'react';
import { AlertTriangle, X, Plus } from 'lucide-react';
import Card from '../shared/Card.tsx';
import Badge from '../shared/Badge.tsx';
import InfoBanner from '../shared/InfoBanner.tsx';
import { CRITICAL_PAIRS } from '../../constants/drugs.ts';
import { checkInteractions, type DrugInteractionResult } from '../../api/drugs.ts';

export default function InteractionSection() {
  const [drugs, setDrugs] = useState<string[]>(['', '']);
  const [result, setResult] = useState<DrugInteractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addDrug = () => setDrugs(d => [...d, '']);
  const removeDrug = (i: number) => setDrugs(d => d.filter((_, idx) => idx !== i));
  const updateDrug = (i: number, val: string) => setDrugs(d => d.map((x, idx) => idx === i ? val : x));

  const handleCheck = useCallback(async () => {
    const filled = drugs.filter(d => d.trim());
    if (filled.length < 2) { setError('Введите минимум 2 препарата'); return; }
    setLoading(true); setError('');
    try { setResult(await checkInteractions(filled)); }
    catch { setError('Ошибка проверки. Проверьте подключение к серверу.'); }
    finally { setLoading(false); }
  }, [drugs]);

  const severityVariant = (s: string) => {
    const sl = s?.toLowerCase();
    if (sl?.includes('critical') || sl?.includes('major') || sl?.includes('серьёз') || sl?.includes('severe')) return 'danger' as const;
    if (sl?.includes('moderate') || sl?.includes('умерен') || sl?.includes('warning')) return 'warning' as const;
    return 'info' as const;
  };

  return (
    <div className="space-y-4">
      <InfoBanner variant="warning" title="Как работает проверка взаимодействий" collapsible defaultOpen>
        <p className="mb-2">
          Система использует <strong>два источника</strong>:
        </p>
        <ol className="list-decimal list-inside space-y-1 mb-2">
          <li>Локальную базу <strong>12 критических пар</strong> (мгновенно)</li>
          <li><strong>RxNorm API</strong> (NLM/NIH) — расширенная база взаимодействий</li>
        </ol>
        <p className="mb-2">
          Вводите <strong>МНН на английском</strong>: warfarin, aspirin, metformin, amiodarone...
        </p>
        <details className="mt-2">
          <summary className="cursor-pointer text-amber-700 font-medium">Известные критические пары</summary>
          <div className="mt-2 space-y-1">
            {CRITICAL_PAIRS.map(p => (
              <div key={p.pair} className="flex gap-2">
                <span className="font-mono text-amber-800">{p.pair}</span>
                <span className="text-amber-600">{p.risk}</span>
              </div>
            ))}
          </div>
        </details>
      </InfoBanner>

      <Card title="Проверка лекарственных взаимодействий" icon={<AlertTriangle size={16} />}>
        <p className="text-xs text-gray-500 mb-3">
          Добавьте все препараты пациента — система проверит все возможные пары.
        </p>
        <div className="space-y-2 mb-4">
          {drugs.map((d, i) => (
            <div key={i} className="flex gap-2">
              <label htmlFor={`drug-${i}`} className="sr-only">Препарат {i + 1}</label>
              <input id={`drug-${i}`} value={d} onChange={e => updateDrug(i, e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleCheck()}
                placeholder={`Препарат ${i + 1}: например warfarin, aspirin...`}
                className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal" />
              {drugs.length > 2 && (
                <button onClick={() => removeDrug(i)} className="text-gray-400 hover:text-red-500 transition-colors" aria-label={`Удалить препарат ${i + 1}`}>
                  <X size={18} />
                </button>
              )}
            </div>
          ))}
        </div>
        <div className="flex gap-3">
          <button onClick={addDrug}
            className="flex items-center gap-1.5 text-medical-teal text-sm hover:text-medical-navy transition-colors">
            <Plus size={16} />Добавить препарат
          </button>
          <button onClick={handleCheck} disabled={loading}
            className="bg-medical-teal text-white px-5 py-2 rounded-lg hover:bg-medical-navy transition-colors flex items-center gap-2 disabled:opacity-50 ml-auto">
            <AlertTriangle size={16} />{loading ? 'Проверяю...' : 'Проверить'}
          </button>
        </div>
        {error && <p role="alert" className="text-red-500 text-sm mt-2">{error}</p>}
      </Card>

      {result && (
        <Card title={`Результат проверки — ${result.checked_pairs} пар${result.checked_pairs === 1 ? 'а' : 'ы'}`}>
          {result.has_interactions ? (
            <div className="space-y-3">
              {result.interactions?.map((inter, i) => (
                <div key={i} className={`p-3 rounded-lg border ${
                  severityVariant(inter.severity) === 'danger' ? 'bg-red-50 border-red-200' :
                  severityVariant(inter.severity) === 'warning' ? 'bg-amber-50 border-amber-200' : 'bg-blue-50 border-blue-200'
                }`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-sm">{inter.drug1} + {inter.drug2}</span>
                    <Badge variant={severityVariant(inter.severity)}>{inter.severity}</Badge>
                  </div>
                  <p className="text-sm text-gray-700">{inter.description}</p>
                </div>
              ))}
              <p className="text-xs text-gray-400 mt-2">
                * Клиническая значимость взаимодействий требует оценки врача с учётом конкретного пациента.
              </p>
            </div>
          ) : (
            <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600">✓</span>
              </div>
              <div>
                <p className="font-semibold text-green-800">Значимых взаимодействий не выявлено</p>
                <p className="text-green-700 text-sm">
                  Для введённых препаратов критических взаимодействий в базе не обнаружено.
                  Это не означает полную безопасность — проконсультируйтесь с врачом.
                </p>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
