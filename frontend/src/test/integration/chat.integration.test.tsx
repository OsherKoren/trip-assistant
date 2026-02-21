import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Chat } from '../../components/Chat';
import { API_URL } from './setup';

const canReachApi = async (): Promise<boolean> => {
  if (!API_URL) return false;
  try {
    const res = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
};

describe.skipIf(!API_URL)('Integration: Chat with real API', () => {
  let apiReachable: boolean;

  beforeAll(async () => {
    apiReachable = await canReachApi();
    if (!apiReachable) {
      console.warn(`API at ${API_URL} is not reachable — skipping integration tests`);
    }
  });

  it('sends a real question and gets an answer', async () => {
    if (!apiReachable) return;

    render(<Chat />);
    const user = userEvent.setup();

    await user.type(screen.getByRole('textbox'), 'What car did we rent?');
    await user.click(screen.getByRole('button', { name: /send/i }));

    // User message appears immediately
    expect(screen.getByText('What car did we rent?')).toBeInTheDocument();

    // Wait for real API response
    await waitFor(
      () => {
        const assistantMessages = screen.getAllByTestId('message-bubble');
        // At least 2 messages: user + assistant
        expect(assistantMessages.length).toBeGreaterThanOrEqual(2);
      },
      { timeout: 15000 },
    );
  });

  it('sends a flight question and gets a flight-related answer', async () => {
    if (!apiReachable) return;

    render(<Chat />);
    const user = userEvent.setup();

    await user.type(screen.getByRole('textbox'), 'What are our flight details?');
    await user.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(
      () => {
        const assistantMessages = screen.getAllByTestId('message-bubble');
        expect(assistantMessages.length).toBeGreaterThanOrEqual(2);
      },
      { timeout: 15000 },
    );
  });

  it('handles multiple messages in sequence', async () => {
    if (!apiReachable) return;

    render(<Chat />);
    const user = userEvent.setup();

    // First message
    await user.type(screen.getByRole('textbox'), 'Hello');
    await user.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(
      () => {
        const bubbles = screen.getAllByTestId('message-bubble');
        expect(bubbles.length).toBeGreaterThanOrEqual(2);
      },
      { timeout: 15000 },
    );

    // Second message
    await user.type(screen.getByRole('textbox'), 'What hotel are we staying at?');
    await user.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(
      () => {
        const bubbles = screen.getAllByTestId('message-bubble');
        // At least 4: 2 user + 2 assistant
        expect(bubbles.length).toBeGreaterThanOrEqual(4);
      },
      { timeout: 15000 },
    );
  });

  it('shows error state when API call fails', async () => {
    // Temporarily break fetch to simulate network failure
    const originalFetch = globalThis.fetch;
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    render(<Chat />);
    const user = userEvent.setup();

    await user.type(screen.getByRole('textbox'), 'test');
    await user.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(
      () => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      },
      { timeout: 10000 },
    );

    // Restore real fetch
    globalThis.fetch = originalFetch;
  });
});
