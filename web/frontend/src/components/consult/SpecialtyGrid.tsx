import { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import type { Specialization } from '../../types/patient';

interface Props {
  specializations: Specialization[];
  onSelect: (spec: Specialization) => void;
}

const CATEGORIES: Record<string, string[]> = {
  'Терапевтические': [
    'therapist', 'cardiologist', 'neurologist', 'pulmonologist', 'gastroenterologist',
    'endocrinologist', 'nephrologist', 'rheumatologist', 'hematologist', 'infectionist',
    'allergist', 'geriatrician',
  ],
  'Хирургические': [
    'surgeon', 'cardiac_surgeon', 'neurosurgeon', 'vascular_surgeon', 'orthopedist', 'urologist',
  ],
  'Диагностические': [
    'radiologist', 'pathologist', 'pharmacologist', 'geneticist',
  ],
  'Специализированные': [
    'dermatologist', 'ophthalmologist', 'ent', 'gynecologist', 'psychiatrist', 'dentist',
    'oncologist',
  ],
  'Другие': [
    'pediatrician', 'emergency', 'intensivist', 'rehabilitation', 'nutritionist', 'sports_medicine',
  ],
};

export default function SpecialtyGrid({ specializations, onSelect }: Props) {
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search) return specializations;
    const q = search.toLowerCase();
    return specializations.filter(
      s => s.name_ru.toLowerCase().includes(q) || s.name_en.toLowerCase().includes(q) || s.description.toLowerCase().includes(q),
    );
  }, [specializations, search]);

  const grouped = useMemo(() => {
    const result: { category: string; items: Specialization[] }[] = [];
    const filteredIds = new Set(filtered.map(s => s.id));

    for (const [category, ids] of Object.entries(CATEGORIES)) {
      const items = ids
        .map(id => filtered.find(s => s.id === id))
        .filter((s): s is Specialization => !!s && filteredIds.has(s.id));
      if (items.length > 0) {
        result.push({ category, items });
      }
    }

    // Any not categorized
    const allCategorized = new Set(Object.values(CATEGORIES).flat());
    const uncategorized = filtered.filter(s => !allCategorized.has(s.id));
    if (uncategorized.length > 0) {
      const existing = result.find(g => g.category === 'Другие');
      if (existing) existing.items.push(...uncategorized);
      else result.push({ category: 'Другие', items: uncategorized });
    }

    return result;
  }, [filtered]);

  return (
    <div className="space-y-6">
      <div className="relative">
        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Поиск специалиста..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 focus:border-medical-teal"
        />
      </div>

      {grouped.length === 0 ? (
        <p className="text-gray-400 text-sm text-center py-8">Ничего не найдено</p>
      ) : (
        grouped.map(group => (
          <div key={group.category}>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              {group.category}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {group.items.map(spec => (
                <button
                  key={spec.id}
                  onClick={() => onSelect(spec)}
                  className="text-left p-4 rounded-xl border border-gray-100 hover:border-medical-teal/40 hover:shadow-md transition-all bg-white group"
                >
                  <div className="font-medium text-gray-800 group-hover:text-medical-teal transition-colors">
                    {spec.name_ru}
                  </div>
                  <p className="text-xs text-gray-400 mt-0.5">{spec.name_en}</p>
                  <p className="text-xs text-gray-500 mt-2 line-clamp-2">{spec.description}</p>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {spec.skills.slice(0, 3).map(s => (
                      <span key={s.name} className="text-[10px] px-1.5 py-0.5 rounded bg-gray-50 text-gray-400">
                        {s.name}
                      </span>
                    ))}
                    {spec.skills.length > 3 && (
                      <span className="text-[10px] text-gray-400">+{spec.skills.length - 3}</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
