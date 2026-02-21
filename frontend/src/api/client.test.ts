import { describe, it, expect, vi, beforeEach } from 'vitest';
import { sendMessage } from './client';
import type { MessageResponse } from '../types';

const mockResponse: MessageResponse = {
  answer: 'You rented a car from Sixt.',
  category: 'car_rental',
  confidence: 0.95,
  source: null,
};

const mockGetToken = vi.fn().mockResolvedValue('test-token');

describe('sendMessage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    mockGetToken.mockResolvedValue('test-token');
  });

  it('sends correct POST request with auth header', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    await sendMessage('What car did we rent?', mockGetToken);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/messages'),
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({ question: 'What car did we rent?' }),
      }),
    );
  });

  it('returns parsed MessageResponse', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await sendMessage('What car did we rent?', mockGetToken);

    expect(result).toEqual(mockResponse);
  });

  it('throws on non-OK response (400)', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
    });

    await expect(sendMessage('bad request', mockGetToken)).rejects.toThrow('Failed to send message');
  });

  it('throws on non-OK response (500)', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });

    await expect(sendMessage('server error', mockGetToken)).rejects.toThrow('Failed to send message');
  });

  it('throws on network error', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(sendMessage('hello', mockGetToken)).rejects.toThrow('Failed to fetch');
  });

  it('request body contains { question } JSON', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    await sendMessage('Where is our hotel?', mockGetToken);

    const callArgs = vi.mocked(fetch).mock.calls[0];
    const body = JSON.parse(callArgs[1]?.body as string);
    expect(body).toEqual({ question: 'Where is our hotel?' });
  });

  it('calls getToken before sending request', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    await sendMessage('hello', mockGetToken);

    expect(mockGetToken).toHaveBeenCalled();
  });
});
