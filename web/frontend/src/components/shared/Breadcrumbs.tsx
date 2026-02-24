import { Link, useLocation, useParams } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

const ROUTE_LABELS: Record<string, string> = {
  patients: 'Пациенты',
  labs: 'Анализы',
  vitals: 'Витальные',
  consultations: 'Консультации',
  consult: 'AI Консультация',
  chat: 'Чат с врачом',
  timeline: 'Хронология',
  diagnoses: 'Диагнозы',
  diagnostics: 'Диагностика',
  drugs: 'Лекарства',
  documents: 'Документы',
};

export default function Breadcrumbs() {
  const { pathname } = useLocation();
  const { patientId } = useParams();

  const segments = pathname.split('/').filter(Boolean);
  if (segments.length <= 1) return null;

  const crumbs: { label: string; to: string }[] = [];

  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    const path = '/' + segments.slice(0, i + 1).join('/');

    if (seg === patientId) {
      crumbs.push({ label: `ID ${seg.slice(0, 8)}`, to: path });
    } else if (ROUTE_LABELS[seg]) {
      crumbs.push({ label: ROUTE_LABELS[seg], to: path });
    }
  }

  if (crumbs.length <= 1) return null;

  return (
    <nav aria-label="Навигационная цепочка" className="flex items-center gap-1 text-xs text-gray-400 mb-3 sm:mb-4 overflow-x-auto whitespace-nowrap">
      {crumbs.map((c, i) => (
        <span key={c.to} className="flex items-center gap-1 shrink-0">
          {i > 0 && <ChevronRight size={12} />}
          {i < crumbs.length - 1 ? (
            <Link to={c.to} className="hover:text-medical-teal transition-colors">{c.label}</Link>
          ) : (
            <span className="text-gray-600">{c.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
