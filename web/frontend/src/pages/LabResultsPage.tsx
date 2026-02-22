import { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { usePatient } from '../hooks/usePatient';
import { useLabTrends } from '../hooks/useLabTrends';
import { usePatientMutations } from '../hooks/usePatientMutations';
import { useToast } from '../contexts/ToastContext';
import LabTrendChart from '../components/charts/LabTrendChart';
import Card from '../components/shared/Card';
import Badge from '../components/shared/Badge';
import Modal from '../components/shared/Modal';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import ApiError from '../components/shared/ApiError';
import AddLabResultForm from '../components/forms/AddLabResultForm';
import ConfirmDialog from '../components/shared/ConfirmDialog';
import { FlaskConical, TrendingUp, Plus, Trash2 } from 'lucide-react';
import { formatDate } from '../utils/formatters';
import type { LabResult } from '../types/patient';

export default function LabResultsPage() {
  const { patientId } = useParams();
  const { data: patient, isLoading, error, refetch } = usePatient(patientId);
  const [selectedTest, setSelectedTest] = useState('');
  const { data: trendData = [] } = useLabTrends(patientId, selectedTest);
  const [showForm, setShowForm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; label: string } | null>(null);
  const mutations = usePatientMutations(patientId);
  const toast = useToast();

  const testNames = useMemo(
    () => patient ? [...new Set(patient.lab_results.map(lr => lr.test_name))] : [],
    [patient]
  );

  const handleSubmit = async (data: Record<string, unknown>) => {
    try {
      await mutations.lab.mutateAsync(data);
      toast.success('Результат анализа добавлен');
      setShowForm(false);
    } catch (err) {
      toast.error((err as Error).message || 'Ошибка сохранения');
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await mutations.deleteRecord.mutateAsync({ table: 'lab_results', recordId: deleteTarget.id });
      toast.success('Результат удалён');
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
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <FlaskConical size={24} className="text-medical-teal" /> Анализы
        </h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-400">{patient.lab_results.length} результатов</span>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-medical-teal text-white rounded-lg text-sm font-medium hover:bg-medical-teal/90 transition-colors"
          >
            <Plus size={14} /> Добавить результат
          </button>
        </div>
      </div>

      <Card title="Динамика показателя" icon={<TrendingUp size={18} />}>
        <div className="mb-4">
          <label htmlFor="lab-test-select" className="sr-only">Выбор анализа</label>
          <select
            id="lab-test-select"
            value={selectedTest}
            onChange={e => setSelectedTest(e.target.value)}
            className="w-full md:w-80 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30"
          >
            <option value="">Выберите анализ для графика...</option>
            {testNames.map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>
        {selectedTest && trendData.length > 0 ? (
          <LabTrendChart data={trendData as never[]} title={selectedTest} />
        ) : selectedTest ? (
          <p className="text-gray-400 text-sm">Нет данных для построения графика</p>
        ) : null}
      </Card>

      <Card title="Все результаты" icon={<FlaskConical size={18} />}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <caption className="sr-only">Результаты лабораторных исследований</caption>
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-100">
                <th scope="col" className="pb-3 font-medium">Анализ</th>
                <th scope="col" className="pb-3 font-medium">Значение</th>
                <th scope="col" className="pb-3 font-medium">Ед.</th>
                <th scope="col" className="pb-3 font-medium">Норма</th>
                <th scope="col" className="pb-3 font-medium">Дата</th>
                <th scope="col" className="pb-3 font-medium">Статус</th>
                <th scope="col" className="pb-3 font-medium w-10"></th>
              </tr>
            </thead>
            <tbody>
              {patient.lab_results.map((lr: LabResult, i: number) => (
                <tr key={lr.id ?? i} className="border-b border-gray-50 hover:bg-gray-50/50">
                  <td className="py-2.5 font-medium text-gray-700 max-w-xs truncate">{lr.test_name}</td>
                  <td className="py-2.5 font-mono">{lr.value}</td>
                  <td className="py-2.5 text-gray-400">{lr.unit}</td>
                  <td className="py-2.5 text-gray-400 text-xs">{lr.reference_range}</td>
                  <td className="py-2.5 text-gray-400">{formatDate(lr.date)}</td>
                  <td className="py-2.5">
                    <Badge variant={lr.is_abnormal ? 'danger' : 'success'}>
                      {lr.is_abnormal ? 'Отклонение' : 'Норма'}
                    </Badge>
                  </td>
                  <td className="py-2.5">
                    {lr.id != null && (
                      <button
                        onClick={() => setDeleteTarget({ id: lr.id!, label: lr.test_name })}
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
      </Card>

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="Добавить результат анализа">
        <AddLabResultForm onSubmit={handleSubmit} isPending={mutations.lab.isPending} />
      </Modal>

      <ConfirmDialog
        isOpen={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Удалить результат анализа"
        message={`Удалить результат "${deleteTarget?.label ?? ''}"?`}
        isPending={mutations.deleteRecord.isPending}
      />
    </div>
  );
}
