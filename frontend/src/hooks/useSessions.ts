import { useCallback, useEffect, useState } from 'react';
import type { ChatSession, Feedback, Message } from '../types';

const SESSIONS_KEY = 'trip-assistant:sessions';
const ACTIVE_KEY = 'trip-assistant:active-session';

// Raw shape stored in localStorage (timestamps are ISO strings)
interface RawMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  category?: string;
  confidence?: number;
  feedback?: Feedback;
  timestamp: string;
}
interface RawSession {
  id: string;
  title: string;
  messages: RawMessage[];
  createdAt: string;
  updatedAt: string;
}

function parseSession(raw: RawSession): ChatSession {
  return {
    ...raw,
    messages: raw.messages.map((m) => ({ ...m, timestamp: new Date(m.timestamp) })),
  };
}

function loadSessions(): ChatSession[] {
  try {
    const stored = localStorage.getItem(SESSIONS_KEY);
    if (!stored) return [];
    const raws = JSON.parse(stored) as RawSession[];
    return raws.map(parseSession);
  } catch {
    return [];
  }
}

function loadActiveId(): string | null {
  try {
    return localStorage.getItem(ACTIVE_KEY);
  } catch {
    return null;
  }
}

function deriveTitle(messages: Message[]): string {
  const first = messages.find((m) => m.role === 'user');
  if (!first) return 'New Chat';
  return first.content.length > 40 ? first.content.slice(0, 40) + '...' : first.content;
}

let sessionCounter = 0;
function generateSessionId(): string {
  return `session-${Date.now()}-${sessionCounter++}`;
}

export function useSessions() {
  const [sessions, setSessions] = useState<ChatSession[]>(loadSessions);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(loadActiveId);

  useEffect(() => {
    try {
      localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
    } catch {
      // storage unavailable — continue without persistence
    }
  }, [sessions]);

  useEffect(() => {
    try {
      if (activeSessionId) {
        localStorage.setItem(ACTIVE_KEY, activeSessionId);
      } else {
        localStorage.removeItem(ACTIVE_KEY);
      }
    } catch {
      // storage unavailable
    }
  }, [activeSessionId]);

  const activeSession = sessions.find((s) => s.id === activeSessionId) ?? null;

  const createSession = useCallback((): ChatSession => {
    const session: ChatSession = {
      id: generateSessionId(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setSessions((prev) => [session, ...prev]);
    setActiveSessionId(session.id);
    return session;
  }, []);

  const selectSession = useCallback((id: string) => {
    setActiveSessionId(id);
  }, []);

  const updateSession = useCallback((id: string, messages: Message[]) => {
    setSessions((prev) =>
      prev.map((s) =>
        s.id === id
          ? { ...s, title: deriveTitle(messages), messages, updatedAt: new Date().toISOString() }
          : s,
      ),
    );
  }, []);

  const deleteSession = useCallback(
    (id: string) => {
      setSessions((prev) => {
        const filtered = prev.filter((s) => s.id !== id);
        if (activeSessionId === id) {
          setActiveSessionId(filtered[0]?.id ?? null);
        }
        return filtered;
      });
    },
    [activeSessionId],
  );

  return { sessions, activeSession, activeSessionId, createSession, selectSession, updateSession, deleteSession };
}
