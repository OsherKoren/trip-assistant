import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { Chat } from './Chat';
import * as client from '../api/client';
import type { MessageResponse } from '../types';

vi.mock('../api/client');

const mockResponse: MessageResponse = {
  answer: 'You rented a car from Sixt.',
  category: 'car_rental',
  confidence: 0.95,
  source: null,
};

describe('Chat', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders MessageList and MessageInput', () => {
    render(<Chat />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    expect(screen.getByText('No messages yet')).toBeInTheDocument();
  });

  it('displays error message when error exists', async () => {
    vi.mocked(client.sendMessage).mockRejectedValue(new Error('Network error'));
    render(<Chat />);

    await userEvent.type(screen.getByRole('textbox'), 'hello{Enter}');

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Network error');
    });
  });

  it('sends message through the full flow', async () => {
    vi.mocked(client.sendMessage).mockResolvedValue(mockResponse);
    render(<Chat />);

    await userEvent.type(screen.getByRole('textbox'), 'What car did we rent?{Enter}');

    await waitFor(() => {
      expect(screen.getByText('What car did we rent?')).toBeInTheDocument();
      expect(screen.getByText('You rented a car from Sixt.')).toBeInTheDocument();
    });
  });
});
