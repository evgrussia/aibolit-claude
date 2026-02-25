import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Stethoscope, Send, Paperclip, X, FileText,
  Image as ImageIcon, AlertTriangle, Sparkles, ArrowLeft, XCircle,
  ArrowRightCircle, Loader2,
} from 'lucide-react';
import DOMPurify from 'dompurify';
import clsx from 'clsx';
import { getChatInfo, getMessages, sendMessage, closeChat, createChat } from '../api/chat';
import type { ChatSSEHandler, ChatMetaEvent, ChatReferralEvent } from '../api/chat';
import type { ChatMessage, ChatDoctor, ChatAttachment } from '../types/patient';
import EmergencyBanner from '../components/shared/EmergencyBanner';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import { useToast } from '../contexts/ToastContext';
import { getAttachmentUrl } from '../api/chat';

const FALLBACK_DISCLAIMER = '\u26a0\ufe0f AI-\u0430\u0441\u0441\u0438\u0441\u0442\u0435\u043d\u0442. \u041d\u0435 \u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f \u043c\u0435\u0434\u0438\u0446\u0438\u043d\u0441\u043a\u043e\u0439 \u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u0446\u0438\u0435\u0439.';

export default function ChatPage() {
  const { consultationId } = useParams<{ consultationId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const cId = Number(consultationId);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [doctor, setDoctor] = useState<ChatDoctor | null>(null);
  const [status, setStatus] = useState<string>('active');
  const [disclaimer, setDisclaimer] = useState(FALLBACK_DISCLAIMER);
  const [emergency, setEmergency] = useState<ChatMetaEvent['emergency'] | null>(null);
  const [redFlags, setRedFlags] = useState<ChatMetaEvent['red_flags'] | null>(null);

  const [referrals, setReferrals] = useState<ChatReferralEvent['referrals']>([]);
  const [originalComplaints, setOriginalComplaints] = useState('');
  const [navigatingToSpec, setNavigatingToSpec] = useState<string | null>(null);

  const [input, setInput] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [streamText, setStreamText] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamText, scrollToBottom]);

  // Load chat info + messages; reset transient state on navigation
  useEffect(() => {
    if (!cId) return;
    let cancelled = false;

    // Reset state that should not persist across chat navigations
    setReferrals([]);
    setNavigatingToSpec(null);
    setStreamText('');
    setStreaming(false);
    setEmergency(null);
    setRedFlags(null);
    setError('');

    async function load() {
      try {
        const [info, msgs] = await Promise.all([
          getChatInfo(cId),
          getMessages(cId),
        ]);
        if (cancelled) return;
        setDoctor(info.doctor);
        setStatus(info.status);
        setMessages(msgs);
        if (info.complaints) setOriginalComplaints(info.complaints);
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [cId]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
  }, [input]);

  const handleSend = useCallback(async () => {
    if (streaming || (!input.trim() && files.length === 0)) return;

    const text = input.trim();
    const currentFiles = [...files];
    setInput('');
    setFiles([]);
    setStreaming(true);
    setStreamText('');
    setReferrals([]);

    // Optimistically add user message
    const optimisticMsg: ChatMessage = {
      id: Date.now(),
      consultation_id: cId,
      role: 'user',
      content: text || '[файл]',
      attachments: currentFiles.map((f, i) => ({
        id: -(i + 1),
        file_name: f.name,
        file_type: f.type,
        file_size: f.size,
      })),
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, optimisticMsg]);

    const ac = new AbortController();
    abortRef.current = ac;

    const handlers: ChatSSEHandler = {
      onMeta: (data) => {
        if (data.red_flags) setRedFlags(data.red_flags);
        if (data.emergency) setEmergency(data.emergency);
        if (data.disclaimer) setDisclaimer(data.disclaimer);
      },
      onDelta: (data) => {
        setStreamText(prev => prev + data.text);
      },
      onDone: (data) => {
        const assistantMsg: ChatMessage = {
          id: data.message_id,
          consultation_id: cId,
          role: 'assistant',
          content: data.full_text,
          created_at: new Date().toISOString(),
        };
        setMessages(prev => [...prev, assistantMsg]);
        setStreamText('');
        setStreaming(false);
      },
      onError: (data) => {
        toast.error(data.error);
        setStreamText('');
        setStreaming(false);
      },
      onReferral: (data) => {
        if (data.referrals?.length) setReferrals(data.referrals);
      },
    };

    try {
      await sendMessage(cId, text, currentFiles.length > 0 ? currentFiles : undefined, handlers, ac.signal);
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        toast.error((err as Error).message || 'Ошибка отправки');
      }
      setStreaming(false);
      setStreamText('');
    }
  }, [cId, input, files, streaming, toast]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []);
    setFiles(prev => [...prev, ...selected].slice(0, 5));
    e.target.value = '';
  };

  const removeFile = (idx: number) => {
    setFiles(prev => prev.filter((_, i) => i !== idx));
  };

  const handleReferral = useCallback(async (specialtyId: string) => {
    setNavigatingToSpec(specialtyId);
    try {
      let newConsultationId: number | null = null;
      const handlers: ChatSSEHandler = {
        onMeta: (data) => {
          if (data.consultation_id) newConsultationId = data.consultation_id;
        },
      };
      const ac = new AbortController();
      const promise = createChat(specialtyId, originalComplaints, handlers, ac.signal);
      // Wait up to 3s for meta event with consultation_id
      const timeout = setTimeout(() => {
        if (newConsultationId) {
          ac.abort();
          navigate(`/chat/${newConsultationId}`);
        }
      }, 3000);
      await promise.catch(() => {});
      clearTimeout(timeout);
      if (newConsultationId) {
        navigate(`/chat/${newConsultationId}`);
      } else {
        toast.error('Не удалось создать чат');
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        toast.error((err as Error).message || 'Ошибка создания чата');
      }
    } finally {
      setNavigatingToSpec(null);
    }
  }, [originalComplaints, navigate, toast]);

  const handleClose = async () => {
    try {
      await closeChat(cId);
      setStatus('closed');
      toast.success('Консультация закрыта');
    } catch (err) {
      toast.error((err as Error).message);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return (
    <div className="p-6 text-center">
      <p className="text-red-600 mb-4">{error}</p>
      <button onClick={() => navigate('/chat')} className="text-medical-teal hover:underline">
        К списку чатов
      </button>
    </div>
  );

  const isActive = status === 'active';

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)] md:h-[calc(100vh-8rem)] max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-2 sm:gap-3 pb-3 sm:pb-4 border-b border-gray-100">
        <button onClick={() => navigate('/chat')} className="p-1.5 sm:p-2 rounded-lg hover:bg-gray-100 text-gray-500 shrink-0">
          <ArrowLeft size={18} />
        </button>
        <div className="w-8 h-8 sm:w-10 sm:h-10 bg-medical-teal/10 rounded-full flex items-center justify-center shrink-0">
          <Stethoscope size={18} className="text-medical-teal sm:hidden" />
          <Stethoscope size={22} className="text-medical-teal hidden sm:block" />
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="text-xs sm:text-sm font-bold text-gray-800 truncate">{doctor?.name || 'AI-Врач'}</h2>
          <p className="text-[10px] sm:text-xs text-gray-500 truncate">{doctor?.qualification}</p>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          <span className={clsx(
            'px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs rounded-full font-medium',
            isActive ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500',
          )}>
            {isActive ? 'Активна' : 'Закрыта'}
          </span>
          {isActive && (
            <button
              onClick={handleClose}
              className="text-xs text-gray-400 hover:text-red-500 transition-colors"
              title="Закрыть консультацию"
            >
              <XCircle size={16} />
            </button>
          )}
          {doctor && (
            <div className="hidden sm:flex items-center gap-1 px-2 py-0.5 bg-violet-50 border border-violet-200 rounded-full">
              <Sparkles size={12} className="text-violet-500" />
              <span className="text-xs font-medium text-violet-600">AI</span>
            </div>
          )}
        </div>
      </div>

      {/* Emergency banner */}
      {emergency && <EmergencyBanner message={emergency.message} className="mt-3" />}

      {/* Red flags */}
      {redFlags && redFlags.length > 0 && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={14} className="text-red-500" />
            <span className="text-xs font-medium text-red-700">Тревожные признаки</span>
          </div>
          {redFlags.map((f, i) => (
            <p key={i} className="text-xs text-red-600 ml-5">- {f.description}</p>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* Streaming indicator */}
        {streaming && streamText && (
          <div className="flex justify-start">
            <div className="max-w-[90%] sm:max-w-[80%] px-3 py-2.5 sm:px-4 sm:py-3 rounded-2xl rounded-bl-sm bg-white border border-gray-100 shadow-sm">
              <div
                className="text-sm text-gray-700 leading-relaxed prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(markdownToHtml(streamText)) }}
              />
              <TypingDots />
            </div>
          </div>
        )}

        {streaming && !streamText && (
          <div className="flex justify-start">
            <div className="px-4 py-3 rounded-2xl rounded-bl-sm bg-white border border-gray-100 shadow-sm">
              <TypingDots />
            </div>
          </div>
        )}

        {/* Referral cards */}
        {!streaming && referrals.length > 0 && (
          <ReferralCard
            referrals={referrals}
            onNavigate={handleReferral}
            navigatingToSpec={navigatingToSpec}
          />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-1.5 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg mb-2">
        <AlertTriangle size={12} className="text-amber-500 shrink-0 mt-0.5" />
        <p className="text-[10px] text-amber-700 leading-snug">{disclaimer}</p>
      </div>

      {/* Input area */}
      {isActive ? (
        <div className="border-t border-gray-100 pt-3">
          {/* File previews */}
          {files.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-2">
              {files.map((f, i) => (
                <div key={i} className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 rounded-lg text-xs text-gray-600">
                  {f.type.startsWith('image/') ? <ImageIcon size={12} /> : <FileText size={12} />}
                  <span className="max-w-[120px] truncate">{f.name}</span>
                  <button onClick={() => removeFile(i)} className="text-gray-400 hover:text-red-500">
                    <X size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-end gap-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={streaming}
              className="p-2.5 text-gray-400 hover:text-medical-teal hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
              title="Прикрепить файл"
            >
              <Paperclip size={18} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*,.pdf,.txt"
              className="hidden"
              onChange={handleFileSelect}
            />

            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Напишите сообщение..."
              rows={1}
              disabled={streaming}
              className="flex-1 px-3 py-2.5 border border-gray-200 rounded-xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50 max-h-40"
            />

            <button
              onClick={handleSend}
              disabled={streaming || (!input.trim() && files.length === 0)}
              className="p-2.5 bg-medical-teal text-white rounded-xl hover:bg-medical-teal/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      ) : (
        <div className="border-t border-gray-100 pt-3 text-center space-y-2">
          <p className="text-sm text-gray-400">Консультация завершена</p>
          {referrals.length > 0 && (
            <div className="flex flex-wrap justify-center gap-2">
              {referrals.map(ref => (
                <button
                  key={ref.specialty_id}
                  onClick={() => handleReferral(ref.specialty_id)}
                  disabled={navigatingToSpec !== null}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-violet-50 border border-violet-200 rounded-lg text-xs font-medium text-violet-700 hover:bg-violet-100 transition-colors disabled:opacity-50"
                >
                  {navigatingToSpec === ref.specialty_id ? <Loader2 size={12} className="animate-spin" /> : <Stethoscope size={12} />}
                  {ref.specialty_name}
                </button>
              ))}
            </div>
          )}
          <button
            onClick={() => navigate('/consult')}
            className="text-sm text-medical-teal hover:underline"
          >
            Начать новую консультацию
          </button>
        </div>
      )}
    </div>
  );
}


// ── Sub-components ───────────────────────────────────────

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div className={clsx(
        'max-w-[90%] sm:max-w-[80%] px-3 py-2.5 sm:px-4 sm:py-3 rounded-2xl',
        isUser
          ? 'bg-medical-teal text-white rounded-br-sm'
          : 'bg-white border border-gray-100 shadow-sm rounded-bl-sm',
      )}>
        {/* Attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {message.attachments.map(att => (
              <AttachmentChip key={att.id} attachment={att} isUser={isUser} />
            ))}
          </div>
        )}

        {/* Content */}
        {isUser ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div
            className="text-sm text-gray-700 leading-relaxed prose prose-sm max-w-none
                       prose-headings:text-gray-800 prose-strong:text-gray-800
                       prose-ul:my-1 prose-li:my-0.5"
            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(markdownToHtml(message.content)) }}
          />
        )}

        {/* Timestamp */}
        <p className={clsx(
          'text-[10px] mt-1.5',
          isUser ? 'text-white/60 text-right' : 'text-gray-400',
        )}>
          {formatTime(message.created_at)}
        </p>
      </div>
    </div>
  );
}


function AttachmentChip({ attachment, isUser }: { attachment: ChatAttachment; isUser: boolean }) {
  const isImage = attachment.file_type.startsWith('image/');
  const url = attachment.id > 0 ? getAttachmentUrl(attachment.id) : undefined;

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={clsx(
        'flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs transition-colors',
        isUser
          ? 'bg-white/20 text-white/90 hover:bg-white/30'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
        !url && 'pointer-events-none',
      )}
    >
      {isImage ? <ImageIcon size={12} /> : <FileText size={12} />}
      <span className="max-w-[100px] truncate">{attachment.file_name}</span>
    </a>
  );
}


function ReferralCard({
  referrals,
  onNavigate,
  navigatingToSpec,
}: {
  referrals: ChatReferralEvent['referrals'];
  onNavigate: (specialtyId: string) => void;
  navigatingToSpec: string | null;
}) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] sm:max-w-[80%] p-3 sm:p-4 rounded-2xl rounded-bl-sm bg-gradient-to-br from-violet-50 to-blue-50 border border-violet-200/60 shadow-sm">
        <div className="flex items-center gap-2 mb-2.5">
          <ArrowRightCircle size={16} className="text-violet-500" />
          <span className="text-xs sm:text-sm font-medium text-violet-700">Рекомендованные специалисты</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {referrals.map(ref => {
            const isNavigating = navigatingToSpec === ref.specialty_id;
            return (
              <button
                key={ref.specialty_id}
                onClick={() => onNavigate(ref.specialty_id)}
                disabled={navigatingToSpec !== null}
                className="flex items-center gap-1.5 px-3 py-2 bg-white border border-violet-200 rounded-xl text-xs sm:text-sm font-medium text-violet-700 hover:bg-violet-50 hover:border-violet-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
              >
                {isNavigating ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <Stethoscope size={14} />
                )}
                <span>{ref.specialty_name}</span>
                {!isNavigating && <ArrowRightCircle size={12} className="text-violet-400" />}
              </button>
            );
          })}
        </div>
        <p className="text-[10px] text-violet-400 mt-2">
          Нажмите, чтобы начать новую консультацию с этим специалистом
        </p>
      </div>
    </div>
  );
}


function TypingDots() {
  return (
    <span className="inline-flex items-center gap-1 ml-1">
      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
    </span>
  );
}


// ── Helpers ──────────────────────────────────────────────

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
}

function markdownToHtml(md: string): string {
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^[•\-\*] (.+)$/gm, '<li>$1</li>')
    .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
    .replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^(.+)$/, '<p>$1</p>')
    .replace(/<p><\/p>/g, '')
    .replace(/<p><(h[123]|ul)>/g, '<$1>')
    .replace(/<\/(h[123]|ul)><\/p>/g, '</$1>');
}
