import { render, screen } from '@testing-library/react';
import { MessageBubble } from './MessageBubble';
import type { Message } from '../types';

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
});
