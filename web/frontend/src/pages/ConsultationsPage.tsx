import { useParams } from 'react-router-dom';
import { useConsultations } from '../hooks/useConsultations';
import ConsultationCard from '../components/consultations/ConsultationCard';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import ApiError from '../components/shared/ApiError';
import { Stethoscope, MessageCircle } from 'lucide-react';
import type { Consultation } from '../types/patient';

export default function ConsultationsPage() {
  const { patientId } = useParams();
  const { data: consultations = [], isLoading, error, refetch } = useConsultations(patientId);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ApiError message={(error as Error).message || 'Ошибка загрузки'} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Stethoscope size={24} className="text-medical-teal" /> Консультации
        </h1>
        <span className="text-sm text-gray-400">{consultations.length} записей</span>
      </div>

      {consultations.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <MessageCircle size={48} className="mx-auto mb-3 opacity-50" />
          <p>Нет истории консультаций</p>
          <p className="text-sm mt-1">AI-консультации проводятся через Claude.ai с MCP</p>
        </div>
      ) : (
        <div className="space-y-3">
          {(consultations as Consultation[]).map(c => (
            <ConsultationCard key={c.id} consultation={c} />
          ))}
        </div>
      )}
    </div>
  );
}
