import { useState } from 'react';
import { Loader2, Search } from 'lucide-react';
import { useIcdSearch } from '../../hooks/useDiseaseInfo';

interface Props {
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  isPending: boolean;
}

export default function AddDiagnosisForm({ onSubmit, isPending }: Props) {
  const [icdCode, setIcdCode] = useState('');
  const [name, setName] = useState('');
  const [status, setStatus] = useState('active');
  const [notes, setNotes] = useState('');
  const [confidence, setConfidence] = useState(0.8);
  const [searchQ, setSearchQ] = useState('');
  const [showResults, setShowResults] = useState(false);

  const { data: icdResults = [] } = useIcdSearch(searchQ);

  const handleSelect = (result: { code: string; title: string }) => {
    setIcdCode(result.code);
    setName(result.title);
    setShowResults(false);
    setSearchQ('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!icdCode.trim() || !name.trim()) return;
    await onSubmit({
      icd10_code: icdCode.trim(),
      name: name.trim(),
      status,
      notes: notes.trim(),
      confidence,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="relative">
        <label htmlFor="diag-search" className="block text-xs font-medium text-gray-600 mb-1">
          Поиск МКБ
        </label>
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            id="diag-search"
            value={searchQ}
            onChange={e => { setSearchQ(e.target.value); setShowResults(true); }}
            onFocus={() => setShowResults(true)}
            disabled={isPending}
            placeholder="Введите диагноз для поиска..."
            className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
        </div>
        {showResults && icdResults.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
            {(icdResults as { code: string; title: string }[]).map((r, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSelect(r)}
                className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm border-b border-gray-50 last:border-0"
              >
                <span className="font-mono text-medical-teal text-xs">{r.code}</span>
                <span className="ml-2 text-gray-700">{r.title}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="diag-code" className="block text-xs font-medium text-gray-600 mb-1">
            Код МКБ-10 *
          </label>
          <input
            id="diag-code"
            value={icdCode}
            onChange={e => setIcdCode(e.target.value)}
            disabled={isPending}
            placeholder="I10"
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
        </div>
        <div>
          <label htmlFor="diag-status" className="block text-xs font-medium text-gray-600 mb-1">
            Статус
          </label>
          <select
            id="diag-status"
            value={status}
            onChange={e => setStatus(e.target.value)}
            disabled={isPending}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30"
          >
            <option value="active">Активный</option>
            <option value="chronic">Хронический</option>
            <option value="resolved">Вылечен</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="diag-name" className="block text-xs font-medium text-gray-600 mb-1">
          Название диагноза *
        </label>
        <input
          id="diag-name"
          value={name}
          onChange={e => setName(e.target.value)}
          disabled={isPending}
          placeholder="Артериальная гипертензия"
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
        />
      </div>

      <div>
        <label htmlFor="diag-confidence" className="block text-xs font-medium text-gray-600 mb-1">
          Достоверность: {(confidence * 100).toFixed(0)}%
        </label>
        <input
          id="diag-confidence"
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={confidence}
          onChange={e => setConfidence(parseFloat(e.target.value))}
          disabled={isPending}
          className="w-full"
        />
      </div>

      <div>
        <label htmlFor="diag-notes" className="block text-xs font-medium text-gray-600 mb-1">
          Заметки
        </label>
        <textarea
          id="diag-notes"
          value={notes}
          onChange={e => setNotes(e.target.value)}
          disabled={isPending}
          rows={2}
          placeholder="Дополнительная информация..."
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 resize-none disabled:opacity-50"
        />
      </div>

      <button
        type="submit"
        disabled={!icdCode.trim() || !name.trim() || isPending}
        className="w-full py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
      >
        {isPending ? <><Loader2 size={16} className="animate-spin" /> Сохранение...</> : 'Добавить диагноз'}
      </button>
    </form>
  );
}
