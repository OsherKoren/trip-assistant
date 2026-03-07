import { describe, it, expect, vi, beforeEach } from 'vitest';
import { sendFeedback, sendMessage } from './client';
import type { FeedbackResponse, MessageResponse } from '../types';

const mockResponse: MessageResponse = {
  id: 'msg-server-123',
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
        body: JSON.stringify({ question: 'What car did we rent?', history: [] }),
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

  it('request body contains { question } JSON with empty history by default', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    await sendMessage('Where is our hotel?', mockGetToken);

    const callArgs = vi.mocked(fetch).mock.calls[0];
    const body = JSON.parse(callArgs[1]?.body as string);
    expect(body).toEqual({ question: 'Where is our hotel?', history: [] });
  });

  it('sends history in request body when provided', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const history = [
      { role: 'user' as const, content: 'What car did we rent?' },
      { role: 'assistant' as const, content: 'You rented from Sixt.' },
    ];

    await sendMessage('How much did it cost?', mockGetToken, history);

    const callArgs = vi.mocked(fetch).mock.calls[0];
    const body = JSON.parse(callArgs[1]?.body as string);
    expect(body).toEqual({ question: 'How much did it cost?', history });
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

const mockFeedbackResponse: FeedbackResponse = {
  status: 'received',
  message_id: 'msg-123',
};

describe('sendFeedback', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    mockGetToken.mockResolvedValue('test-token');
  });

  it('sends correct POST request to /api/feedback', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockFeedbackResponse),
    });

    await sendFeedback(
      { message_id: 'msg-123', rating: 'up' },
      mockGetToken,
    );

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/feedback'),
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
      }),
    );
  });

  it('returns parsed FeedbackResponse', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockFeedbackResponse),
    });

    const result = await sendFeedback(
      { message_id: 'msg-123', rating: 'down', comment: 'Wrong' },
      mockGetToken,
    );

    expect(result).toEqual(mockFeedbackResponse);
  });

  it('throws on non-OK response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });

    await expect(
      sendFeedback({ message_id: 'msg-123', rating: 'up' }, mockGetToken),
    ).rejects.toThrow('Failed to send feedback');
  });
});
