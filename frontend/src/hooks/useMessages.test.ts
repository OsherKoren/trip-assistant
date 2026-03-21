import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useMessages } from './useMessages';
import * as client from '../api/client';
import type { StreamDone } from '../types';

vi.mock('../api/client');

vi.mock('./useAuth', () => ({
  useAuth: () => ({
    getToken: vi.fn().mockResolvedValue('mock-token'),
  }),
}));

const mockDone: StreamDone = {
  done: true,
  id: 'msg-server-456',
  answer: 'You rented a car from Sixt.',
  category: 'car_rental',
  confidence: 0.95,
  source: null,
};

/** Helper: mock streamMessage to call onToken(s) then onDone */
function mockStreamSuccess(tokens = ['You rented a car from Sixt.'], done = mockDone) {
  vi.mocked(client.streamMessage).mockImplementation(
    async (_q, _t, _h, callbacks) => {
      for (const token of tokens) callbacks.onToken(token);
      callbacks.onDone(done);
    },
  );
}

/** Helper: mock streamMessage to call onError */
function mockStreamError(message: string) {
  vi.mocked(client.streamMessage).mockImplementation(
    async (_q, _t, _h, callbacks) => {
      callbacks.onError(message);
    },
  );
}

describe('useMessages', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('has correct initial state', () => {
    const { result } = renderHook(() => useMessages());

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('adds user message to state', async () => {
    mockStreamSuccess();
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('What car did we rent?');
    });

    expect(result.current.messages[0].role).toBe('user');
    expect(result.current.messages[0].content).toBe('What car did we rent?');
  });

  it('sets isLoading while waiting for first token', async () => {
    let resolveStream!: () => void;
    vi.mocked(client.streamMessage).mockReturnValue(
      new Promise<void>((resolve) => { resolveStream = resolve; }),
    );
    const { result } = renderHook(() => useMessages());

    act(() => { result.current.sendMessage('hello'); });

    expect(result.current.isLoading).toBe(true);

    await act(async () => { resolveStream(); });

    expect(result.current.isLoading).toBe(false);
  });

  it('adds assistant response after streaming completes', async () => {
    mockStreamSuccess();
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

  it('streams tokens into assistant message content', async () => {
    mockStreamSuccess(['Hello ', 'world', '!']);
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hi');
    });

    expect(result.current.messages[1].content).toBe('Hello world!');
  });

  it('uses server ID from done event', async () => {
    mockStreamSuccess();
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(result.current.messages[1].id).toBe('msg-server-456');
  });

  it('passes getToken and empty history to streamMessage on first call', async () => {
    mockStreamSuccess();
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(client.streamMessage).toHaveBeenCalledWith(
      'hello',
      expect.any(Function),
      [],
      expect.any(Object),
    );
  });

  it('passes conversation history to streamMessage on subsequent calls', async () => {
    const secondDone = { ...mockDone, id: 'msg-server-789', answer: 'It cost 200 euros.' };
    vi.mocked(client.streamMessage)
      .mockImplementationOnce(async (_q, _t, _h, cb) => {
        cb.onToken('You rented a car from Sixt.');
        cb.onDone(mockDone);
      })
      .mockImplementationOnce(async (_q, _t, _h, cb) => {
        cb.onToken('It cost 200 euros.');
        cb.onDone(secondDone);
      });
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('What car did we rent?'); });
    await act(async () => { await result.current.sendMessage('How much did it cost?'); });

    expect(client.streamMessage).toHaveBeenLastCalledWith(
      'How much did it cost?',
      expect.any(Function),
      [
        { role: 'user', content: 'What car did we rent?' },
        { role: 'assistant', content: 'You rented a car from Sixt.' },
      ],
      expect.any(Object),
    );
  });

  it('sets error on streaming failure (onError callback)', async () => {
    mockStreamError('Network error');
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.isLoading).toBe(false);
    // Placeholder message should be removed
    expect(result.current.messages).toHaveLength(1); // only user message
  });

  it('sets error when streamMessage throws', async () => {
    vi.mocked(client.streamMessage).mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.isLoading).toBe(false);
  });

  it('clears previous error on new message', async () => {
    mockStreamError('Network error');
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('fail'); });
    expect(result.current.error).toBe('Network error');

    mockStreamSuccess();
    await act(async () => { await result.current.sendMessage('succeed'); });
    expect(result.current.error).toBeNull();
  });

  it('messages have unique IDs', async () => {
    const done2 = { ...mockDone, id: 'msg-server-789' };
    vi.mocked(client.streamMessage)
      .mockImplementationOnce(async (_q, _t, _h, cb) => { cb.onToken('a'); cb.onDone(mockDone); })
      .mockImplementationOnce(async (_q, _t, _h, cb) => { cb.onToken('b'); cb.onDone(done2); });
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('first'); });
    await act(async () => { await result.current.sendMessage('second'); });

    const ids = result.current.messages.map((m) => m.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('messages have timestamps', async () => {
    mockStreamSuccess();
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });

    for (const msg of result.current.messages) {
      expect(msg.timestamp).toBeInstanceOf(Date);
    }
  });

  it('setFeedback updates message feedback', async () => {
    mockStreamSuccess();
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
    mockStreamSuccess();
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });

    const assistantMsg = result.current.messages[1];

    act(() => {
      result.current.setFeedback(assistantMsg.id, { rating: 'down', comment: 'Wrong answer' });
    });

    expect(result.current.messages[1].feedback).toEqual({ rating: 'down', comment: 'Wrong answer' });
  });

  it('clearMessages resets messages and error', async () => {
    mockStreamError('fail');
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });
    expect(result.current.messages.length).toBeGreaterThan(0);
    expect(result.current.error).toBe('fail');

    act(() => { result.current.clearMessages(); });

    expect(result.current.messages).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it('clears messages when session has expired', async () => {
    mockStreamSuccess();
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('first'); });
    expect(result.current.messages).toHaveLength(2);

    const originalNow = Date.now;
    Date.now = () => originalNow() + 31 * 60 * 1000;

    mockStreamSuccess(['after timeout answer'], { ...mockDone, id: 'msg-new', answer: 'after timeout answer' });
    await act(async () => { await result.current.sendMessage('after timeout'); });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].content).toBe('after timeout');

    expect(client.streamMessage).toHaveBeenLastCalledWith(
      'after timeout',
      expect.any(Function),
      [],
      expect.any(Object),
    );

    Date.now = originalNow;
  });

  it('loadMessages replaces messages and clears error', async () => {
    mockStreamError('fail');
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
