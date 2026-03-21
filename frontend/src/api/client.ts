import type { FeedbackRequest, FeedbackResponse, HistoryEntry, MessageResponse, StreamDone } from '../types';

interface StreamCallbacks {
  onToken: (token: string) => void;
  onDone: (meta: StreamDone) => void;
  onError: (message: string) => void;
}

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

export async function streamMessage(
  question: string,
  getToken: () => Promise<string>,
  history: HistoryEntry[] = [],
  callbacks: StreamCallbacks,
): Promise<void> {
  const token = await getToken();
  const response = await fetch(`${API_URL}/api/messages/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ question, history }),
  });

  if (!response.ok || !response.body) {
    callbacks.onError('Failed to send message');
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      try {
        const data = JSON.parse(line.slice(6)) as Record<string, unknown>;
        if (data.error) {
          callbacks.onError(String(data.error));
          return;
        } else if (data.done) {
          callbacks.onDone(data as unknown as StreamDone);
          return;
        } else if (typeof data.token === 'string') {
          callbacks.onToken(data.token);
        }
      } catch {
        // ignore malformed JSON lines
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
