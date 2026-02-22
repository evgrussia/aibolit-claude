import { memo } from 'react';
import { HeartPulse, Thermometer, Wind, Droplets } from 'lucide-react';
import Card from '../shared/Card';
import { VITALS_THRESHOLDS } from '../../constants/medical';
import type { VitalSigns } from '../../types/patient';

interface Props {
  vitals: VitalSigns | null;
}

function Gauge({ label, value, unit, icon, status }: {
  label: string; value: string | number | null; unit: string;
  icon: React.ReactNode; status: 'normal' | 'warning' | 'danger';
}) {
  const ring = {
    normal: 'border-emerald-400',
    warning: 'border-amber-400',
    danger: 'border-red-400',
  }[status];

  return (
    <div className="flex flex-col items-center">
      <div className={`w-16 h-16 rounded-full border-3 ${ring} flex items-center justify-center bg-white shadow-sm`}>
        {icon}
      </div>
      <span className="text-lg font-bold mt-1.5 text-gray-800">{value ?? '—'}</span>
      <span className="text-xs text-gray-400">{unit}</span>
      <span className="text-xs text-gray-500 mt-0.5">{label}</span>
    </div>
  );
}

function bpStatus(sys: number | null): 'normal' | 'warning' | 'danger' {
  if (!sys) return 'normal';
  if (sys >= VITALS_THRESHOLDS.bp.danger) return 'danger';
  if (sys >= VITALS_THRESHOLDS.bp.warning) return 'warning';
  return 'normal';
}

function hrStatus(hr: number | null): 'normal' | 'warning' | 'danger' {
  if (!hr) return 'normal';
  if (hr > VITALS_THRESHOLDS.hr.highDanger || hr < VITALS_THRESHOLDS.hr.lowDanger) return 'danger';
  if (hr > VITALS_THRESHOLDS.hr.highWarning || hr < VITALS_THRESHOLDS.hr.lowWarning) return 'warning';
  return 'normal';
}

export default memo(function VitalsGauges({ vitals }: Props) {
  if (!vitals) return null;

  const bp = vitals.systolic_bp && vitals.diastolic_bp
    ? `${vitals.systolic_bp}/${vitals.diastolic_bp}`
    : null;

  return (
    <Card title="Витальные показатели" icon={<HeartPulse size={18} />}>
      <div className="flex justify-around flex-wrap gap-4">
        <Gauge
          label="АД" value={bp} unit="мм рт.ст."
          icon={<Droplets size={20} className="text-blue-500" />}
          status={bpStatus(vitals.systolic_bp)}
        />
        <Gauge
          label="Пульс" value={vitals.heart_rate} unit="уд/мин"
          icon={<HeartPulse size={20} className="text-red-500" />}
          status={hrStatus(vitals.heart_rate)}
        />
        <Gauge
          label="Темп." value={vitals.temperature?.toFixed(1) ?? null} unit="°C"
          icon={<Thermometer size={20} className="text-orange-500" />}
          status={vitals.temperature && vitals.temperature > VITALS_THRESHOLDS.temp.warning ? 'warning' : 'normal'}
        />
        <Gauge
          label="SpO2" value={vitals.spo2} unit="%"
          icon={<Wind size={20} className="text-cyan-500" />}
          status={vitals.spo2 && vitals.spo2 < VITALS_THRESHOLDS.spo2.danger ? 'danger' : 'normal'}
        />
      </div>
    </Card>
  );
});
