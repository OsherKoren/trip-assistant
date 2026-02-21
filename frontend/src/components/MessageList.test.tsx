import { render, screen } from '@testing-library/react';
import { MessageList } from './MessageList';
import type { Message } from '../types';

const messages: Message[] = [
  { id: '1', role: 'user', content: 'Hello', timestamp: new Date() },
  { id: '2', role: 'assistant', content: 'Hi there!', category: 'greeting', timestamp: new Date() },
];

describe('MessageList', () => {
  it('renders multiple messages', () => {
    render(<MessageList messages={messages} isLoading={false} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  it('renders empty state when no messages', () => {
    render(<MessageList messages={[]} isLoading={false} />);
    expect(screen.getByText('No messages yet')).toBeInTheDocument();
  });

  it('shows loading indicator when isLoading=true', () => {
    render(<MessageList messages={[]} isLoading={true} />);
    expect(screen.getByRole('status')).toHaveTextContent('Thinking…');
  });

  it('hides loading indicator when isLoading=false', () => {
    render(<MessageList messages={messages} isLoading={false} />);
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });
});
