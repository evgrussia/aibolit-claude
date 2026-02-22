import { memo } from 'react';
import { Pill } from 'lucide-react';
import Card from '../shared/Card';
import type { Medication } from '../../types/patient';

interface Props {
  medications: Medication[];
}

export default memo(function MedicationsList({ medications }: Props) {
  return (
    <Card title="Препараты" icon={<Pill size={18} />}>
      {medications.length === 0 ? (
        <p className="text-gray-400 text-sm">Нет назначений</p>
      ) : (
        <div className="space-y-3">
          {medications.map((m, i) => (
            <div key={i} className="flex items-start justify-between py-2 border-b border-gray-50 last:border-0">
              <div>
                <p className="font-medium text-gray-800">{m.name}</p>
                <p className="text-sm text-gray-500">{m.dosage} — {m.frequency}</p>
                {m.notes && <p className="text-xs text-gray-400 mt-0.5">{m.notes}</p>}
              </div>
              <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded">{m.route}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
});
