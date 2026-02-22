import { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { usePatient } from '../hooks/usePatient';
import { useConsultations } from '../hooks/useConsultations';
import Card from '../components/shared/Card';
import Badge from '../components/shared/Badge';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import ApiError from '../components/shared/ApiError';
import { formatDateTime, statusLabel } from '../utils/formatters';
import {
  Clock, HeartPulse, FlaskConical, ShieldAlert, Pill, Stethoscope, Filter,
} from 'lucide-react';

type EventType = 'vitals' | 'labs' | 'diagnoses' | 'medications' | 'consultations';

interface TimelineEvent {
  type: EventType;
  date: string;
  title: string;
  detail: string;
  badge?: { label: string; variant: 'success' | 'warning' | 'danger' | 'info' | 'gray' };
}

const TYPE_CONFIG: Record<EventType, { icon: React.ReactNode; label: string; color: string }> = {
  vitals: { icon: <HeartPulse size={14} />, label: 'Витальные', color: 'bg-rose-100 text-rose-600' },
  labs: { icon: <FlaskConical size={14} />, label: 'Анализы', color: 'bg-cyan-100 text-cyan-600' },
  diagnoses: { icon: <ShieldAlert size={14} />, label: 'Диагнозы', color: 'bg-amber-100 text-amber-600' },
  medications: { icon: <Pill size={14} />, label: 'Лекарства', color: 'bg-emerald-100 text-emerald-600' },
  consultations: { icon: <Stethoscope size={14} />, label: 'Консультации', color: 'bg-blue-100 text-blue-600' },
};

const RANGES = [
  { label: 'Неделя', days: 7 },
  { label: 'Месяц', days: 30 },
  { label: '3 месяца', days: 90 },
  { label: 'Год', days: 365 },
  { label: 'Все', days: Infinity },
];

export default function HealthTimelinePage() {
  const { patientId } = useParams();
  const { data: patient, isLoading, error, refetch } = usePatient(patientId);
  const { data: consultations = [] } = useConsultations(patientId);

  const [range, setRange] = useState(90);
  const [typeFilter, setTypeFilter] = useState<Set<EventType>>(
    new Set(['vitals', 'labs', 'diagnoses', 'medications', 'consultations']),
  );

  const toggleType = (t: EventType) => {
    setTypeFilter(prev => {
      const next = new Set(prev);
      if (next.has(t)) next.delete(t);
      else next.add(t);
      return next;
    });
  };

  const events = useMemo(() => {
    if (!patient) return [];

    const items: TimelineEvent[] = [];
    const cutoff = range === Infinity ? 0 : Date.now() - range * 86_400_000;

    // Vitals
    for (const v of patient.vitals_history) {
      if (new Date(v.timestamp).getTime() < cutoff) continue;
      const parts: string[] = [];
      if (v.systolic_bp && v.diastolic_bp) parts.push(`АД ${v.systolic_bp}/${v.diastolic_bp}`);
      if (v.heart_rate) parts.push(`ЧСС ${v.heart_rate}`);
      if (v.temperature) parts.push(`t° ${v.temperature}`);
      if (v.spo2) parts.push(`SpO₂ ${v.spo2}%`);
      items.push({
        type: 'vitals',
        date: v.timestamp,
        title: 'Измерение витальных показателей',
        detail: parts.join(' · ') || 'Записаны показатели',
      });
    }

    // Labs
    for (const lr of patient.lab_results) {
      if (new Date(lr.date).getTime() < cutoff) continue;
      items.push({
        type: 'labs',
        date: lr.date,
        title: lr.test_name,
        detail: `${lr.value} ${lr.unit}` + (lr.reference_range ? ` (норма: ${lr.reference_range})` : ''),
        badge: lr.is_abnormal
          ? { label: 'Отклонение', variant: 'danger' }
          : { label: 'Норма', variant: 'success' },
      });
    }

    // Diagnoses
    for (const d of patient.diagnoses) {
      if (new Date(d.date_diagnosed).getTime() < cutoff) continue;
      items.push({
        type: 'diagnoses',
        date: d.date_diagnosed,
        title: `${d.icd10_code} — ${d.name}`,
        detail: d.notes || statusLabel(d.status),
        badge: {
          label: statusLabel(d.status),
          variant: d.status === 'active' ? 'danger' : d.status === 'chronic' ? 'warning' : 'success',
        },
      });
    }

    // Medications
    for (const m of patient.medications) {
      if (!m.start_date) continue;
      if (new Date(m.start_date).getTime() < cutoff) continue;
      items.push({
        type: 'medications',
        date: m.start_date,
        title: `Назначен: ${m.name}`,
        detail: `${m.dosage}, ${m.frequency}, ${m.route}`,
        badge: { label: 'Назначение', variant: 'info' },
      });
    }

    // Consultations
    for (const c of consultations as { date: string; specialty: string; complaints: string }[]) {
      if (new Date(c.date).getTime() < cutoff) continue;
      items.push({
        type: 'consultations',
        date: c.date,
        title: `Консультация: ${c.specialty}`,
        detail: c.complaints?.slice(0, 100) || '',
      });
    }

    return items
      .filter(e => typeFilter.has(e.type))
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }, [patient, consultations, range, typeFilter]);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ApiError message={(error as Error).message} onRetry={() => refetch()} />;
  if (!patient) return <p className="text-center text-gray-400 py-12">Пациент не найден</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
        <Clock size={24} className="text-medical-teal" /> Хронология
      </h1>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter size={14} className="text-gray-400" />
            <span className="text-xs font-medium text-gray-500 uppercase">Период:</span>
            <div className="flex gap-1">
              {RANGES.map(r => (
                <button
                  key={r.days}
                  onClick={() => setRange(r.days)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                    range === r.days
                      ? 'bg-medical-teal text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-gray-500 uppercase">Тип:</span>
            <div className="flex gap-1">
              {(Object.keys(TYPE_CONFIG) as EventType[]).map(t => (
                <button
                  key={t}
                  onClick={() => toggleType(t)}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                    typeFilter.has(t)
                      ? TYPE_CONFIG[t].color
                      : 'bg-gray-50 text-gray-300'
                  }`}
                >
                  {TYPE_CONFIG[t].icon}
                  {TYPE_CONFIG[t].label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Timeline */}
      {events.length === 0 ? (
        <p className="text-center text-gray-400 py-12">Нет событий за выбранный период</p>
      ) : (
        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-px bg-gray-200" />
          <div className="space-y-4">
            {events.map((ev, i) => (
              <div key={i} className="relative flex gap-4 pl-12">
                <div className={`absolute left-4 w-5 h-5 rounded-full flex items-center justify-center -translate-x-1/2 ${TYPE_CONFIG[ev.type].color}`}>
                  {TYPE_CONFIG[ev.type].icon}
                </div>
                <div className="flex-1 bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${TYPE_CONFIG[ev.type].color}`}>
                          {TYPE_CONFIG[ev.type].label}
                        </span>
                        {ev.badge && <Badge variant={ev.badge.variant}>{ev.badge.label}</Badge>}
                      </div>
                      <p className="text-sm font-medium text-gray-800 mt-1">{ev.title}</p>
                      {ev.detail && <p className="text-xs text-gray-500 mt-0.5">{ev.detail}</p>}
                    </div>
                    <span className="text-xs text-gray-400 shrink-0">{formatDateTime(ev.date)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
