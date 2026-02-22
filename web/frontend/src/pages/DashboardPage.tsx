import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { usePatient } from '../hooks/usePatient';
import { usePatientMutations } from '../hooks/usePatientMutations';
import { useToast } from '../contexts/ToastContext';
import PatientCard from '../components/patients/PatientCard';
import DiagnosesList from '../components/patients/DiagnosesList';
import MedicationsList from '../components/patients/MedicationsList';
import VitalsGauges from '../components/patients/VitalsGauges';
import { PatientCardSkeleton, Skeleton } from '../components/shared/Skeleton';
import Card from '../components/shared/Card';
import Modal from '../components/shared/Modal';
import ApiError from '../components/shared/ApiError';
import AddVitalsForm from '../components/forms/AddVitalsForm';
import AddDiagnosisForm from '../components/forms/AddDiagnosisForm';
import AddMedicationForm from '../components/forms/AddMedicationForm';
import AddAllergyForm from '../components/forms/AddAllergyForm';
import EditProfileForm from '../components/forms/EditProfileForm';
import ConfirmDialog from '../components/shared/ConfirmDialog';
import {
  FileText, Plus, MessageSquare, ShieldAlert, Pill, HeartPulse,
  AlertTriangle, Clock, UserCog, Trash2,
} from 'lucide-react';

type ModalType = 'vitals' | 'diagnosis' | 'medication' | 'allergy' | 'profile' | null;

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <PatientCardSkeleton />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-md border border-gray-100 p-5 space-y-3">
          <Skeleton className="h-4 w-1/4 mb-4" />
          <div className="grid grid-cols-2 gap-4">
            {[1,2,3,4].map(i => <Skeleton key={i} className="h-20 rounded-full mx-auto w-20" />)}
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-md border border-gray-100 p-5 space-y-2">
          <Skeleton className="h-4 w-1/4 mb-4" />
          {[1,2,3,4,5].map(i => <Skeleton key={i} className="h-8" />)}
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ icon, label, value, color, to }: {
  icon: React.ReactNode; label: string; value: string | number; color: string; to: string;
}) {
  return (
    <Link to={to} className="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
          {icon}
        </div>
        <div>
          <div className="text-xl font-bold text-gray-800">{value}</div>
          <div className="text-xs text-gray-400">{label}</div>
        </div>
      </div>
    </Link>
  );
}

export default function DashboardPage() {
  const { patientId } = useParams();
  const { data: patient, isLoading, error, refetch } = usePatient(patientId);
  const mutations = usePatientMutations(patientId);
  const toast = useToast();
  const [modal, setModal] = useState<ModalType>(null);
  const [deleteTarget, setDeleteTarget] = useState<{ table: string; id: number; label: string } | null>(null);

  const closeModal = () => setModal(null);

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      await mutations.deleteRecord.mutateAsync({ table: deleteTarget.table, recordId: deleteTarget.id });
      toast.success(`${deleteTarget.label} удалено`);
      setDeleteTarget(null);
    } catch (err) {
      toast.error((err as Error).message || 'Ошибка удаления');
    }
  };

  const makeSubmitHandler = (
    mutationFn: { mutateAsync: (data: Record<string, unknown>) => Promise<unknown> },
    successMsg: string,
  ) => {
    return async (data: Record<string, unknown>) => {
      try {
        await mutationFn.mutateAsync(data);
        toast.success(successMsg);
        closeModal();
      } catch (err) {
        toast.error((err as Error).message || 'Ошибка сохранения');
      }
    };
  };

  if (isLoading) return <DashboardSkeleton />;
  if (error) return <ApiError message={(error as Error).message || 'Ошибка загрузки'} onRetry={() => refetch()} />;
  if (!patient) return <p className="text-center text-gray-400 py-12">Пациент не найден</p>;

  const latestVitals = patient.vitals_history.length > 0
    ? patient.vitals_history[patient.vitals_history.length - 1]
    : null;

  const activeDiagnoses = patient.diagnoses.filter(d => d.status === 'active' || d.status === 'chronic').length;

  return (
    <div className="space-y-6">
      {/* Patient card with edit button */}
      <div className="relative">
        <PatientCard patient={patient} />
        <button
          onClick={() => setModal('profile')}
          className="absolute top-4 right-4 p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors"
          title="Редактировать профиль"
        >
          <UserCog size={18} />
        </button>
      </div>

      {/* Summary row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <SummaryCard
          icon={<ShieldAlert size={20} className="text-red-500" />}
          label="Активных диагнозов"
          value={activeDiagnoses}
          color={activeDiagnoses > 0 ? 'bg-red-50' : 'bg-gray-50'}
          to={`/patients/${patientId}`}
        />
        <SummaryCard
          icon={<Pill size={20} className="text-emerald-500" />}
          label="Препаратов"
          value={patient.medications.length}
          color="bg-emerald-50"
          to={`/patients/${patientId}`}
        />
        <SummaryCard
          icon={<HeartPulse size={20} className="text-rose-500" />}
          label="Последние витальные"
          value={latestVitals ? new Date(latestVitals.timestamp).toLocaleDateString('ru-RU') : '—'}
          color="bg-rose-50"
          to={`/patients/${patientId}/vitals`}
        />
        <SummaryCard
          icon={<Clock size={20} className="text-blue-500" />}
          label="Хронология"
          value=">"
          color="bg-blue-50"
          to={`/patients/${patientId}/timeline`}
        />
      </div>

      {/* Consult button */}
      <Link
        to={`/consult`}
        className="flex items-center gap-3 w-full p-4 bg-gradient-to-r from-medical-teal/10 to-blue-50 border border-medical-teal/20 rounded-xl hover:shadow-md transition-shadow"
      >
        <div className="w-10 h-10 bg-medical-teal/20 rounded-lg flex items-center justify-center">
          <MessageSquare size={20} className="text-medical-teal" />
        </div>
        <div>
          <div className="font-medium text-gray-800">AI Консультация</div>
          <p className="text-xs text-gray-500">Обратиться к AI-специалисту с жалобами</p>
        </div>
      </Link>

      {/* Vitals + Diagnoses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="relative">
          <VitalsGauges vitals={latestVitals} />
          <button
            onClick={() => setModal('vitals')}
            className="absolute top-3.5 right-5 p-1 rounded-md hover:bg-medical-teal/10 text-medical-teal transition-colors"
            title="Записать показатели"
          >
            <Plus size={16} />
          </button>
        </div>

        <div className="relative">
          <DiagnosesList
            diagnoses={patient.diagnoses}
            compact
            onDelete={(id) => setDeleteTarget({ table: 'diagnoses', id, label: 'Диагноз' })}
          />
          <button
            onClick={() => setModal('diagnosis')}
            className="absolute top-3.5 right-5 p-1 rounded-md hover:bg-medical-teal/10 text-medical-teal transition-colors"
            title="Добавить диагноз"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      {/* Medications + Allergies */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="relative">
          <MedicationsList
            medications={patient.medications}
            onDelete={(id) => setDeleteTarget({ table: 'medications', id, label: 'Препарат' })}
          />
          <button
            onClick={() => setModal('medication')}
            className="absolute top-3.5 right-5 p-1 rounded-md hover:bg-medical-teal/10 text-medical-teal transition-colors"
            title="Назначить лекарство"
          >
            <Plus size={16} />
          </button>
        </div>

        <div className="relative">
          <Card title="Аллергии" icon={<AlertTriangle size={18} />}>
            {patient.allergies.length === 0 ? (
              <p className="text-gray-400 text-sm">Нет аллергий</p>
            ) : (
              <div className="space-y-2">
                {patient.allergies.map((a, i) => (
                  <div key={a.id ?? i} className="flex items-center justify-between py-1.5 border-b border-gray-50 last:border-0">
                    <div>
                      <span className="text-sm font-medium text-gray-700">{a.substance}</span>
                      {a.reaction && <span className="text-xs text-gray-400 ml-2">{a.reaction}</span>}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        a.severity === 'severe' ? 'bg-red-100 text-red-700' :
                        a.severity === 'moderate' ? 'bg-amber-100 text-amber-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {a.severity === 'severe' ? 'Тяжёлая' : a.severity === 'moderate' ? 'Умеренная' : 'Лёгкая'}
                      </span>
                      {a.id != null && (
                        <button
                          onClick={() => setDeleteTarget({ table: 'allergies', id: a.id!, label: `Аллергия "${a.substance}"` })}
                          className="p-1 rounded hover:bg-red-50 text-gray-300 hover:text-red-500 transition-colors"
                          title="Удалить"
                        >
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
          <button
            onClick={() => setModal('allergy')}
            className="absolute top-3.5 right-5 p-1 rounded-md hover:bg-medical-teal/10 text-medical-teal transition-colors"
            title="Добавить аллергию"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      {/* Family history + Notes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Семейный анамнез" icon={<FileText size={18} />}>
          {patient.family_history.length === 0 ? (
            <p className="text-gray-400 text-sm">Не указан</p>
          ) : (
            <ul className="space-y-1.5">
              {patient.family_history.map((h, i) => (
                <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="text-medical-teal mt-0.5">-</span> {h}
                </li>
              ))}
            </ul>
          )}
        </Card>

        {patient.notes && (
          <Card title="Заметки">
            <p className="text-sm text-gray-600 whitespace-pre-wrap">{patient.notes}</p>
          </Card>
        )}
      </div>

      {/* Modals */}
      <Modal isOpen={modal === 'vitals'} onClose={closeModal} title="Записать витальные показатели">
        <AddVitalsForm
          onSubmit={makeSubmitHandler(mutations.vitals, 'Показатели записаны')}
          isPending={mutations.vitals.isPending}
        />
      </Modal>

      <Modal isOpen={modal === 'diagnosis'} onClose={closeModal} title="Добавить диагноз">
        <AddDiagnosisForm
          onSubmit={makeSubmitHandler(mutations.diagnosis, 'Диагноз добавлен')}
          isPending={mutations.diagnosis.isPending}
        />
      </Modal>

      <Modal isOpen={modal === 'medication'} onClose={closeModal} title="Назначить лекарство">
        <AddMedicationForm
          onSubmit={makeSubmitHandler(mutations.medication, 'Препарат назначен')}
          isPending={mutations.medication.isPending}
        />
      </Modal>

      <Modal isOpen={modal === 'allergy'} onClose={closeModal} title="Добавить аллергию">
        <AddAllergyForm
          onSubmit={makeSubmitHandler(mutations.allergy, 'Аллергия добавлена')}
          isPending={mutations.allergy.isPending}
        />
      </Modal>

      <Modal isOpen={modal === 'profile'} onClose={closeModal} title="Редактировать профиль">
        <EditProfileForm
          patient={patient}
          onSubmit={makeSubmitHandler(mutations.profile, 'Профиль обновлён')}
          isPending={mutations.profile.isPending}
        />
      </Modal>

      <ConfirmDialog
        isOpen={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        title="Подтвердите удаление"
        message={`Вы уверены, что хотите удалить: ${deleteTarget?.label ?? ''}?`}
        isPending={mutations.deleteRecord.isPending}
      />
    </div>
  );
}
