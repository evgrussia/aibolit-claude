import { AlertCircle } from 'lucide-react';

interface Props {
  message: string;
  onRetry?: () => void;
}

export default function ApiError({ message, onRetry }: Props) {
  return (
    <div role="alert" className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
      <AlertCircle size={20} className="shrink-0" />
      <p className="text-sm flex-1">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="shrink-0 px-4 py-1.5 text-sm bg-red-100 hover:bg-red-200 rounded-lg transition-colors"
        >
          Повторить
        </button>
      )}
    </div>
  );
}
