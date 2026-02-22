import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { MessageList } from './MessageList';
import type { Message } from '../types';

vi.mock('../api/client', () => ({
  sendFeedback: vi.fn().mockResolvedValue({ status: 'received', id: 'test-id' }),
}));

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    getToken: vi.fn().mockResolvedValue('mock-token'),
  }),
}));

const messages: Message[] = [
  { id: '1', role: 'user', content: 'Hello', timestamp: new Date() },
  { id: '2', role: 'assistant', content: 'Hi there!', category: 'greeting', timestamp: new Date() },
];

const onFeedback = vi.fn();

describe('MessageList', () => {
  it('renders multiple messages', () => {
    render(<MessageList messages={messages} isLoading={false} onFeedback={onFeedback} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  it('renders empty state when no messages', () => {
    render(<MessageList messages={[]} isLoading={false} onFeedback={onFeedback} />);
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    expect(screen.getByText(/ask me anything about your family trip/i)).toBeInTheDocument();
  });

  it('shows loading indicator when isLoading=true', () => {
    render(<MessageList messages={[]} isLoading={true} onFeedback={onFeedback} />);
    expect(screen.getByRole('status')).toHaveTextContent('Thinking…');
  });

  it('hides loading indicator when isLoading=false', () => {
    render(<MessageList messages={messages} isLoading={false} onFeedback={onFeedback} />);
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });
});
