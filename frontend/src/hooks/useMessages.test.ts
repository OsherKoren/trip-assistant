import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useMessages } from './useMessages';
import * as client from '../api/client';
import type { MessageResponse } from '../types';

vi.mock('../api/client');

vi.mock('./useAuth', () => ({
  useAuth: () => ({
    getToken: vi.fn().mockResolvedValue('mock-token'),
  }),
}));

const mockResponse: MessageResponse = {
  id: 'msg-server-456',
  answer: 'You rented a car from Sixt.',
  category: 'car_rental',
  confidence: 0.95,
  source: null,
};

describe('useMessages', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.mocked(client.sendMessage).mockResolvedValue(mockResponse);
  });

  it('has correct initial state', () => {
    const { result } = renderHook(() => useMessages());

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('adds user message to state', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('What car did we rent?');
    });

    expect(result.current.messages[0].role).toBe('user');
    expect(result.current.messages[0].content).toBe('What car did we rent?');
  });

  it('sets isLoading while waiting for response', async () => {
    let resolveRequest!: (v: MessageResponse) => void;
    vi.mocked(client.sendMessage).mockReturnValue(
      new Promise<MessageResponse>((resolve) => { resolveRequest = resolve; }),
    );
    const { result } = renderHook(() => useMessages());

    act(() => { result.current.sendMessage('hello'); });

    expect(result.current.isLoading).toBe(true);

    await act(async () => { resolveRequest(mockResponse); });

    expect(result.current.isLoading).toBe(false);
  });

  it('adds assistant response after send completes', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('What car did we rent?');
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].role).toBe('assistant');
    expect(result.current.messages[1].content).toBe('You rented a car from Sixt.');
    expect(result.current.messages[1].category).toBe('car_rental');
    expect(result.current.messages[1].isStreaming).toBe(false);
  });

  it('uses server ID from response', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(result.current.messages[1].id).toBe('msg-server-456');
  });

  it('passes getToken and empty history to sendMessage on first call', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(client.sendMessage).toHaveBeenCalledWith(
      'hello',
      expect.any(Function),
      [],
    );
  });

  it('passes conversation history to sendMessage on subsequent calls', async () => {
    const secondResponse = { ...mockResponse, id: 'msg-server-789', answer: 'It cost 200 euros.' };
    vi.mocked(client.sendMessage)
      .mockResolvedValueOnce(mockResponse)
      .mockResolvedValueOnce(secondResponse);
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('What car did we rent?'); });
    await act(async () => { await result.current.sendMessage('How much did it cost?'); });

    expect(client.sendMessage).toHaveBeenLastCalledWith(
      'How much did it cost?',
      expect.any(Function),
      [
        { role: 'user', content: 'What car did we rent?' },
        { role: 'assistant', content: 'You rented a car from Sixt.' },
      ],
    );
  });

  it('sets error when sendMessage throws', async () => {
    vi.mocked(client.sendMessage).mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.isLoading).toBe(false);
  });

  it('clears previous error on new message', async () => {
    vi.mocked(client.sendMessage)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce(mockResponse);
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('fail'); });
    expect(result.current.error).toBe('Network error');

    await act(async () => { await result.current.sendMessage('succeed'); });
    expect(result.current.error).toBeNull();
  });

  it('messages have unique IDs', async () => {
    const response2 = { ...mockResponse, id: 'msg-server-789' };
    vi.mocked(client.sendMessage)
      .mockResolvedValueOnce(mockResponse)
      .mockResolvedValueOnce(response2);
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('first'); });
    await act(async () => { await result.current.sendMessage('second'); });

    const ids = result.current.messages.map((m) => m.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('messages have timestamps', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });

    for (const msg of result.current.messages) {
      expect(msg.timestamp).toBeInstanceOf(Date);
    }
  });

  it('setFeedback updates message feedback', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });

    const assistantMsg = result.current.messages[1];

    act(() => {
      result.current.setFeedback(assistantMsg.id, { rating: 'up' });
    });

    expect(result.current.messages[1].feedback).toEqual({ rating: 'up' });
    expect(result.current.messages[0].feedback).toBeUndefined();
  });

  it('setFeedback with down rating and comment', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });

    const assistantMsg = result.current.messages[1];

    act(() => {
      result.current.setFeedback(assistantMsg.id, { rating: 'down', comment: 'Wrong answer' });
    });

    expect(result.current.messages[1].feedback).toEqual({ rating: 'down', comment: 'Wrong answer' });
  });

  it('clearMessages resets messages and error', async () => {
    vi.mocked(client.sendMessage).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });
    expect(result.current.messages.length).toBeGreaterThan(0);
    expect(result.current.error).toBe('fail');

    act(() => { result.current.clearMessages(); });

    expect(result.current.messages).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it('clears messages when session has expired', async () => {
    const afterTimeoutResponse = { ...mockResponse, id: 'msg-new', answer: 'after timeout answer' };
    vi.mocked(client.sendMessage)
      .mockResolvedValueOnce(mockResponse)
      .mockResolvedValueOnce(afterTimeoutResponse);
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('first'); });
    expect(result.current.messages).toHaveLength(2);

    const originalNow = Date.now;
    Date.now = () => originalNow() + 31 * 60 * 1000;

    await act(async () => { await result.current.sendMessage('after timeout'); });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].content).toBe('after timeout');

    expect(client.sendMessage).toHaveBeenLastCalledWith(
      'after timeout',
      expect.any(Function),
      [],
    );

    Date.now = originalNow;
  });

  it('loadMessages replaces messages and clears error', async () => {
    vi.mocked(client.sendMessage).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });
    expect(result.current.error).toBe('fail');

    const loaded = [
      { id: 'loaded-1', role: 'user' as const, content: 'Old question', timestamp: new Date() },
      { id: 'loaded-2', role: 'assistant' as const, content: 'Old answer', timestamp: new Date() },
    ];

    act(() => { result.current.loadMessages(loaded); });

    expect(result.current.messages).toEqual(loaded);
    expect(result.current.error).toBeNull();
  });
});
