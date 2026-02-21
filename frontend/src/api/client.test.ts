import { describe, it, expect, vi, beforeEach } from 'vitest';
import { sendMessage } from './client';
import type { MessageResponse } from '../types';

const mockResponse: MessageResponse = {
  answer: 'You rented a car from Sixt.',
  category: 'car_rental',
  confidence: 0.95,
  source: null,
};

describe('sendMessage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('sends correct POST request', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    await sendMessage('What car did we rent?');

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/messages'),
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: 'What car did we rent?' }),
      }),
    );
  });

  it('returns parsed MessageResponse', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await sendMessage('What car did we rent?');

    expect(result).toEqual(mockResponse);
  });

  it('throws on non-OK response (400)', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
    });

    await expect(sendMessage('bad request')).rejects.toThrow('Failed to send message');
  });

  it('throws on non-OK response (500)', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });

    await expect(sendMessage('server error')).rejects.toThrow('Failed to send message');
  });

  it('throws on network error', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(sendMessage('hello')).rejects.toThrow('Failed to fetch');
  });

  it('request body contains { question } JSON', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    await sendMessage('Where is our hotel?');

    const callArgs = vi.mocked(fetch).mock.calls[0];
    const body = JSON.parse(callArgs[1]?.body as string);
    expect(body).toEqual({ question: 'Where is our hotel?' });
  });
});
