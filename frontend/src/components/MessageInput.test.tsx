import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MessageInput } from './MessageInput';
import { vi } from 'vitest';

describe('MessageInput', () => {
  it('renders input and send button', () => {
    render(<MessageInput onSend={vi.fn()} disabled={false} />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('calls onSend with input value on submit', async () => {
    const onSend = vi.fn();
    render(<MessageInput onSend={onSend} disabled={false} />);

    await userEvent.type(screen.getByRole('textbox'), 'Hello');
    await userEvent.click(screen.getByRole('button', { name: /send/i }));

    expect(onSend).toHaveBeenCalledWith('Hello');
  });

  it('clears input after submit', async () => {
    render(<MessageInput onSend={vi.fn()} disabled={false} />);
    const input = screen.getByRole('textbox');

    await userEvent.type(input, 'Hello');
    await userEvent.click(screen.getByRole('button', { name: /send/i }));

    expect(input).toHaveValue('');
  });

  it('submits on Enter key press', async () => {
    const onSend = vi.fn();
    render(<MessageInput onSend={onSend} disabled={false} />);

    await userEvent.type(screen.getByRole('textbox'), 'Hello{Enter}');

    expect(onSend).toHaveBeenCalledWith('Hello');
  });

  it('disables input and button when disabled=true', () => {
    render(<MessageInput onSend={vi.fn()} disabled={true} />);
    expect(screen.getByRole('textbox')).toBeDisabled();
    expect(screen.getByRole('button', { name: /send/i })).toBeDisabled();
  });

  it('does not submit empty input', async () => {
    const onSend = vi.fn();
    render(<MessageInput onSend={onSend} disabled={false} />);

    await userEvent.click(screen.getByRole('button', { name: /send/i }));

    expect(onSend).not.toHaveBeenCalled();
  });
});
