import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useMessages } from './useMessages';
import * as client from '../api/client';
import type { StreamDoneMeta } from '../types';

vi.mock('../api/client');

vi.mock('./useAuth', () => ({
  useAuth: () => ({
    getToken: vi.fn().mockResolvedValue('mock-token'),
  }),
}));

const mockMeta: StreamDoneMeta = {
  id: 'msg-server-456',
  category: 'car_rental',
  confidence: 0.95,
};

function mockStream(tokens: string[], meta: StreamDoneMeta = mockMeta) {
  vi.mocked(client.sendMessageStream).mockImplementation(
    async (_q, _gt, _h, onChunk, onDone) => {
      for (const token of tokens) onChunk(token);
      onDone(meta);
    },
  );
}

describe('useMessages', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    mockStream(['You rented a car from Sixt.']);
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

  it('sets isLoading while waiting for first token', async () => {
    let resolveStream!: () => void;
    vi.mocked(client.sendMessageStream).mockReturnValue(
      new Promise<void>((resolve) => { resolveStream = resolve; }),
    );
    const { result } = renderHook(() => useMessages());

    act(() => { result.current.sendMessage('hello'); });

    expect(result.current.isLoading).toBe(true);

    await act(async () => { resolveStream(); });

    expect(result.current.isLoading).toBe(false);
  });

  it('sets isLoading false on first token and adds streaming bubble', async () => {
    let capturedOnChunk!: (t: string) => void;
    let capturedOnDone!: (m: StreamDoneMeta) => void;
    vi.mocked(client.sendMessageStream).mockImplementation(
      async (_q, _gt, _h, onChunk, onDone) => {
        capturedOnChunk = onChunk;
        capturedOnDone = onDone;
      },
    );
    const { result } = renderHook(() => useMessages());

    act(() => { result.current.sendMessage('hello'); });
    expect(result.current.isLoading).toBe(true);

    act(() => { capturedOnChunk('Hi'); });
    expect(result.current.isLoading).toBe(false);
    expect(result.current.messages[1].isStreaming).toBe(true);
    expect(result.current.messages[1].content).toBe('Hi');

    act(() => { capturedOnChunk(' there'); });
    expect(result.current.messages[1].content).toBe('Hi there');

    await act(async () => { capturedOnDone(mockMeta); });
    expect(result.current.messages[1].isStreaming).toBe(false);
    expect(result.current.messages[1].id).toBe('msg-server-456');
    expect(result.current.messages[1].confidence).toBe(0.95);
  });

  it('final message content equals concatenated tokens', async () => {
    mockStream(['Hello', ' ', 'world']);
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hi');
    });

    expect(result.current.messages[1].content).toBe('Hello world');
  });

  it('adds assistant response with metadata after stream completes', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('What car did we rent?');
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].role).toBe('assistant');
    expect(result.current.messages[1].content).toBe('You rented a car from Sixt.');
    expect(result.current.messages[1].category).toBe('car_rental');
    expect(result.current.messages[1].confidence).toBe(0.95);
    expect(result.current.messages[1].isStreaming).toBe(false);
  });

  it('uses server ID from onDone metadata', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(result.current.messages[1].id).toBe('msg-server-456');
  });

  it('passes getToken and empty history to sendMessageStream on first call', async () => {
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(client.sendMessageStream).toHaveBeenCalledWith(
      'hello',
      expect.any(Function),
      [],
      expect.any(Function),
      expect.any(Function),
      expect.any(AbortSignal),
    );
  });

  it('passes conversation history to sendMessageStream on subsequent calls', async () => {
    const meta2 = { ...mockMeta, id: 'msg-server-789' };
    vi.mocked(client.sendMessageStream)
      .mockImplementationOnce(async (_q, _gt, _h, onChunk, onDone) => {
        onChunk('You rented a car from Sixt.');
        onDone(mockMeta);
      })
      .mockImplementationOnce(async (_q, _gt, _h, onChunk, onDone) => {
        onChunk('It cost 200 euros.');
        onDone(meta2);
      });
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('What car did we rent?'); });
    await act(async () => { await result.current.sendMessage('How much did it cost?'); });

    expect(client.sendMessageStream).toHaveBeenLastCalledWith(
      'How much did it cost?',
      expect.any(Function),
      [
        { role: 'user', content: 'What car did we rent?' },
        { role: 'assistant', content: 'You rented a car from Sixt.' },
      ],
      expect.any(Function),
      expect.any(Function),
      expect.any(AbortSignal),
    );
  });

  it('sets error when stream throws', async () => {
    vi.mocked(client.sendMessageStream).mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.isLoading).toBe(false);
  });

  it('removes placeholder bubble on error', async () => {
    vi.mocked(client.sendMessageStream).mockImplementation(
      async (_q, _gt, _h, onChunk) => {
        onChunk('Partial...');
        throw new Error('Stream failed');
      },
    );
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    expect(result.current.error).toBe('Stream failed');
    expect(result.current.messages.every((m) => m.role === 'user')).toBe(true);
  });

  it('clears previous error on new message', async () => {
    vi.mocked(client.sendMessageStream)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockImplementationOnce(async (_q, _gt, _h, onChunk, onDone) => {
        onChunk('OK');
        onDone(mockMeta);
      });
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('fail'); });
    expect(result.current.error).toBe('Network error');

    await act(async () => { await result.current.sendMessage('succeed'); });
    expect(result.current.error).toBeNull();
  });

  it('messages have unique IDs', async () => {
    const meta2 = { ...mockMeta, id: 'msg-server-789' };
    vi.mocked(client.sendMessageStream)
      .mockImplementationOnce(async (_q, _gt, _h, onChunk, onDone) => {
        onChunk('First answer');
        onDone(mockMeta);
      })
      .mockImplementationOnce(async (_q, _gt, _h, onChunk, onDone) => {
        onChunk('Second answer');
        onDone(meta2);
      });
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
    vi.mocked(client.sendMessageStream).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('hello'); });
    expect(result.current.messages.length).toBeGreaterThan(0);
    expect(result.current.error).toBe('fail');

    act(() => { result.current.clearMessages(); });

    expect(result.current.messages).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it('clears messages when session has expired', async () => {
    const afterTimeoutMeta = { ...mockMeta, id: 'msg-new' };
    vi.mocked(client.sendMessageStream)
      .mockImplementationOnce(async (_q, _gt, _h, onChunk, onDone) => {
        onChunk('first answer');
        onDone(mockMeta);
      })
      .mockImplementationOnce(async (_q, _gt, _h, onChunk, onDone) => {
        onChunk('after timeout answer');
        onDone(afterTimeoutMeta);
      });
    const { result } = renderHook(() => useMessages());

    await act(async () => { await result.current.sendMessage('first'); });
    expect(result.current.messages).toHaveLength(2);

    const originalNow = Date.now;
    Date.now = () => originalNow() + 31 * 60 * 1000;

    await act(async () => { await result.current.sendMessage('after timeout'); });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].content).toBe('after timeout');

    expect(client.sendMessageStream).toHaveBeenLastCalledWith(
      'after timeout',
      expect.any(Function),
      [],
      expect.any(Function),
      expect.any(Function),
      expect.any(AbortSignal),
    );

    Date.now = originalNow;
  });

  it('loadMessages replaces messages and clears error', async () => {
    vi.mocked(client.sendMessageStream).mockRejectedValue(new Error('fail'));
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
