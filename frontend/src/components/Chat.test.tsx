import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { Chat } from './Chat';
import type { Message } from '../types';

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    getToken: vi.fn().mockResolvedValue('mock-token'),
  }),
}));

const defaultProps = {
  messages: [] as Message[],
  isLoading: false,
  error: null as string | null,
  onSend: vi.fn(),
  onFeedback: vi.fn(),
};

describe('Chat', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    defaultProps.onSend = vi.fn();
    defaultProps.onFeedback = vi.fn();
  });

  it('renders MessageList and MessageInput', () => {
    render(<Chat {...defaultProps} />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });

  it('displays error message when error exists', () => {
    render(<Chat {...defaultProps} error="Network error" />);
    expect(screen.getByRole('alert')).toHaveTextContent('Network error');
  });

  it('calls onSend when submitting a message', async () => {
    render(<Chat {...defaultProps} />);

    await userEvent.type(screen.getByRole('textbox'), 'What car did we rent?{Enter}');

    expect(defaultProps.onSend).toHaveBeenCalledWith('What car did we rent?');
  });

  it('renders messages passed via props', () => {
    const messages: Message[] = [
      { id: '1', role: 'user', content: 'Hello', timestamp: new Date() },
      { id: '2', role: 'assistant', content: 'Hi there!', timestamp: new Date() },
    ];
    render(<Chat {...defaultProps} messages={messages} />);

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });
});
