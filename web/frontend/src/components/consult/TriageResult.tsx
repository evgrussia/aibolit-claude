import { Stethoscope, AlertTriangle, ArrowRight } from 'lucide-react';
import EmergencyBanner from '../shared/EmergencyBanner';
import type { TriageResult as TriageResultData } from '../../api/consultations';

interface Props {
  result: TriageResultData;
  onSelectSpecialty: (specialtyId: string) => void;
}

export default function TriageResult({ result, onSelectSpecialty }: Props) {
  return (
    <div className="space-y-4">
      {result.emergency && (
        <EmergencyBanner message={result.emergency.message} />
      )}

      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-gray-700">
          Рекомендуемые специалисты:
        </h3>
        {result.recommendations.map((rec, i) => (
          <button
            key={rec.specialty_id}
            onClick={() => onSelectSpecialty(rec.specialty_id)}
            className="w-full text-left p-4 rounded-xl border border-gray-100 hover:border-medical-teal/40 hover:shadow-md transition-all bg-white group"
          >
            <div className="flex items-start gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                i === 0 ? 'bg-medical-teal/10' : 'bg-gray-50'
              }`}>
                <Stethoscope size={18} className={i === 0 ? 'text-medical-teal' : 'text-gray-400'} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-800 group-hover:text-medical-teal transition-colors">
                    {rec.name_ru}
                  </span>
                  {i === 0 && (
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-medical-teal/10 text-medical-teal uppercase">
                      Лучшее совпадение
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{rec.description}</p>
                <p className="text-xs text-medical-teal mt-1">{rec.reason}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <div className="text-right">
                  <div className="text-xs text-gray-400">Релевантность</div>
                  <div className={`text-sm font-bold ${
                    rec.relevance >= 0.8 ? 'text-emerald-600' : rec.relevance >= 0.5 ? 'text-amber-600' : 'text-gray-500'
                  }`}>
                    {Math.round(rec.relevance * 100)}%
                  </div>
                </div>
                <ArrowRight size={16} className="text-gray-300 group-hover:text-medical-teal transition-colors" />
              </div>
            </div>
          </button>
        ))}
      </div>

      {result.red_flags && result.red_flags.length > 0 && !result.emergency && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={14} className="text-amber-500" />
            <span className="text-xs font-semibold text-amber-700">Обратите внимание</span>
          </div>
          {result.red_flags.map((f, i) => (
            <p key={i} className="text-xs text-amber-600 ml-5">{f.description}</p>
          ))}
        </div>
      )}
    </div>
  );
}
