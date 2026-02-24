import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, ArrowLeft, Sparkles } from 'lucide-react';
import { useSpecializations } from '../hooks/useSpecializations';
import { useAuth } from '../contexts/AuthContext';
import { triageComplaints, type TriageResult } from '../api/consultations';
import { createChat } from '../api/chat';
import type { ChatSSEHandler } from '../api/chat';
import SpecialtyGrid from '../components/consult/SpecialtyGrid';
import TriageResultComponent from '../components/consult/TriageResult';
import ConsultationLoading from '../components/consult/ConsultationLoading';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import ApiError from '../components/shared/ApiError';
import { useToast } from '../contexts/ToastContext';
import type { Specialization } from '../types/patient';

type Step = 'complaint' | 'triage' | 'specialty' | 'loading';

const STEP_LABELS: Record<Step, string> = {
  complaint: 'Жалобы',
  triage: 'Рекомендации',
  specialty: 'Специалист',
  loading: 'Создание чата',
};

const STEP_ORDER: Step[] = ['complaint', 'triage', 'specialty', 'loading'];

export default function ConsultDoctorPage() {
  const [step, setStep] = useState<Step>('complaint');
  const [complaints, setComplaints] = useState('');
  const [triageResult, setTriageResult] = useState<TriageResult | null>(null);
  const [selected, setSelected] = useState<Specialization | null>(null);
  const [triageLoading, setTriageLoading] = useState(false);

  const { data: specializations = [], isLoading, error, refetch } = useSpecializations();
  useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleTriage = useCallback(async () => {
    if (!complaints.trim()) return;
    setTriageLoading(true);
    try {
      const res = await triageComplaints(complaints.trim());
      setTriageResult(res);
      setStep('triage');
    } catch (err) {
      toast.error((err as Error).message || 'Ошибка анализа жалоб');
    } finally {
      setTriageLoading(false);
    }
  }, [complaints, toast]);

  const startChat = useCallback(async (spec: Specialization) => {
    setStep('loading');
    try {
      let consultationId: number | null = null;
      const handlers: ChatSSEHandler = {
        onMeta: (data) => {
          if (data.consultation_id) consultationId = data.consultation_id;
        },
      };
      // Create chat — this starts streaming, but we just need the consultation_id
      // then redirect. The chat page will pick up from there.
      const ac = new AbortController();
      const promise = createChat(spec.id, complaints.trim(), handlers, ac.signal);
      // Wait a bit for meta event with consultation_id, then abort and redirect
      const timeout = setTimeout(() => {
        if (consultationId) {
          ac.abort();
          navigate(`/chat/${consultationId}`, { replace: true });
        }
      }, 2000);

      await promise.catch(() => {});
      clearTimeout(timeout);

      // If we got the consultation_id (stream completed or was aborted), navigate
      if (consultationId) {
        navigate(`/chat/${consultationId}`, { replace: true });
      } else {
        toast.error('Не удалось создать чат');
        setStep(triageResult ? 'triage' : 'complaint');
      }
    } catch (err) {
      const msg = (err as Error).message || '';
      toast.error(msg || 'Ошибка при создании чата');
      setStep(triageResult ? 'triage' : 'complaint');
    }
  }, [complaints, triageResult, toast, navigate]);

  const handleSelectFromTriage = useCallback((specialtyId: string) => {
    const spec = specializations.find(s => s.id === specialtyId);
    if (spec) {
      setSelected(spec);
      startChat(spec);
    }
  }, [specializations, startChat]);

  const handleSelectSpecialty = useCallback((spec: Specialization) => {
    setSelected(spec);
    startChat(spec);
  }, [startChat]);

  const handleBack = () => {
    if (step === 'specialty') setStep('triage');
    else if (step === 'triage') setStep('complaint');
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ApiError message={(error as Error).message} onRetry={() => refetch()} />;

  const stepIdx = STEP_ORDER.indexOf(step);
  const visibleSteps: Step[] = ['complaint', 'triage', 'specialty', 'loading'];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        {step !== 'complaint' && step !== 'loading' && (
          <button onClick={handleBack} className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500">
            <ArrowLeft size={20} />
          </button>
        )}
        <h1 className="text-xl sm:text-2xl font-bold text-gray-800 flex items-center gap-2">
          <MessageSquare size={22} className="text-medical-teal shrink-0" />
          AI Консультация
        </h1>
      </div>

      {/* Step indicators */}
      <div className="flex items-center gap-1.5 sm:gap-2 text-sm overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
        {visibleSteps.map((s, i) => {
          const isActive = s === step;
          const isPast = stepIdx > STEP_ORDER.indexOf(s);
          return (
            <div key={s} className="flex items-center gap-1.5 sm:gap-2 shrink-0">
              {i > 0 && <div className={`w-4 sm:w-8 h-px ${isPast || isActive ? 'bg-medical-teal' : 'bg-gray-200'}`} />}
              <div className={`flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 rounded-full text-[10px] sm:text-xs font-medium whitespace-nowrap ${
                isActive ? 'bg-medical-teal text-white' :
                isPast ? 'bg-medical-teal/10 text-medical-teal' : 'bg-gray-100 text-gray-400'
              }`}>
                <span>{i + 1}</span>
                <span className="hidden xs:inline sm:inline">{STEP_LABELS[s]}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Step 1: Complaint input (now first) */}
      {step === 'complaint' && (
        <div className="max-w-2xl space-y-6">
          <div className="bg-medical-teal/5 border border-medical-teal/20 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles size={16} className="text-medical-teal" />
              <span className="text-sm font-medium text-gray-800">Ресепшн клиники Aibolit</span>
            </div>
            <p className="text-sm text-gray-600">
              Опишите свои жалобы и симптомы. AI-система проанализирует их и подберёт
              подходящего специалиста. Вы также можете выбрать врача самостоятельно.
            </p>
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
              placeholder="Опишите: что беспокоит, когда началось, что усиливает/ослабляет, есть ли сопутствующие симптомы..."
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 resize-none"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleTriage}
              disabled={!complaints.trim() || triageLoading}
              className="px-6 py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
            >
              {triageLoading ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Анализирую...
                </>
              ) : (
                'Подобрать специалиста'
              )}
            </button>
            <button
              onClick={() => setStep('specialty')}
              disabled={!complaints.trim()}
              className="px-4 py-2.5 text-gray-600 hover:bg-gray-100 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              Выбрать врача самостоятельно
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Triage results */}
      {step === 'triage' && triageResult && (
        <div className="max-w-2xl space-y-4">
          <div className="p-3 bg-gray-50 rounded-lg">
            <span className="text-xs text-gray-500">Ваши жалобы:</span>
            <p className="text-sm text-gray-700 mt-0.5">{complaints}</p>
          </div>
          <TriageResultComponent result={triageResult} onSelectSpecialty={handleSelectFromTriage} />
          <button
            onClick={() => setStep('specialty')}
            className="text-sm text-gray-500 hover:text-medical-teal transition-colors"
          >
            Показать всех специалистов
          </button>
        </div>
      )}

      {/* Step 3: Full specialty picker (manual selection) */}
      {step === 'specialty' && (
        <SpecialtyGrid specializations={specializations} onSelect={handleSelectSpecialty} />
      )}

      {/* Loading: Creating chat */}
      {step === 'loading' && selected && (
        <ConsultationLoading specialtyName={selected.name_ru} />
      )}
    </div>
  );
}
