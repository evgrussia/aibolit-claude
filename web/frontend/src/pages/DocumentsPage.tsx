import { useState } from 'react';
import { FileText, ClipboardList, UserCheck, Upload } from 'lucide-react';
import PrescriptionTab from '../components/documents/PrescriptionTab';
import ReferralTab from '../components/documents/ReferralTab';
import MyDocumentsTab from '../components/documents/MyDocumentsTab';

const TABS = [
  { id: 'my-docs',      label: 'Мои документы', icon: <Upload size={16} /> },
  { id: 'prescription', label: 'Рецепт',        icon: <ClipboardList size={16} /> },
  { id: 'referral',     label: 'Направление',   icon: <UserCheck size={16} /> },
];

const descriptions: Record<string, string> = {
  'my-docs': 'Загрузка и хранение медицинских документов, анализов и снимков',
  prescription: 'Формирование листа назначений с перечнем препаратов и дозировок',
  referral: 'Оформление направления к специалисту с обоснованием',
};

export default function DocumentsPage() {
  const [tab, setTab] = useState('my-docs');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <FileText size={24} className="text-medical-teal" /> Документы
        </h1>
        <p className="text-sm text-gray-500 mt-1">{descriptions[tab]}</p>
      </div>

      <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit" role="tablist" aria-label="Типы документов">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            role="tab" aria-selected={tab === t.id}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.id ? 'bg-white shadow text-medical-navy' : 'text-gray-500 hover:text-gray-700'
            }`}>
            {t.icon}{t.label}
          </button>
        ))}
      </div>

      {tab === 'my-docs'      && <MyDocumentsTab />}
      {tab === 'prescription' && <PrescriptionTab />}
      {tab === 'referral'     && <ReferralTab />}
    </div>
  );
}
