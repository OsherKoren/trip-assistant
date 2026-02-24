import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { MessageFeedback } from './MessageFeedback';
import type { Feedback } from '../types';
import { useState } from 'react';

vi.mock('../api/client', () => ({
  sendFeedback: vi.fn().mockResolvedValue({ status: 'received', id: 'test-id' }),
}));

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    getToken: vi.fn().mockResolvedValue('mock-token'),
  }),
}));

const defaultProps = {
  messageId: 'msg-server-789',
  onFeedback: vi.fn(),
};

// Wrapper that mimics how the parent manages feedback state
function FeedbackWrapper({ messageId }: { messageId: string }) {
  const [feedback, setFeedback] = useState<Feedback | undefined>();
  return (
    <MessageFeedback
      feedback={feedback}
      messageId={messageId}
      onFeedback={setFeedback}
    />
  );
}

describe('MessageFeedback', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders thumbs up and thumbs down buttons', () => {
    render(<MessageFeedback {...defaultProps} />);
    expect(screen.getByRole('button', { name: /thumbs up/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /thumbs down/i })).toBeInTheDocument();
  });

  it('does not show submit button before selecting a rating', () => {
    render(<MessageFeedback {...defaultProps} />);
    expect(screen.queryByRole('button', { name: /submit/i })).not.toBeInTheDocument();
  });

  it('shows submit button after selecting thumbs up', async () => {
    render(<FeedbackWrapper messageId="msg-test" />);
    await userEvent.click(screen.getByRole('button', { name: /thumbs up/i }));
    expect(screen.getByRole('button', { name: /submit feedback/i })).toBeInTheDocument();
  });

  it('shows submit button after selecting thumbs down', async () => {
    render(<FeedbackWrapper messageId="msg-test" />);
    await userEvent.click(screen.getByRole('button', { name: /thumbs down/i }));
    expect(screen.getByRole('button', { name: /submit feedback/i })).toBeInTheDocument();
  });

  it('allows toggling between thumbs up and down before submit', async () => {
    render(<FeedbackWrapper messageId="msg-test" />);

    // Select thumbs down — textarea appears
    await userEvent.click(screen.getByRole('button', { name: /thumbs down/i }));
    expect(screen.getByRole('textbox', { name: /feedback comment/i })).toBeInTheDocument();

    // Switch to thumbs up — textarea disappears
    await userEvent.click(screen.getByRole('button', { name: /thumbs up/i }));
    expect(screen.queryByRole('textbox', { name: /feedback comment/i })).not.toBeInTheDocument();

    // Switch back to thumbs down — textarea reappears
    await userEvent.click(screen.getByRole('button', { name: /thumbs down/i }));
    expect(screen.getByRole('textbox', { name: /feedback comment/i })).toBeInTheDocument();
  });

  it('shows textarea only for thumbs down', async () => {
    render(<FeedbackWrapper messageId="msg-test" />);

    await userEvent.click(screen.getByRole('button', { name: /thumbs up/i }));
    expect(screen.queryByRole('textbox', { name: /feedback comment/i })).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /thumbs down/i }));
    expect(screen.getByRole('textbox', { name: /feedback comment/i })).toBeInTheDocument();
  });

  it('calls sendFeedback API with thumbs up on submit', async () => {
    const { sendFeedback } = await import('../api/client');
    render(<FeedbackWrapper messageId="msg-test-answer" />);

    await userEvent.click(screen.getByRole('button', { name: /thumbs up/i }));
    await userEvent.click(screen.getByRole('button', { name: /submit feedback/i }));

    expect(sendFeedback).toHaveBeenCalledWith(
      expect.objectContaining({ message_id: 'msg-test-answer', rating: 'up' }),
      expect.any(Function),
    );
  });

  it('calls sendFeedback API with thumbs down and comment on submit', async () => {
    const { sendFeedback } = await import('../api/client');
    render(<FeedbackWrapper messageId="msg-test-answer" />);

    await userEvent.click(screen.getByRole('button', { name: /thumbs down/i }));
    await userEvent.type(screen.getByRole('textbox', { name: /feedback comment/i }), 'Wrong time');
    await userEvent.click(screen.getByRole('button', { name: /submit feedback/i }));

    expect(sendFeedback).toHaveBeenCalledWith(
      expect.objectContaining({
        message_id: 'msg-test-answer',
        rating: 'down',
        comment: 'Wrong time',
      }),
      expect.any(Function),
    );
  });

  it('disables buttons after submission', async () => {
    render(<FeedbackWrapper messageId="msg-test" />);

    await userEvent.click(screen.getByRole('button', { name: /thumbs up/i }));
    await userEvent.click(screen.getByRole('button', { name: /submit feedback/i }));

    expect(screen.getByRole('button', { name: /thumbs up/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /thumbs down/i })).toBeDisabled();
    expect(screen.queryByRole('button', { name: /submit feedback/i })).not.toBeInTheDocument();
  });

  it('highlights thumbs up when feedback rating is up', () => {
    render(
      <MessageFeedback {...defaultProps} feedback={{ rating: 'up' }} />,
    );

    const upButton = screen.getByRole('button', { name: /thumbs up/i });
    expect(upButton.className).toContain('text-green-600');
  });

  it('highlights thumbs down when feedback rating is down', () => {
    render(
      <MessageFeedback {...defaultProps} feedback={{ rating: 'down' }} />,
    );

    const downButton = screen.getByRole('button', { name: /thumbs down/i });
    expect(downButton.className).toContain('text-red-600');
  });
});
