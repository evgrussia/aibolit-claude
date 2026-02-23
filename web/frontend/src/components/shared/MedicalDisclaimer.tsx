import { AlertTriangle } from 'lucide-react';

const DISCLAIMER_TEXTS: Record<string, string> = {
  general:
    'Информация предоставлена AI-ассистентом и носит исключительно информационный характер. Не является медицинской консультацией, диагнозом или назначением лечения. Обратитесь к врачу для получения квалифицированной медицинской помощи.',
  lab_analysis:
    'Расшифровка анализов выполнена AI-системой и требует подтверждения врачом. Отклонения от нормы не обязательно означают заболевание. Врач интерпретирует результаты в контексте вашего состояния.',
  diagnosis:
    'Предположительный анализ симптомов выполнен AI-системой. Это НЕ диагноз. Только врач может поставить диагноз на основе полного обследования. Обратитесь к специалисту.',
  medication:
    'Информация о лекарственных препаратах носит справочный характер. AI НЕ назначает лекарства. Перед приёмом любых препаратов проконсультируйтесь с врачом.',
};

interface Props {
  type?: keyof typeof DISCLAIMER_TEXTS;
  text?: string;
  className?: string;
}

export default function MedicalDisclaimer({ type = 'general', text, className = '' }: Props) {
  const content = text || DISCLAIMER_TEXTS[type] || DISCLAIMER_TEXTS.general;

  return (
    <div className={`flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 ${className}`}>
      <AlertTriangle size={16} className="text-amber-500 shrink-0 mt-0.5" />
      <p className="text-xs text-amber-700">{content}</p>
    </div>
  );
}
