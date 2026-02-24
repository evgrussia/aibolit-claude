import { useState } from 'react';
import { Pill, Search, AlertTriangle } from 'lucide-react';
import DrugSearchSection from '../components/drugs/DrugSearchSection';
import InteractionSection from '../components/drugs/InteractionSection';

const TABS = [
  { id: 'search', label: 'Поиск препарата', icon: <Search size={16} /> },
  { id: 'interactions', label: 'Взаимодействия', icon: <AlertTriangle size={16} /> },
];

const descriptions: Record<string, string> = {
  search: 'Информация о препаратах из базы данных FDA — показания, дозировки, противопоказания',
  interactions: 'Проверка совместимости препаратов по локальной базе и RxNorm API',
};

export default function DrugToolsPage() {
  const [tab, setTab] = useState('search');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Pill size={22} className="text-medical-teal shrink-0" /> Лекарства
        </h1>
        <p className="text-sm text-gray-500 mt-1">{descriptions[tab]}</p>
      </div>

      <div className="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
        <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit" role="tablist" aria-label="Инструменты для лекарств">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              role="tab" aria-selected={tab === t.id}
              className={`flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all whitespace-nowrap ${
                tab === t.id ? 'bg-white shadow text-medical-navy' : 'text-gray-500 hover:text-gray-700'
              }`}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>
      </div>

      {tab === 'search'       && <DrugSearchSection />}
      {tab === 'interactions' && <InteractionSection />}
    </div>
  );
}
