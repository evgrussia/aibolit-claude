import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { COMMON_LABS } from '../../constants';

interface Props {
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  isPending: boolean;
}

export default function AddLabResultForm({ onSubmit, isPending }: Props) {
  const [testName, setTestName] = useState('');
  const [value, setValue] = useState('');
  const [unit, setUnit] = useState('');
  const [refRange, setRefRange] = useState('');

  const handleSelectKnown = (code: string) => {
    const lab = COMMON_LABS.find(l => l.code === code);
    if (lab) {
      setTestName(lab.label);
      setUnit(lab.unit);
      setRefRange(lab.normM);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testName.trim() || !value.trim()) return;
    const numVal = parseFloat(value);
    await onSubmit({
      test_name: testName.trim(),
      value: isNaN(numVal) ? value.trim() : numVal,
      unit: unit.trim(),
      reference_range: refRange.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="lab-quick" className="block text-xs font-medium text-gray-600 mb-1">
          Быстрый выбор
        </label>
        <select
          id="lab-quick"
          onChange={e => handleSelectKnown(e.target.value)}
          disabled={isPending}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30"
        >
          <option value="">Выберите анализ или введите вручную...</option>
          {COMMON_LABS.map(l => (
            <option key={l.code} value={l.code}>{l.label} ({l.unit})</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="lab-name" className="block text-xs font-medium text-gray-600 mb-1">
          Название анализа *
        </label>
        <input
          id="lab-name"
          value={testName}
          onChange={e => setTestName(e.target.value)}
          disabled={isPending}
          placeholder="Гемоглобин"
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
        />
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <label htmlFor="lab-value" className="block text-xs font-medium text-gray-600 mb-1">
            Значение *
          </label>
          <input
            id="lab-value"
            value={value}
            onChange={e => setValue(e.target.value)}
            disabled={isPending}
            placeholder="145"
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
        </div>
        <div>
          <label htmlFor="lab-unit" className="block text-xs font-medium text-gray-600 mb-1">
            Единицы
          </label>
          <input
            id="lab-unit"
            value={unit}
            onChange={e => setUnit(e.target.value)}
            disabled={isPending}
            placeholder="г/л"
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
        </div>
        <div>
          <label htmlFor="lab-ref" className="block text-xs font-medium text-gray-600 mb-1">
            Норма
          </label>
          <input
            id="lab-ref"
            value={refRange}
            onChange={e => setRefRange(e.target.value)}
            disabled={isPending}
            placeholder="130–170"
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={!testName.trim() || !value.trim() || isPending}
        className="w-full py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
      >
        {isPending ? <><Loader2 size={16} className="animate-spin" /> Сохранение...</> : 'Добавить результат'}
      </button>
    </form>
  );
}
