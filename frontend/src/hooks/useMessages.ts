import { useState } from 'react';
import type { Feedback, Message } from '../types';
import { sendMessage as sendApiMessage } from '../api/client';
import { useAuth } from './useAuth';

let nextId = 0;
function generateId(): string {
  return `msg-${Date.now()}-${nextId++}`;
}

export function useMessages() {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (question: string) => {
    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendApiMessage(question, getToken);
      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: response.answer,
        category: response.category,
        confidence: response.confidence,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  const setFeedback = (messageId: string, feedback: Feedback) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, feedback } : msg,
      ),
    );
  };

  return { messages, isLoading, error, sendMessage, setFeedback };
}
