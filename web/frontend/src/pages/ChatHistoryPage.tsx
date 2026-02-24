import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { MessageCircle, Plus, Stethoscope, Clock, ChevronRight } from 'lucide-react';
import clsx from 'clsx';
import { getMyChats } from '../api/chat';
import type { ChatConsultation } from '../types/patient';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import ApiError from '../components/shared/ApiError';

export default function ChatHistoryPage() {
  const navigate = useNavigate();
  const [chats, setChats] = useState<ChatConsultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await getMyChats();
        if (!cancelled) setChats(data);
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ApiError message={error} onRetry={() => window.location.reload()} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-800 flex items-center gap-2 min-w-0">
          <MessageCircle size={22} className="text-medical-teal shrink-0" />
          <span className="truncate">Мои консультации</span>
        </h1>
        <Link
          to="/consult"
          className="flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 bg-medical-teal text-white rounded-lg text-xs sm:text-sm font-medium hover:bg-medical-teal/90 transition-colors shrink-0"
        >
          <Plus size={14} />
          <span className="hidden sm:inline">Новая</span>
          <span className="sm:hidden">+</span>
        </Link>
      </div>

      {chats.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <MessageCircle size={28} className="text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-700 mb-2">Нет консультаций</h3>
          <p className="text-sm text-gray-500 mb-4">
            Начните первую AI-консультацию с врачом
          </p>
          <Link
            to="/consult"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-medical-teal text-white rounded-lg text-sm font-medium hover:bg-medical-teal/90 transition-colors"
          >
            <Stethoscope size={16} />
            Начать консультацию
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {chats.map(chat => (
            <ChatCard key={chat.id} chat={chat} onClick={() => {
              if (chat.status === 'legacy') return; // legacy chats can't be opened as chats
              navigate(`/chat/${chat.id}`);
            }} />
          ))}
        </div>
      )}
    </div>
  );
}

function ChatCard({ chat, onClick }: { chat: ChatConsultation; onClick: () => void }) {
  const isLegacy = chat.status === 'legacy';
  const isActive = chat.status === 'active';

  return (
    <button
      onClick={onClick}
      disabled={isLegacy}
      className={clsx(
        'w-full text-left p-4 rounded-xl border transition-all duration-200',
        isLegacy
          ? 'bg-gray-50 border-gray-100 cursor-default opacity-70'
          : 'bg-white border-gray-100 shadow-sm hover:shadow-md hover:border-medical-teal/30 cursor-pointer',
      )}
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-medical-teal/10 rounded-full flex items-center justify-center shrink-0">
          <Stethoscope size={18} className="text-medical-teal" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-gray-800 truncate">
              {chat.doctor.name}
            </span>
            <span className={clsx(
              'px-1.5 py-0.5 text-[10px] rounded-full font-medium shrink-0',
              isActive ? 'bg-emerald-100 text-emerald-700' :
              isLegacy ? 'bg-gray-100 text-gray-500' :
              'bg-gray-100 text-gray-500',
            )}>
              {isActive ? 'Активна' : isLegacy ? 'Архив' : 'Закрыта'}
            </span>
          </div>

          <p className="text-sm text-gray-800 truncate mb-1">{chat.title}</p>

          {chat.last_message_preview && (
            <p className="text-xs text-gray-500 truncate">{chat.last_message_preview}</p>
          )}

          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Clock size={11} />
              {formatDate(chat.date)}
            </span>
            {chat.message_count > 0 && (
              <span>{chat.message_count} сообщ.</span>
            )}
          </div>
        </div>

        {!isLegacy && (
          <ChevronRight size={18} className="text-gray-300 shrink-0 mt-2" />
        )}
      </div>
    </button>
  );
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Сегодня ' + d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    if (days === 1) return 'Вчера';
    if (days < 7) return `${days} дн. назад`;
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
  } catch {
    return '';
  }
}
