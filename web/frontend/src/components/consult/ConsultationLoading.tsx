import { useState, useEffect } from 'react';
import { Stethoscope, Brain, FileSearch, ClipboardCheck } from 'lucide-react';

const STAGES = [
  { icon: FileSearch, label: 'Анализ жалоб и симптомов', delay: 0 },
  { icon: Brain, label: 'Дифференциальная диагностика', delay: 8 },
  { icon: Stethoscope, label: 'Формирование рекомендаций', delay: 20 },
  { icon: ClipboardCheck, label: 'Подготовка заключения', delay: 40 },
];

interface Props {
  specialtyName: string;
}

export default function ConsultationLoading({ specialtyName }: Props) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setElapsed(s => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const activeStage = STAGES.reduce(
    (acc, stage, i) => (elapsed >= stage.delay ? i : acc), 0,
  );

  return (
    <div className="max-w-md mx-auto py-8">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-medical-teal/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <Stethoscope size={32} className="text-medical-teal animate-pulse" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800">
          AI-{specialtyName} проводит консультацию
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Это может занять до 2 минут
        </p>
      </div>

      <div className="space-y-3">
        {STAGES.map((stage, i) => {
          const Icon = stage.icon;
          const isActive = i === activeStage;
          const isDone = i < activeStage;

          return (
            <div
              key={i}
              className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-500 ${
                isActive ? 'bg-medical-teal/5 border border-medical-teal/20' :
                isDone ? 'bg-gray-50' : 'opacity-40'
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                isActive ? 'bg-medical-teal/20' : isDone ? 'bg-emerald-100' : 'bg-gray-100'
              }`}>
                {isDone ? (
                  <svg className="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <Icon size={14} className={isActive ? 'text-medical-teal animate-pulse' : 'text-gray-400'} />
                )}
              </div>
              <span className={`text-sm ${
                isActive ? 'text-medical-teal font-medium' :
                isDone ? 'text-gray-600' : 'text-gray-400'
              }`}>
                {stage.label}
              </span>
              {isActive && (
                <div className="ml-auto flex gap-1">
                  <div className="w-1.5 h-1.5 bg-medical-teal rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1.5 h-1.5 bg-medical-teal rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1.5 h-1.5 bg-medical-teal rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="text-center mt-6">
        <span className="text-xs text-gray-400">
          {elapsed < 60 ? `${elapsed} сек` : `${Math.floor(elapsed / 60)}:${String(elapsed % 60).padStart(2, '0')}`}
        </span>
      </div>
    </div>
  );
}
