import { Phone } from 'lucide-react';

interface Props {
  message?: string;
  className?: string;
}

export default function EmergencyBanner({
  message = 'Обнаружены критические показатели, требующие экстренной медицинской помощи!',
  className = '',
}: Props) {
  return (
    <div role="alert" className={`p-4 bg-red-50 border-2 border-red-300 rounded-xl ${className}`}>
      <div className="flex items-center gap-3 mb-2">
        <Phone size={20} className="text-red-600 shrink-0" />
        <p className="text-red-700 font-bold text-sm">{message}</p>
      </div>
      <div className="flex items-center gap-4 ml-8">
        <a
          href="tel:103"
          className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-red-600 text-white rounded-lg text-sm font-semibold hover:bg-red-700 transition-colors"
        >
          <Phone size={14} />
          103
        </a>
        <a
          href="tel:112"
          className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-red-600 text-white rounded-lg text-sm font-semibold hover:bg-red-700 transition-colors"
        >
          <Phone size={14} />
          112
        </a>
        <span className="text-xs text-red-600">
          Немедленно вызовите скорую помощь!
        </span>
      </div>
    </div>
  );
}
