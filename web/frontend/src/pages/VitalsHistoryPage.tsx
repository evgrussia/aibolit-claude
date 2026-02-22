import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { usePatient } from '../hooks/usePatient';
import { usePatientMutations } from '../hooks/usePatientMutations';
import { useToast } from '../contexts/ToastContext';
import BloodPressureChart from '../components/charts/BloodPressureChart';
import Card from '../components/shared/Card';
import Modal from '../components/shared/Modal';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import ApiError from '../components/shared/ApiError';
import AddVitalsForm from '../components/forms/AddVitalsForm';
import { HeartPulse, Plus } from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

export default function VitalsHistoryPage() {
  const { patientId } = useParams();
  const { data: patient, isLoading, error, refetch } = usePatient(patientId);
  const [showForm, setShowForm] = useState(false);
  const mutations = usePatientMutations(patientId);
  const toast = useToast();

  const handleSubmit = async (data: Record<string, unknown>) => {
    try {
      await mutations.vitals.mutateAsync(data);
      toast.success('Витальные показатели записаны');
      setShowForm(false);
    } catch (err) {
      toast.error((err as Error).message || 'Ошибка сохранения');
    }
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ApiError message={(error as Error).message || 'Ошибка загрузки'} onRetry={() => refetch()} />;
  if (!patient) return <p className="text-center text-gray-400 py-12">Пациент не найден</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <HeartPulse size={24} className="text-medical-teal" /> Витальные показатели
        </h1>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-medical-teal text-white rounded-lg text-sm font-medium hover:bg-medical-teal/90 transition-colors"
        >
          <Plus size={14} /> Записать показатели
        </button>
      </div>

      <BloodPressureChart data={patient.vitals_history} />

      <Card title="История измерений" icon={<HeartPulse size={18} />}>
        {patient.vitals_history.length === 0 ? (
          <p className="text-gray-400 text-sm">Нет записей</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <caption className="sr-only">История витальных показателей</caption>
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-100">
                  <th scope="col" className="pb-3 font-medium">Дата</th>
                  <th scope="col" className="pb-3 font-medium">АД</th>
                  <th scope="col" className="pb-3 font-medium">Пульс</th>
                  <th scope="col" className="pb-3 font-medium">Темп.</th>
                  <th scope="col" className="pb-3 font-medium">SpO2</th>
                  <th scope="col" className="pb-3 font-medium">ЧД</th>
                  <th scope="col" className="pb-3 font-medium">Глюк.</th>
                </tr>
              </thead>
              <tbody>
                {patient.vitals_history.map((v, i) => (
                  <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/50">
                    <td className="py-2.5 text-gray-600">{formatDateTime(v.timestamp)}</td>
                    <td className="py-2.5 font-mono">
                      {v.systolic_bp && v.diastolic_bp ? `${v.systolic_bp}/${v.diastolic_bp}` : '—'}
                    </td>
                    <td className="py-2.5 font-mono">{v.heart_rate ?? '—'}</td>
                    <td className="py-2.5 font-mono">{v.temperature?.toFixed(1) ?? '—'}</td>
                    <td className="py-2.5 font-mono">{v.spo2 ?? '—'}%</td>
                    <td className="py-2.5 font-mono">{v.respiratory_rate ?? '—'}</td>
                    <td className="py-2.5 font-mono">{v.blood_glucose ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="Записать витальные показатели">
        <AddVitalsForm onSubmit={handleSubmit} isPending={mutations.vitals.isPending} />
      </Modal>
    </div>
  );
}
