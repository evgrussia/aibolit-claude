import { useState, useRef, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Search, User, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { usePatients } from '../hooks/usePatients';
import { formatDate, genderLabel } from '../utils/formatters';
import { Skeleton } from '../components/shared/Skeleton';
import ApiError from '../components/shared/ApiError';

function PatientListSkeleton() {
  return (
    <div className="space-y-2">
      {[1, 2, 3].map(i => (
        <div key={i} className="flex items-center gap-4 bg-white rounded-xl px-5 py-4 shadow-sm border border-gray-100">
          <Skeleton className="w-10 h-10 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-48" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function PatientListPage() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Cleanup debounce timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  const handleChange = useCallback((val: string) => {
    setQuery(val);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setDebouncedQuery(val), 300);
  }, []);

  const { data: patients = [], isLoading, error, refetch } = usePatients(debouncedQuery);

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-2xl font-bold text-gray-800">Пациенты</h1>
      </div>
      <p className="text-sm text-gray-500 mb-6">
        Картотека пациентов клиники. Нажмите на пациента, чтобы открыть карту с анализами, витальными и историей консультаций.
      </p>

      <div className="relative mb-2">
        <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
        <label htmlFor="patient-search" className="sr-only">Поиск пациента</label>
        <input
          id="patient-search"
          type="text"
          placeholder="Поиск по имени или фамилии (от 2 символов)..."
          value={query}
          onChange={e => handleChange(e.target.value)}
          className="w-full pl-10 pr-4 py-3 bg-white border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 focus:border-medical-teal text-sm"
        />
      </div>
      <p className="text-xs text-gray-400 mb-4">
        Пациенты добавляются через MCP-сервер (команда <code className="bg-gray-100 px-1 rounded">register_patient</code>) или API.
      </p>

      {isLoading ? (
        <PatientListSkeleton />
      ) : error ? (
        <ApiError message={(error as Error).message || 'Ошибка загрузки пациентов'} onRetry={() => refetch()} />
      ) : patients.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <User size={48} className="mx-auto mb-3 opacity-50" />
          <p>Пациенты не найдены</p>
        </div>
      ) : (
        <div className="space-y-2">
          {patients.map((p, i) => (
            <motion.div
              key={p.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link
                to={`/patients/${p.id}`}
                className="flex items-center gap-4 bg-white rounded-xl px-5 py-4 shadow-sm border border-gray-100 hover:shadow-md hover:border-medical-teal/30 transition-all group"
              >
                <div className="w-10 h-10 bg-medical-light rounded-full flex items-center justify-center shrink-0">
                  <User size={20} className="text-medical-navy" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-800 group-hover:text-medical-teal transition-colors">
                    {p.name}
                  </p>
                  <p className="text-sm text-gray-400">
                    {formatDate(p.dob)} &middot; {genderLabel(p.gender)}
                  </p>
                </div>
                <span className="text-xs text-gray-300 font-mono">{p.id}</span>
                <ChevronRight size={18} className="text-gray-300 group-hover:text-medical-teal transition-colors" />
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
