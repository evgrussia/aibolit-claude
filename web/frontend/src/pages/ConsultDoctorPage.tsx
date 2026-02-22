import { useState } from 'react';
import { MessageSquare, ArrowLeft, Loader2 } from 'lucide-react';
import { useSpecializations } from '../hooks/useSpecializations';
import { useStartConsultation } from '../hooks/useConsultation';
import { useAuth } from '../contexts/AuthContext';
import SpecialtyGrid from '../components/consult/SpecialtyGrid';
import ConsultationResultCard from '../components/consult/ConsultationResultCard';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import ApiError from '../components/shared/ApiError';
import { useToast } from '../contexts/ToastContext';
import type { Specialization, ConsultationResult } from '../types/patient';

type Step = 'specialty' | 'complaint' | 'result';

export default function ConsultDoctorPage() {
  const [step, setStep] = useState<Step>('specialty');
  const [selected, setSelected] = useState<Specialization | null>(null);
  const [complaints, setComplaints] = useState('');
  const [result, setResult] = useState<ConsultationResult | null>(null);

  const { data: specializations = [], isLoading, error, refetch } = useSpecializations();
  const mutation = useStartConsultation();
  const { patientId } = useAuth();
  const toast = useToast();

  const handleSelectSpecialty = (spec: Specialization) => {
    setSelected(spec);
    setStep('complaint');
  };

  const handleSubmit = async () => {
    if (!selected || !complaints.trim()) return;
    try {
      const res = await mutation.mutateAsync({
        specialty: selected.id,
        complaints: complaints.trim(),
        patientId: patientId || undefined,
      });
      setResult(res);
      setStep('result');
      toast.success('Консультация проведена');
    } catch (err) {
      toast.error((err as Error).message || 'Ошибка при создании консультации');
    }
  };

  const handleReset = () => {
    setStep('specialty');
    setSelected(null);
    setComplaints('');
    setResult(null);
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ApiError message={(error as Error).message} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        {step !== 'specialty' && (
          <button
            onClick={() => setStep(step === 'result' ? 'complaint' : 'specialty')}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500"
          >
            <ArrowLeft size={20} />
          </button>
        )}
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <MessageSquare size={24} className="text-medical-teal" />
          AI Консультация
        </h1>
      </div>

      {/* Step indicators */}
      <div className="flex items-center gap-2 text-sm">
        {(['specialty', 'complaint', 'result'] as const).map((s, i) => {
          const labels = ['Специалист', 'Жалобы', 'Результат'];
          const isActive = s === step;
          const isPast = ['specialty', 'complaint', 'result'].indexOf(step) > i;
          return (
            <div key={s} className="flex items-center gap-2">
              {i > 0 && <div className={`w-8 h-px ${isPast || isActive ? 'bg-medical-teal' : 'bg-gray-200'}`} />}
              <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                isActive ? 'bg-medical-teal text-white' : isPast ? 'bg-medical-teal/10 text-medical-teal' : 'bg-gray-100 text-gray-400'
              }`}>
                <span>{i + 1}</span>
                <span>{labels[i]}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Step 1: Specialty picker */}
      {step === 'specialty' && (
        <SpecialtyGrid specializations={specializations} onSelect={handleSelectSpecialty} />
      )}

      {/* Step 2: Complaint form */}
      {step === 'complaint' && selected && (
        <div className="max-w-2xl space-y-6">
          <div className="bg-medical-teal/5 border border-medical-teal/20 rounded-xl p-4">
            <div className="font-medium text-gray-800">{selected.name_ru}</div>
            <p className="text-sm text-gray-500 mt-1">{selected.description}</p>
          </div>

          <div>
            <label htmlFor="complaints" className="block text-sm font-medium text-gray-700 mb-1.5">
              Жалобы и симптомы
            </label>
            <textarea
              id="complaints"
              value={complaints}
              onChange={e => setComplaints(e.target.value)}
              rows={5}
              placeholder="Опишите ваши жалобы, симптомы, когда началось, что усиливает/ослабляет..."
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 resize-none"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={!complaints.trim() || mutation.isPending}
            className="px-6 py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {mutation.isPending ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Идёт консультация...
              </>
            ) : (
              'Начать консультацию'
            )}
          </button>
        </div>
      )}

      {/* Step 3: Result */}
      {step === 'result' && result && (
        <div className="space-y-4">
          <ConsultationResultCard result={result} />
          <button
            onClick={handleReset}
            className="px-4 py-2 text-sm text-medical-teal hover:bg-medical-teal/5 rounded-lg transition-colors"
          >
            Новая консультация
          </button>
        </div>
      )}
    </div>
  );
}
