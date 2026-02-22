import { memo } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ShieldAlert, ChevronRight } from 'lucide-react';
import Badge from '../shared/Badge';
import Card from '../shared/Card';
import { formatDate, statusLabel } from '../../utils/formatters';
import type { Diagnosis } from '../../types/patient';

interface Props {
  diagnoses: Diagnosis[];
  compact?: boolean;
}

function statusVariant(s: string) {
  switch (s) {
    case 'active': return 'danger' as const;
    case 'chronic': return 'warning' as const;
    case 'resolved': return 'success' as const;
    default: return 'gray' as const;
  }
}

export default memo(function DiagnosesList({ diagnoses, compact }: Props) {
  const { patientId } = useParams();
  const items = compact ? diagnoses.filter(d => d.status !== 'resolved').slice(0, 8) : diagnoses;

  return (
    <Card title="Диагнозы" icon={<ShieldAlert size={18} />}>
      {items.length === 0 ? (
        <p className="text-gray-400 text-sm">Нет диагнозов</p>
      ) : (
        <div className="space-y-2">
          {items.map((d, i) => {
            const content = (
              <div className="flex items-start justify-between py-2 border-b border-gray-50 last:border-0 group">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-medical-teal font-semibold">{d.icd10_code}</span>
                    <Badge variant={statusVariant(d.status)}>{statusLabel(d.status)}</Badge>
                  </div>
                  <p className="text-sm text-gray-700 mt-0.5 truncate group-hover:text-medical-teal transition-colors">
                    {d.name}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-3">
                  <span className="text-xs text-gray-400">{formatDate(d.date_diagnosed)}</span>
                  {patientId && (
                    <ChevronRight size={14} className="text-gray-300 group-hover:text-medical-teal transition-colors" />
                  )}
                </div>
              </div>
            );

            return patientId ? (
              <Link
                key={i}
                to={`/patients/${patientId}/diagnoses/${encodeURIComponent(d.icd10_code)}`}
                className="block hover:bg-gray-50/50 rounded-lg -mx-1 px-1 transition-colors"
              >
                {content}
              </Link>
            ) : (
              <div key={i}>{content}</div>
            );
          })}
        </div>
      )}
    </Card>
  );
});
