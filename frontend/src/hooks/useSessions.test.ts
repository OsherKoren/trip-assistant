import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSessions } from './useSessions';
import type { Message } from '../types';

const mockMessage = (role: 'user' | 'assistant', content: string): Message => ({
  id: `msg-${Math.random()}`,
  role,
  content,
  timestamp: new Date('2026-03-21T10:00:00Z'),
});

describe('useSessions', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('starts with no sessions when localStorage is empty', () => {
    const { result } = renderHook(() => useSessions());
    expect(result.current.sessions).toEqual([]);
    expect(result.current.activeSessionId).toBeNull();
    expect(result.current.activeSession).toBeNull();
  });

  it('createSession adds a session and sets it as active', () => {
    const { result } = renderHook(() => useSessions());

    act(() => { result.current.createSession(); });

    expect(result.current.sessions).toHaveLength(1);
    expect(result.current.sessions[0].title).toBe('New Chat');
    expect(result.current.activeSessionId).toBe(result.current.sessions[0].id);
    expect(result.current.activeSession).not.toBeNull();
  });

  it('selectSession switches the active session', () => {
    const { result } = renderHook(() => useSessions());

    act(() => { result.current.createSession(); });
    act(() => { result.current.createSession(); });

    const [second, first] = result.current.sessions; // newest first
    expect(result.current.activeSessionId).toBe(second.id);

    act(() => { result.current.selectSession(first.id); });
    expect(result.current.activeSessionId).toBe(first.id);
  });

  it('updateSession saves messages and derives title from first user message', () => {
    const { result } = renderHook(() => useSessions());

    act(() => { result.current.createSession(); });
    const id = result.current.sessions[0].id;

    const messages = [
      mockMessage('user', 'What car did we rent?'),
      mockMessage('assistant', 'A Sixt rental.'),
    ];

    act(() => { result.current.updateSession(id, messages); });

    expect(result.current.sessions[0].messages).toHaveLength(2);
    expect(result.current.sessions[0].title).toBe('What car did we rent?');
  });

  it('updateSession truncates long titles to 40 chars', () => {
    const { result } = renderHook(() => useSessions());

    act(() => { result.current.createSession(); });
    const id = result.current.sessions[0].id;
    const longQuestion = 'A'.repeat(50);

    act(() => { result.current.updateSession(id, [mockMessage('user', longQuestion)]); });

    expect(result.current.sessions[0].title).toBe('A'.repeat(40) + '...');
  });

  it('deleteSession removes the session', () => {
    const { result } = renderHook(() => useSessions());

    act(() => { result.current.createSession(); });
    const id = result.current.sessions[0].id;

    act(() => { result.current.deleteSession(id); });

    expect(result.current.sessions).toHaveLength(0);
  });

  it('deleteSession falls back to the next session when active is deleted', () => {
    const { result } = renderHook(() => useSessions());

    act(() => { result.current.createSession(); });
    act(() => { result.current.createSession(); });

    const [active] = result.current.sessions; // most recent is active
    act(() => { result.current.deleteSession(active.id); });

    expect(result.current.sessions).toHaveLength(1);
    expect(result.current.activeSessionId).toBe(result.current.sessions[0].id);
  });

  it('persists sessions to localStorage', () => {
    const { result } = renderHook(() => useSessions());

    act(() => { result.current.createSession(); });

    const stored = localStorage.getItem('trip-assistant:sessions');
    expect(stored).not.toBeNull();
    const parsed = JSON.parse(stored!);
    expect(parsed).toHaveLength(1);
    expect(parsed[0].title).toBe('New Chat');
  });

  it('initializes from existing localStorage data', () => {
    const raw = [
      {
        id: 'session-existing',
        title: 'Old question',
        messages: [
          { id: 'msg-1', role: 'user', content: 'Old question', timestamp: '2026-03-20T10:00:00.000Z' },
        ],
        createdAt: '2026-03-20T10:00:00.000Z',
        updatedAt: '2026-03-20T10:00:00.000Z',
      },
    ];
    localStorage.setItem('trip-assistant:sessions', JSON.stringify(raw));
    localStorage.setItem('trip-assistant:active-session', 'session-existing');

    const { result } = renderHook(() => useSessions());

    expect(result.current.sessions).toHaveLength(1);
    expect(result.current.sessions[0].title).toBe('Old question');
    expect(result.current.activeSessionId).toBe('session-existing');
    // timestamps are parsed back to Date objects
    expect(result.current.sessions[0].messages[0].timestamp).toBeInstanceOf(Date);
  });
});
