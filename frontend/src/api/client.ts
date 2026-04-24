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

export async function parseSSEStream(
  body: ReadableStream<Uint8Array>,
  onChunk: (token: string) => void,
  onDone: (meta: StreamDoneMeta) => void,
): Promise<void> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split('\n\n');
    buffer = parts.pop() ?? '';

    for (const part of parts) {
      // Collect all data: lines in the event (SSE spec allows multi-line data)
      const dataLines = part.split('\n').filter(l => l.startsWith('data:'));
      if (dataLines.length === 0) continue;
      const data = dataLines
        .map(l => l.slice(5))
        .map(s => (s.startsWith(' ') ? s.slice(1) : s))
        .join('\n');
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

  if (!response.body) {
    throw new Error('Response body is null');
  }

  await parseSSEStream(response.body, onChunk, onDone);
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
