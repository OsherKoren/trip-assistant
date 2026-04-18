import { useCallback, useEffect, useRef, useState } from 'react';
import type { Feedback, HistoryEntry, Message } from '../types';
import { sendMessageStream } from '../api/client';
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
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const loadMessages = useCallback((msgs: Message[]) => {
    setMessages(msgs);
    setError(null);
    lastActivityRef.current = Date.now();
  }, []);

  const sendMessage = useCallback(async (question: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

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

    const placeholderId = generateId();
    let placeholderAdded = false;

    try {
      await sendMessageStream(
        question,
        getToken,
        history,
        (token) => {
          if (!placeholderAdded) {
            placeholderAdded = true;
            setIsLoading(false);
            setMessages((prev) => [
              ...prev,
              {
                id: placeholderId,
                role: 'assistant',
                content: token,
                isStreaming: true,
                timestamp: new Date(),
              },
            ]);
          } else {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === placeholderId ? { ...m, content: m.content + token } : m,
              ),
            );
          }
        },
        (meta) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === placeholderId
                ? { ...m, id: meta.id, category: meta.category, confidence: meta.confidence, isStreaming: false }
                : m,
            ),
          );
        },
        controller.signal,
      );
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return;
      setError(err instanceof Error ? err.message : 'Something went wrong');
      if (placeholderAdded) {
        setMessages((prev) => prev.filter((m) => m.id !== placeholderId));
      }
    } finally {
      setIsLoading(false);
    }
  }, [messages, getToken]);

  const setFeedback = useCallback((messageId: string, feedback: Feedback) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, feedback } : msg,
      ),
    );
  }, []);

  return { messages, isLoading, error, sendMessage, setFeedback, clearMessages, loadMessages };
}
