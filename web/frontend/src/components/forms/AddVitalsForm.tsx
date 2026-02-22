import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { VITALS_FIELDS } from '../../constants';

interface Props {
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  isPending: boolean;
}

export default function AddVitalsForm({ onSubmit, isPending }: Props) {
  const [values, setValues] = useState<Record<string, string>>({});

  const set = (key: string, val: string) => setValues(prev => ({ ...prev, [key]: val }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const data: Record<string, number> = {};
    for (const [key, val] of Object.entries(values)) {
      if (val.trim()) {
        data[key] = parseFloat(val);
      }
    }
    if (Object.keys(data).length === 0) return;
    await onSubmit(data);
  };

  const hasValues = Object.values(values).some(v => v.trim());

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        {VITALS_FIELDS.map(f => (
          <div key={f.key}>
            <label htmlFor={`vital-${f.key}`} className="block text-xs font-medium text-gray-600 mb-1">
              {f.label} ({f.unit})
            </label>
            <input
              id={`vital-${f.key}`}
              type="number"
              step="any"
              placeholder={f.example}
              value={values[f.key] || ''}
              onChange={e => set(f.key, e.target.value)}
              disabled={isPending}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
            />
            <p className="text-[10px] text-gray-400 mt-0.5">Норма: {f.norm}</p>
          </div>
        ))}
      </div>

      <button
        type="submit"
        disabled={!hasValues || isPending}
        className="w-full py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
      >
        {isPending ? <><Loader2 size={16} className="animate-spin" /> Сохранение...</> : 'Записать показатели'}
      </button>
    </form>
  );
}
