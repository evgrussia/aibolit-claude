import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { FREQUENCIES, ROUTES } from '../../constants';

interface Props {
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  isPending: boolean;
}

export default function AddMedicationForm({ onSubmit, isPending }: Props) {
  const [name, setName] = useState('');
  const [dosage, setDosage] = useState('');
  const [frequency, setFrequency] = useState(FREQUENCIES[0]);
  const [route, setRoute] = useState(ROUTES[0]);
  const [notes, setNotes] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !dosage.trim()) return;
    await onSubmit({
      name: name.trim(),
      dosage: dosage.trim(),
      frequency,
      route,
      notes: notes.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="med-name" className="block text-xs font-medium text-gray-600 mb-1">
          Название препарата *
        </label>
        <input
          id="med-name"
          value={name}
          onChange={e => setName(e.target.value)}
          disabled={isPending}
          placeholder="Амлодипин"
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
        />
      </div>

      <div>
        <label htmlFor="med-dosage" className="block text-xs font-medium text-gray-600 mb-1">
          Дозировка *
        </label>
        <input
          id="med-dosage"
          value={dosage}
          onChange={e => setDosage(e.target.value)}
          disabled={isPending}
          placeholder="5 мг"
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="med-freq" className="block text-xs font-medium text-gray-600 mb-1">
            Частота приёма
          </label>
          <select
            id="med-freq"
            value={frequency}
            onChange={e => setFrequency(e.target.value)}
            disabled={isPending}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30"
          >
            {FREQUENCIES.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="med-route" className="block text-xs font-medium text-gray-600 mb-1">
            Путь введения
          </label>
          <select
            id="med-route"
            value={route}
            onChange={e => setRoute(e.target.value)}
            disabled={isPending}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30"
          >
            {ROUTES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="med-notes" className="block text-xs font-medium text-gray-600 mb-1">
          Заметки
        </label>
        <textarea
          id="med-notes"
          value={notes}
          onChange={e => setNotes(e.target.value)}
          disabled={isPending}
          rows={2}
          placeholder="Принимать утром натощак..."
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 resize-none disabled:opacity-50"
        />
      </div>

      <button
        type="submit"
        disabled={!name.trim() || !dosage.trim() || isPending}
        className="w-full py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
      >
        {isPending ? <><Loader2 size={16} className="animate-spin" /> Сохранение...</> : 'Назначить препарат'}
      </button>
    </form>
  );
}
