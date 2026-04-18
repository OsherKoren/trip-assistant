import type { FeedbackRequest, FeedbackResponse, HistoryEntry, MessageResponse, StreamDoneMeta } from '../types';

const API_URL = import.meta.env.VITE_API_URL;

export async function sendMessage(
  question: string,
  getToken: () => Promise<string>,
  history: HistoryEntry[] = [],
): Promise<MessageResponse> {
  const token = await getToken();
  const response = await fetch(`${API_URL}/api/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ question, history }),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
}

export async function sendMessageStream(
  question: string,
  getToken: () => Promise<string>,
  history: HistoryEntry[] = [],
  onChunk: (token: string) => void,
  onDone: (meta: StreamDoneMeta) => void,
  signal?: AbortSignal,
): Promise<void> {
  const token = await getToken();
  const response = await fetch(`${API_URL}/api/messages/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ question, history }),
    signal,
  });

  if (!response.ok) {
    throw new Error('Failed to stream message');
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split('\n\n');
    buffer = parts.pop() ?? '';

    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith('data:')) continue;
      const raw = line.slice(5);
      const data = raw.startsWith(' ') ? raw.slice(1) : raw;
      if (data.startsWith('[DONE]')) {
        onDone(JSON.parse(data.slice(6).trim()));
      } else if (data.startsWith('[ERROR]')) {
        throw new Error(data.slice(7).trim());
      } else {
        onChunk(data);
      }
    }
  }
}

export async function sendFeedback(
  feedback: FeedbackRequest,
  getToken: () => Promise<string>,
): Promise<FeedbackResponse> {
  const token = await getToken();
  const response = await fetch(`${API_URL}/api/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(feedback),
  });

  if (!response.ok) {
    throw new Error('Failed to send feedback');
  }

  return response.json();
}
