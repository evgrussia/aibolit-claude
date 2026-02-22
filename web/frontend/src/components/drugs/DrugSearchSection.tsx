import { useState, useCallback } from 'react';
import { Search, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import Card from '../shared/Card.tsx';
import Badge from '../shared/Badge.tsx';
import InfoBanner from '../shared/InfoBanner.tsx';
import { DRUG_EXAMPLES } from '../../constants/drugs.ts';
import { getDrugInfo, getAdverseEvents, type DrugInfo } from '../../api/drugs.ts';

export default function DrugSearchSection() {
  const [query, setQuery] = useState('');
  const [info, setInfo] = useState<DrugInfo | null>(null);
  const [events, setEvents] = useState<{ reaction: string; count: number }[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showEvents, setShowEvents] = useState(false);

  const handleSearch = useCallback(async (name?: string) => {
    const term = name ?? query.trim();
    if (!term) return;
    if (name) setQuery(name);
    setLoading(true); setError(''); setInfo(null); setEvents(null); setShowEvents(false);
    try {
      const [drugData, eventsData] = await Promise.all([
        getDrugInfo(term),
        getAdverseEvents(term).catch(() => null),
      ]);
      setInfo(drugData);
      if (eventsData?.events) setEvents(eventsData.events);
    } catch {
      setError(`Препарат "${term}" не найден в базе FDA. Попробуйте ввести название на английском.`);
    } finally { setLoading(false); }
  }, [query]);

  return (
    <div className="space-y-4">
      <InfoBanner variant="info" title="Источник данных: OpenFDA (FDA, США)" collapsible defaultOpen>
        <p className="mb-2">
          Поиск работает по базе FDA — американского регулятора лекарственных средств.
          Инструкции могут отличаться от российских аналогов.
        </p>
        <p className="mb-2">
          <strong>Вводите на английском:</strong> используйте МНН (международное непатентованное название).
          Например: <code>metformin</code> (не «метформин»), <code>lisinopril</code> (не «лизиноприл»).
        </p>
        <p>
          Поиск также загружает отчёты о нежелательных явлениях из базы <strong>FDA FAERS</strong> —
          системы мониторинга безопасности лекарств.
        </p>
      </InfoBanner>

      <Card title="Поиск информации о препарате (OpenFDA)" icon={<Search size={16} />}>
        <div className="flex gap-3 mb-3">
          <label htmlFor="drug-search" className="sr-only">Название препарата</label>
          <input
            id="drug-search"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Введите МНН на английском: metformin, lisinopril..."
            className="flex-1 border border-gray-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-medical-teal"
          />
          <button onClick={() => handleSearch()} disabled={loading}
            className="bg-medical-teal text-white px-5 py-2 rounded-lg hover:bg-medical-navy transition-colors flex items-center gap-2 disabled:opacity-50">
            <Search size={16} />{loading ? 'Поиск...' : 'Найти'}
          </button>
        </div>
        <div className="flex flex-wrap gap-2 mb-1">
          <span className="text-xs text-gray-400">Быстрый поиск:</span>
          {DRUG_EXAMPLES.map(d => (
            <button key={d} onClick={() => handleSearch(d)}
              className="text-xs text-medical-teal hover:text-medical-navy border border-medical-teal/30 hover:border-medical-teal/60 px-2 py-0.5 rounded-full transition-colors">
              {d}
            </button>
          ))}
        </div>
        {error && (
          <div role="alert" className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-amber-700 text-sm">{error}</p>
            <p className="text-amber-600 text-xs mt-1">
              Убедитесь, что используете МНН на английском. Торговые названия (Формет, Глюкофаж) обычно не поддерживаются.
            </p>
          </div>
        )}
      </Card>

      {info && (
        <Card title={info.name || query}>
          <div className="space-y-4">
            {info.generic_name && (
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">МНН</span>
                <p className="text-gray-800">{info.generic_name}</p>
              </div>
            )}
            {info.drug_class && (
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Фармакологическая группа</span>
                <p className="text-gray-800">{info.drug_class}</p>
              </div>
            )}
            {info.brand_names?.length ? (
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Торговые названия (США)</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {info.brand_names.map((b, i) => <Badge key={i} variant="info">{b}</Badge>)}
                </div>
              </div>
            ) : null}
            {[
              { key: 'indications', label: 'Показания' },
              { key: 'dosage', label: 'Дозировка' },
              { key: 'contraindications', label: 'Противопоказания' },
              { key: 'warnings', label: 'Предупреждения' },
              { key: 'adverse_reactions', label: 'Нежелательные реакции' },
            ].map(({ key, label }) => info[key as keyof DrugInfo] ? (
              <div key={key}>
                <span className="text-xs text-gray-500 uppercase tracking-wide">{label}</span>
                <p className="text-gray-700 text-sm mt-1 whitespace-pre-wrap">{info[key as keyof DrugInfo] as string}</p>
              </div>
            ) : null)}
          </div>
          <p className="mt-4 text-xs text-gray-400 border-t border-gray-100 pt-3">
            Источник: FDA (USA). Инструкции могут отличаться от утверждённых в РФ. Всегда уточняйте у врача.
          </p>
        </Card>
      )}

      {events && events.length > 0 && (
        <Card title="Нежелательные эффекты (FDA FAERS)" icon={<AlertTriangle size={16} />}>
          <p className="text-xs text-gray-500 mb-3">
            Данные из системы мониторинга нежелательных явлений FDA. Количество спонтанных отчётов —
            не частота встречаемости в популяции.
          </p>
          <button onClick={() => setShowEvents(!showEvents)}
            className="flex items-center gap-2 text-sm text-medical-teal hover:text-medical-navy mb-3">
            {showEvents ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            {showEvents ? 'Скрыть' : `Показать ${events.length} отчётов`}
          </button>
          {showEvents && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <caption className="sr-only">Нежелательные эффекты препарата</caption>
                <thead><tr className="border-b border-gray-100">
                  <th scope="col" className="text-left py-2 text-gray-500 font-medium">Реакция</th>
                  <th scope="col" className="text-right py-2 text-gray-500 font-medium">Случаев</th>
                </tr></thead>
                <tbody>
                  {events.slice(0, 20).map((e, i) => (
                    <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-1.5 text-gray-700">{e.reaction}</td>
                      <td className="py-1.5 text-right font-mono text-gray-600">{e.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
