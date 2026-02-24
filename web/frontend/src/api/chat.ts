import api from './client';
import type { ChatConsultation, ChatMessage } from '../types/patient';

/**
 * SSE event types from the chat backend.
 */
export interface ChatMetaEvent {
  consultation_id?: number;
  doctor?: { specialty_id: string; name: string; qualification: string };
  disclaimer?: string;
  red_flags?: Array<{ category: string; description: string; urgency: number; action: string }>;
  emergency?: { call: string; message: string; flags: Array<{ category: string; description: string; action: string }> };
}

export interface ChatDeltaEvent {
  text: string;
}

export interface ChatDoneEvent {
  message_id: number;
  full_text: string;
}

export interface ChatErrorEvent {
  error: string;
}

export interface ChatReferralEvent {
  referrals: Array<{
    specialty_id: string;
    name: string;
    specialty_name: string;
  }>;
}

export type ChatSSEHandler = {
  onMeta?: (data: ChatMetaEvent) => void;
  onDelta?: (data: ChatDeltaEvent) => void;
  onDone?: (data: ChatDoneEvent) => void;
  onError?: (data: ChatErrorEvent) => void;
  onReferral?: (data: ChatReferralEvent) => void;
};

/**
 * Create a new chat consultation and stream first AI response.
 * Uses fetch + ReadableStream for SSE (Axios doesn't support streaming).
 */
export async function createChat(
  specialty: string,
  complaints: string,
  handlers: ChatSSEHandler,
  signal?: AbortSignal,
): Promise<void> {
  const token = localStorage.getItem('aibolit_token');
  const res = await fetch('/api/v1/chat/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ specialty, complaints }),
    signal,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `Ошибка ${res.status}` }));
    throw new Error(err.detail || `Ошибка ${res.status}`);
  }

  await _processSSE(res, handlers);
}

/**
 * Send a message (text + optional files) and stream AI response.
 */
export async function sendMessage(
  consultationId: number,
  text: string,
  files: File[] | undefined,
  handlers: ChatSSEHandler,
  signal?: AbortSignal,
): Promise<void> {
  const token = localStorage.getItem('aibolit_token');
  const form = new FormData();
  form.append('text', text);
  if (files) {
    for (const f of files) {
      form.append('files', f);
    }
  }

  const res = await fetch(`/api/v1/chat/${consultationId}/message`, {
    method: 'POST',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: form,
    signal,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `Ошибка ${res.status}` }));
    throw new Error(err.detail || `Ошибка ${res.status}`);
  }

  await _processSSE(res, handlers);
}

/**
 * Get all messages for a consultation.
 */
export async function getMessages(consultationId: number): Promise<ChatMessage[]> {
  const { data } = await api.get(`/chat/${consultationId}/messages`);
  return data;
}

/**
 * Get consultation metadata.
 */
export async function getChatInfo(consultationId: number): Promise<ChatConsultation & { session_id?: string; complaints: string }> {
  const { data } = await api.get(`/chat/${consultationId}`);
  return data;
}

/**
 * Get my chat consultations.
 */
export async function getMyChats(): Promise<ChatConsultation[]> {
  const { data } = await api.get('/chat');
  return data;
}

/**
 * Close a consultation.
 */
export async function closeChat(consultationId: number): Promise<void> {
  await api.post(`/chat/${consultationId}/close`);
}

/**
 * Get attachment download URL.
 */
export function getAttachmentUrl(attachmentId: number): string {
  return `/api/v1/chat/attachments/${attachmentId}`;
}

// ── SSE parser ───────────────────────────────────────────

async function _processSSE(res: Response, handlers: ChatSSEHandler): Promise<void> {
  const reader = res.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    let currentEvent = '';

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith('data: ')) {
        const raw = line.slice(6);
        try {
          const data = JSON.parse(raw);
          switch (currentEvent) {
            case 'meta':
              handlers.onMeta?.(data);
              break;
            case 'delta':
              handlers.onDelta?.(data);
              break;
            case 'done':
              handlers.onDone?.(data);
              break;
            case 'error':
              handlers.onError?.(data);
              break;
            case 'referral':
              handlers.onReferral?.(data);
              break;
          }
        } catch {
          // skip malformed JSON
        }
        currentEvent = '';
      }
    }
  }
}
