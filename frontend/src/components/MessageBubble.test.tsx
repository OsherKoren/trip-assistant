import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { MessageBubble } from './MessageBubble';
import type { Message } from '../types';

vi.mock('../api/client', () => ({
  sendFeedback: vi.fn().mockResolvedValue({ status: 'received', id: 'test-id' }),
}));

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    getToken: vi.fn().mockResolvedValue('mock-token'),
  }),
}));

const userMessage: Message = {
  id: 'msg-1',
  role: 'user',
  content: 'What car did we rent?',
  timestamp: new Date(),
};

const assistantMessage: Message = {
  id: 'msg-2',
  role: 'assistant',
  content: 'You rented a car from Sixt.',
  category: 'car_rental',
  timestamp: new Date(),
};

describe('MessageBubble', () => {
  it('renders user message content', () => {
    render(<MessageBubble message={userMessage} />);
    expect(screen.getByText('What car did we rent?')).toBeInTheDocument();
  });

  it('renders assistant message content', () => {
    render(<MessageBubble message={assistantMessage} />);
    expect(screen.getByText('You rented a car from Sixt.')).toBeInTheDocument();
  });

  it('user message is right-aligned', () => {
    const { container } = render(<MessageBubble message={userMessage} />);
    const wrapper = container.firstElementChild!;
    expect(wrapper.className).toContain('justify-end');
  });

  it('assistant message is left-aligned', () => {
    const { container } = render(<MessageBubble message={assistantMessage} />);
    const wrapper = container.firstElementChild!;
    expect(wrapper.className).toContain('justify-start');
  });

  it('shows feedback buttons for assistant messages', () => {
    const onFeedback = vi.fn();
    render(<MessageBubble message={assistantMessage} onFeedback={onFeedback} />);
    expect(screen.getByRole('button', { name: /thumbs up/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /thumbs down/i })).toBeInTheDocument();
  });

  it('does not show feedback buttons for user messages', () => {
    const onFeedback = vi.fn();
    render(<MessageBubble message={userMessage} onFeedback={onFeedback} />);
    expect(screen.queryByRole('button', { name: /thumbs up/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /thumbs down/i })).not.toBeInTheDocument();
  });
});
