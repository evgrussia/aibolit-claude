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
 * Refresh the access token using the stored refresh token.
 * Returns the new access token or null if refresh failed.
 */
async function _refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('aibolit_refresh_token');
  if (!refreshToken) return null;
  try {
    const res = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    localStorage.setItem('aibolit_token', data.token);
    localStorage.setItem('aibolit_refresh_token', data.refresh_token);
    return data.token;
  } catch {
    return null;
  }
}

/**
 * Fetch with automatic Bearer token and 401 retry via refresh token.
 * Raw fetch is used for SSE endpoints (axios doesn't support streaming),
 * but it bypasses the axios auto-refresh interceptor — this helper fills that gap.
 */
async function _fetchWithAuth(
  url: string,
  init: RequestInit,
): Promise<Response> {
  const token = localStorage.getItem('aibolit_token');
  const headers: Record<string, string> = {};
  // Copy explicit headers (e.g. Content-Type for JSON requests)
  if (init.headers) {
    for (const [k, v] of Object.entries(init.headers as Record<string, string>)) {
      headers[k] = v;
    }
  }
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res = await fetch(url, { ...init, headers });

  if (res.status === 401) {
    const newToken = await _refreshAccessToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      res = await fetch(url, { ...init, headers });
    }
  }

  return res;
}

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
  const res = await _fetchWithAuth('/api/v1/chat/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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
  const form = new FormData();
  form.append('text', text);
  if (files) {
    for (const f of files) {
      form.append('files', f);
    }
  }

  const res = await _fetchWithAuth(`/api/v1/chat/${consultationId}/message`, {
    method: 'POST',
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
  let currentEvent = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

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
