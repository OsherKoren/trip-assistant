import type { FeedbackRequest, FeedbackResponse, HistoryEntry, MessageResponse } from '../types';

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
