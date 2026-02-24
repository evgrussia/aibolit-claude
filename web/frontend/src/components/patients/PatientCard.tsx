import { memo } from 'react';
import { User, Calendar, Droplets, AlertTriangle } from 'lucide-react';
import Badge from '../shared/Badge';
import { formatDate, genderLabel } from '../../utils/formatters';
import type { PatientFull } from '../../types/patient';

interface Props {
  patient: PatientFull;
}

export default memo(function PatientCard({ patient }: Props) {
  const genderIcon = patient.gender === 'male' ? '♂' : '♀';
  const genderColor = patient.gender === 'male' ? 'text-blue-500' : 'text-pink-500';

  return (
    <div className="bg-gradient-to-r from-medical-navy to-medical-navy-light rounded-xl p-4 sm:p-6 text-white shadow-lg">
      <div className="flex items-start gap-3 sm:gap-5">
        <div className="w-12 h-12 sm:w-16 sm:h-16 bg-white/20 rounded-full flex items-center justify-center shrink-0">
          <User size={24} className="sm:hidden" />
          <User size={32} className="hidden sm:block" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h2 className="text-lg sm:text-2xl font-bold truncate">{patient.full_name}</h2>
            <div className="text-right shrink-0 hidden sm:block">
              <div className="text-3xl font-bold text-medical-teal-light">
                {patient.diagnoses.filter(d => d.status === 'active').length}
              </div>
              <div className="text-xs text-blue-200">активных диагнозов</div>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 sm:gap-4 mt-1.5 sm:mt-2 text-blue-100 text-xs sm:text-sm">
            <span className="flex items-center gap-1">
              <Calendar size={14} /> {formatDate(patient.date_of_birth)}
            </span>
            <span className={`font-semibold ${genderColor}`}>
              {genderIcon} {genderLabel(patient.gender)}
            </span>
            <span>{patient.age} лет</span>
            {patient.blood_type && (
              <span className="flex items-center gap-1">
                <Droplets size={14} /> {patient.blood_type}
              </span>
            )}
          </div>

          {patient.allergies.length > 0 && (
            <div className="mt-2 sm:mt-3 flex items-center gap-2 flex-wrap">
              <AlertTriangle size={14} className="text-amber-300 shrink-0" />
              {patient.allergies.map((a, i) => (
                <Badge key={i} variant="warning">{a.substance}</Badge>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});
