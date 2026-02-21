import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useMessages } from './useMessages';
import * as client from '../api/client';
import type { MessageResponse } from '../types';

vi.mock('../api/client');

const mockResponse: MessageResponse = {
  answer: 'You rented a car from Sixt.',
  category: 'car_rental',
  confidence: 0.95,
  source: null,
};

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
    vi.mocked(client.sendMessage).mockResolvedValue(mockResponse);
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('What car did we rent?');
    });

    expect(result.current.messages[0].role).toBe('user');
    expect(result.current.messages[0].content).toBe('What car did we rent?');
  });

  it('sets isLoading while waiting', async () => {
    let resolveApi!: (value: MessageResponse) => void;
    vi.mocked(client.sendMessage).mockImplementation(
      () => new Promise((resolve) => { resolveApi = resolve; }),
    );
    const { result } = renderHook(() => useMessages());

    act(() => {
      result.current.sendMessage('hello');
    });

    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      resolveApi(mockResponse);
    });

    expect(result.current.isLoading).toBe(false);
  });

  it('adds assistant response after API call', async () => {
    vi.mocked(client.sendMessage).mockResolvedValue(mockResponse);
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('What car did we rent?');
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].role).toBe('assistant');
    expect(result.current.messages[1].content).toBe('You rented a car from Sixt.');
    expect(result.current.messages[1].category).toBe('car_rental');
  });

  it('sets error on API failure', async () => {
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

    await act(async () => {
      await result.current.sendMessage('fail');
    });
    expect(result.current.error).toBe('Network error');

    await act(async () => {
      await result.current.sendMessage('succeed');
    });
    expect(result.current.error).toBeNull();
  });

  it('messages have unique IDs', async () => {
    vi.mocked(client.sendMessage).mockResolvedValue(mockResponse);
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('first');
    });
    await act(async () => {
      await result.current.sendMessage('second');
    });

    const ids = result.current.messages.map((m) => m.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  it('messages have timestamps', async () => {
    vi.mocked(client.sendMessage).mockResolvedValue(mockResponse);
    const { result } = renderHook(() => useMessages());

    await act(async () => {
      await result.current.sendMessage('hello');
    });

    for (const msg of result.current.messages) {
      expect(msg.timestamp).toBeInstanceOf(Date);
    }
  });
});
