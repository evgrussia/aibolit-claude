import { Stethoscope, FlaskConical, BookOpen, AlertTriangle } from 'lucide-react';
import Card from '../shared/Card';
import Badge from '../shared/Badge';
import type { ConsultationResult } from '../../types/patient';

interface Props {
  result: ConsultationResult;
}

export default function ConsultationResultCard({ result }: Props) {
  return (
    <div className="space-y-4">
      {/* Doctor card */}
      <Card>
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-medical-teal/10 rounded-full flex items-center justify-center">
            <Stethoscope size={28} className="text-medical-teal" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-800">{result.doctor.name}</h3>
            <p className="text-sm text-gray-500">{result.doctor.qualification}</p>
          </div>
        </div>
      </Card>

      {/* Summary — main content */}
      {result.consultation.summary && (
        <Card>
          <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
            {result.consultation.summary}
          </div>
        </Card>
      )}

      {/* Recommended tests */}
      {result.consultation.recommended_tests.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <FlaskConical size={16} className="text-medical-teal" />
            <span className="text-sm font-medium text-gray-700">Рекомендуемые обследования</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.consultation.recommended_tests.map(test => (
              <Badge key={test} variant="info">{test}</Badge>
            ))}
          </div>
        </Card>
      )}

      {/* ICD codes */}
      {result.consultation.relevant_icd_prefixes.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <BookOpen size={16} className="text-medical-teal" />
            <span className="text-sm font-medium text-gray-700">Коды МКБ</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.consultation.relevant_icd_prefixes.map(code => (
              <Badge key={code} variant="gray">{code}</Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Instructions (small text) */}
      <p className="text-xs text-gray-400 leading-relaxed whitespace-pre-line px-1">
        {result.instructions}
      </p>

      {/* Disclaimer */}
      <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
        <AlertTriangle size={16} className="text-amber-500 shrink-0 mt-0.5" />
        <p className="text-xs text-amber-700">{result.disclaimer}</p>
      </div>
    </div>
  );
}
