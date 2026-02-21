import type { MessageResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL;

export async function sendMessage(question: string): Promise<MessageResponse> {
  const response = await fetch(`${API_URL}/api/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
}
