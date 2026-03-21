import { useCallback, useRef, useState } from 'react';
import type { Feedback, HistoryEntry, Message } from '../types';
import { sendMessage as sendApiMessage } from '../api/client';
import { useAuth } from './useAuth';

export const SESSION_TIMEOUT_MS = 30 * 60 * 1000;

let nextId = 0;
function generateId(): string {
  return `msg-${Date.now()}-${nextId++}`;
}

export function useMessages() {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastActivityRef = useRef<number>(Date.now());

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const loadMessages = useCallback((msgs: Message[]) => {
    setMessages(msgs);
    setError(null);
    lastActivityRef.current = Date.now();
  }, []);

  const sendMessage = async (question: string) => {
    const now = Date.now();
    let currentMessages: Message[] = [];

    if (now - lastActivityRef.current > SESSION_TIMEOUT_MS) {
      setMessages([]);
      setError(null);
    } else {
      currentMessages = messages;
    }

    lastActivityRef.current = now;

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    };

    const history: HistoryEntry[] = currentMessages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendApiMessage(question, getToken, history);
      const assistantMessage: Message = {
        id: response.id,
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

  return { messages, isLoading, error, sendMessage, setFeedback, clearMessages, loadMessages };
}
