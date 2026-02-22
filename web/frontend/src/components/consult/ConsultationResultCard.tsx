import { useState } from 'react';
import { ChevronDown, ChevronUp, Stethoscope, BookOpen, FlaskConical, AlertTriangle } from 'lucide-react';
import Card from '../shared/Card';
import Badge from '../shared/Badge';
import type { ConsultationResult } from '../../types/patient';

interface Props {
  result: ConsultationResult;
}

function Collapsible({ title, icon, children, defaultOpen = false }: {
  title: string; icon: React.ReactNode; children: React.ReactNode; defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-gray-100 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
      >
        <span className="flex items-center gap-2">
          <span className="text-medical-teal">{icon}</span>
          {title}
        </span>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      {open && <div className="px-4 pb-4 text-sm text-gray-600">{children}</div>}
    </div>
  );
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

      {/* Patient context */}
      {result.consultation.patient_context !== 'Карта пациента не загружена' && (
        <Collapsible title="Контекст пациента" icon={<BookOpen size={16} />}>
          <pre className="whitespace-pre-wrap text-xs bg-gray-50 rounded-lg p-3 max-h-48 overflow-y-auto">
            {result.consultation.patient_context}
          </pre>
        </Collapsible>
      )}

      {/* Recommended tests */}
      {result.consultation.recommended_tests.length > 0 && (
        <Collapsible title="Рекомендуемые обследования" icon={<FlaskConical size={16} />} defaultOpen>
          <div className="flex flex-wrap gap-2">
            {result.consultation.recommended_tests.map(test => (
              <Badge key={test} variant="info">{test}</Badge>
            ))}
          </div>
        </Collapsible>
      )}

      {/* Available skills */}
      {result.consultation.available_skills.length > 0 && (
        <Collapsible title="Диагностические навыки" icon={<Stethoscope size={16} />}>
          <div className="space-y-2">
            {result.consultation.available_skills.map(skill => (
              <div key={skill.name} className="flex items-start gap-2">
                <span className="text-medical-teal mt-0.5 shrink-0">-</span>
                <div>
                  <span className="font-medium text-gray-700">{skill.name}</span>
                  <span className="text-gray-400 ml-2">{skill.description}</span>
                </div>
              </div>
            ))}
          </div>
        </Collapsible>
      )}

      {/* ICD prefixes */}
      {result.consultation.relevant_icd_prefixes.length > 0 && (
        <Collapsible title="Коды МКБ" icon={<BookOpen size={16} />}>
          <div className="flex flex-wrap gap-2">
            {result.consultation.relevant_icd_prefixes.map(code => (
              <Badge key={code} variant="gray">{code}</Badge>
            ))}
          </div>
        </Collapsible>
      )}

      {/* Instructions */}
      <Card title="Порядок консультации">
        <pre className="whitespace-pre-wrap text-sm text-gray-600 leading-relaxed">
          {result.instructions}
        </pre>
      </Card>

      {/* Disclaimer */}
      <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
        <AlertTriangle size={16} className="text-amber-500 shrink-0 mt-0.5" />
        <p className="text-xs text-amber-700">{result.disclaimer}</p>
      </div>
    </div>
  );
}
