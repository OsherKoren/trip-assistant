import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeToggle } from './ThemeToggle';

describe('ThemeToggle', () => {
  it('shows sun icon in dark mode', () => {
    render(<ThemeToggle theme="dark" onToggle={vi.fn()} />);
    expect(screen.getByLabelText('Switch to light mode')).toBeInTheDocument();
  });

  it('shows moon icon in light mode', () => {
    render(<ThemeToggle theme="light" onToggle={vi.fn()} />);
    expect(screen.getByLabelText('Switch to dark mode')).toBeInTheDocument();
  });

  it('calls onToggle when clicked', async () => {
    const onToggle = vi.fn();
    render(<ThemeToggle theme="light" onToggle={onToggle} />);

    await userEvent.click(screen.getByRole('button'));

    expect(onToggle).toHaveBeenCalledOnce();
  });
});
