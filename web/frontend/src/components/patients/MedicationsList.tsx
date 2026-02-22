import { memo } from 'react';
import { Pill, Trash2 } from 'lucide-react';
import Card from '../shared/Card';
import type { Medication } from '../../types/patient';

interface Props {
  medications: Medication[];
  onDelete?: (id: number) => void;
}

export default memo(function MedicationsList({ medications, onDelete }: Props) {
  return (
    <Card title="Препараты" icon={<Pill size={18} />}>
      {medications.length === 0 ? (
        <p className="text-gray-400 text-sm">Нет назначений</p>
      ) : (
        <div className="space-y-3">
          {medications.map((m, i) => (
            <div key={m.id ?? i} className="flex items-start justify-between py-2 border-b border-gray-50 last:border-0">
              <div>
                <p className="font-medium text-gray-800">{m.name}</p>
                <p className="text-sm text-gray-500">{m.dosage} — {m.frequency}</p>
                {m.notes && <p className="text-xs text-gray-400 mt-0.5">{m.notes}</p>}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">{m.route}</span>
                {onDelete && m.id != null && (
                  <button
                    onClick={() => onDelete(m.id!)}
                    className="p-1 rounded hover:bg-red-50 text-gray-300 hover:text-red-500 transition-colors"
                    title="Удалить"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
});
