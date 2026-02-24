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
import ConfirmDialog from '../components/shared/ConfirmDialog';
import { HeartPulse, Plus, Trash2 } from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

export default function VitalsHistoryPage() {
  const { patientId } = useParams();
  const { data: patient, isLoading, error, refetch } = usePatient(patientId);
  const [showForm, setShowForm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; label: string } | null>(null);
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

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await mutations.deleteRecord.mutateAsync({ table: 'vitals', recordId: deleteTarget.id });
      toast.success('Запись удалена');
      setDeleteTarget(null);
    } catch (err) {
      toast.error((err as Error).message || 'Ошибка удаления');
    }
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ApiError message={(error as Error).message || 'Ошибка загрузки'} onRetry={() => refetch()} />;
  if (!patient) return <p className="text-center text-gray-400 py-12">Пациент не найден</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-800 flex items-center gap-2 min-w-0">
          <HeartPulse size={22} className="text-medical-teal shrink-0" /> <span className="truncate">Витальные</span>
        </h1>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 bg-medical-teal text-white rounded-lg text-xs sm:text-sm font-medium hover:bg-medical-teal/90 transition-colors shrink-0"
        >
          <Plus size={14} /> <span className="hidden sm:inline">Записать</span><span className="sm:hidden">+</span>
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
                  <th scope="col" className="pb-3 font-medium w-10"></th>
                </tr>
              </thead>
              <tbody>
                {patient.vitals_history.map((v, i) => (
                  <tr key={v.id ?? i} className="border-b border-gray-50 hover:bg-gray-50/50">
                    <td className="py-2.5 text-gray-600">{formatDateTime(v.timestamp)}</td>
                    <td className="py-2.5 font-mono">
                      {v.systolic_bp && v.diastolic_bp ? `${v.systolic_bp}/${v.diastolic_bp}` : '—'}
                    </td>
                    <td className="py-2.5 font-mono">{v.heart_rate ?? '—'}</td>
                    <td className="py-2.5 font-mono">{v.temperature?.toFixed(1) ?? '—'}</td>
                    <td className="py-2.5 font-mono">{v.spo2 ?? '—'}%</td>
                    <td className="py-2.5 font-mono">{v.respiratory_rate ?? '—'}</td>
                    <td className="py-2.5 font-mono">{v.blood_glucose ?? '—'}</td>
                    <td className="py-2.5">
                      {v.id != null && (
                        <button
                          onClick={() => setDeleteTarget({ id: v.id!, label: formatDateTime(v.timestamp) })}
                          className="p-1 rounded hover:bg-red-50 text-gray-300 hover:text-red-500 transition-colors"
                          title="Удалить"
                        >
                          <Trash2 size={14} />
                        </button>
                      )}
                    </td>
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

      <ConfirmDialog
        isOpen={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Удалить запись"
        message={`Удалить показатели от ${deleteTarget?.label ?? ''}?`}
        isPending={mutations.deleteRecord.isPending}
      />
    </div>
  );
}
