import { useState } from 'react';
import { Loader2 } from 'lucide-react';

interface Props {
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  isPending: boolean;
}

export default function AddAllergyForm({ onSubmit, isPending }: Props) {
  const [substance, setSubstance] = useState('');
  const [reaction, setReaction] = useState('');
  const [severity, setSeverity] = useState('moderate');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!substance.trim()) return;
    await onSubmit({
      substance: substance.trim(),
      reaction: reaction.trim(),
      severity,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="allergy-substance" className="block text-xs font-medium text-gray-600 mb-1">
          Аллерген *
        </label>
        <input
          id="allergy-substance"
          value={substance}
          onChange={e => setSubstance(e.target.value)}
          disabled={isPending}
          placeholder="Пенициллин"
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
        />
      </div>

      <div>
        <label htmlFor="allergy-reaction" className="block text-xs font-medium text-gray-600 mb-1">
          Реакция
        </label>
        <input
          id="allergy-reaction"
          value={reaction}
          onChange={e => setReaction(e.target.value)}
          disabled={isPending}
          placeholder="Крапивница, отёк Квинке..."
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
        />
      </div>

      <div>
        <label htmlFor="allergy-severity" className="block text-xs font-medium text-gray-600 mb-1">
          Степень тяжести
        </label>
        <select
          id="allergy-severity"
          value={severity}
          onChange={e => setSeverity(e.target.value)}
          disabled={isPending}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30"
        >
          <option value="mild">Лёгкая</option>
          <option value="moderate">Умеренная</option>
          <option value="severe">Тяжёлая</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={!substance.trim() || isPending}
        className="w-full py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
      >
        {isPending ? <><Loader2 size={16} className="animate-spin" /> Сохранение...</> : 'Добавить аллергию'}
      </button>
    </form>
  );
}
