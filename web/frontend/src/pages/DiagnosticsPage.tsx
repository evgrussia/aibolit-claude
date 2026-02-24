import { useState } from 'react';
import { Activity, FlaskConical, HeartPulse, Droplets, TrendingUp } from 'lucide-react';
import LabAnalysisTab from '../components/diagnostics/LabAnalysisTab';
import VitalsAssessTab from '../components/diagnostics/VitalsAssessTab';
import GfrCalculatorTab from '../components/diagnostics/GfrCalculatorTab';
import CvRiskTab from '../components/diagnostics/CvRiskTab';

const TABS = [
  { id: 'labs',    label: 'Анализы',     icon: <FlaskConical size={16} /> },
  { id: 'vitals',  label: 'Витальные',   icon: <HeartPulse size={16} /> },
  { id: 'gfr',     label: 'СКФ',         icon: <Droplets size={16} /> },
  { id: 'cvrisk',  label: 'СС-риск',     icon: <TrendingUp size={16} /> },
];

type TabId = 'labs' | 'vitals' | 'gfr' | 'cvrisk';

const TAB_DESCRIPTIONS: Record<TabId, string> = {
  labs: 'Интерпретация лабораторных показателей с выявлением паттернов заболеваний',
  vitals: 'Оценка витальных показателей по клиническим нормам с выявлением критических значений',
  gfr: 'Расчёт скорости клубочковой фильтрации по CKD-EPI — оценка функции почек',
  cvrisk: 'Оценка 10-летнего риска сердечно-сосудистых событий по модели SCORE2',
};

export default function DiagnosticsPage() {
  const [tab, setTab] = useState<TabId>('labs');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Activity size={22} className="text-medical-teal shrink-0" /> Диагностика
        </h1>
        <p className="text-sm text-gray-500 mt-1">{TAB_DESCRIPTIONS[tab]}</p>
      </div>

      <div className="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
        <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit" role="tablist" aria-label="Диагностические инструменты">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id as TabId)}
              role="tab" aria-selected={tab === t.id}
              className={`flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all whitespace-nowrap ${
                tab === t.id ? 'bg-white shadow text-medical-navy' : 'text-gray-500 hover:text-gray-700'
              }`}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>
      </div>

      {tab === 'labs'   && <LabAnalysisTab />}
      {tab === 'vitals' && <VitalsAssessTab />}
      {tab === 'gfr'    && <GfrCalculatorTab />}
      {tab === 'cvrisk' && <CvRiskTab />}
    </div>
  );
}
