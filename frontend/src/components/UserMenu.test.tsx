import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserMenu } from './UserMenu';

const defaultProps = {
  user: { email: 'test@example.com' },
  theme: 'light' as const,
  toggleTheme: vi.fn(),
  signOut: vi.fn().mockResolvedValue(undefined),
};

function renderUserMenu(overrides = {}) {
  const props = { ...defaultProps, ...overrides };
  return render(<UserMenu {...props} />);
}

describe('UserMenu', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders avatar with first letter of email', () => {
    renderUserMenu();
    expect(screen.getByText('T')).toBeInTheDocument();
  });

  it('renders avatar with first letter of name when available', () => {
    renderUserMenu({ user: { email: 'test@example.com', name: 'Alice' } });
    expect(screen.getByText('A')).toBeInTheDocument();
  });

  it('opens dropdown on click', async () => {
    const user = userEvent.setup();
    renderUserMenu();

    await user.click(screen.getByRole('button', { name: /user menu/i }));
    expect(screen.getByRole('menu')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('closes dropdown on outside click', async () => {
    const user = userEvent.setup();
    renderUserMenu();

    await user.click(screen.getByRole('button', { name: /user menu/i }));
    expect(screen.getByRole('menu')).toBeInTheDocument();

    await user.click(document.body);
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('closes dropdown on Escape key', async () => {
    const user = userEvent.setup();
    renderUserMenu();

    await user.click(screen.getByRole('button', { name: /user menu/i }));
    expect(screen.getByRole('menu')).toBeInTheDocument();

    await user.keyboard('{Escape}');
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('shows user email in dropdown', async () => {
    const user = userEvent.setup();
    renderUserMenu();

    await user.click(screen.getByRole('button', { name: /user menu/i }));
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('toggles theme and closes menu', async () => {
    const user = userEvent.setup();
    const toggleTheme = vi.fn();
    renderUserMenu({ toggleTheme });

    await user.click(screen.getByRole('button', { name: /user menu/i }));
    await user.click(screen.getByRole('menuitem', { name: /dark mode/i }));

    expect(toggleTheme).toHaveBeenCalled();
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('shows Light mode label when in dark theme', async () => {
    const user = userEvent.setup();
    renderUserMenu({ theme: 'dark' });

    await user.click(screen.getByRole('button', { name: /user menu/i }));
    expect(screen.getByRole('menuitem', { name: /light mode/i })).toBeInTheDocument();
  });

  it('calls signOut and closes menu', async () => {
    const user = userEvent.setup();
    const signOut = vi.fn().mockResolvedValue(undefined);
    renderUserMenu({ signOut });

    await user.click(screen.getByRole('button', { name: /user menu/i }));
    await user.click(screen.getByRole('menuitem', { name: /sign out/i }));

    expect(signOut).toHaveBeenCalled();
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('has correct aria attributes', () => {
    renderUserMenu();
    const button = screen.getByRole('button', { name: /user menu/i });
    expect(button).toHaveAttribute('aria-expanded', 'false');
    expect(button).toHaveAttribute('aria-haspopup', 'true');
  });

  it('sets aria-expanded to true when open', async () => {
    const user = userEvent.setup();
    renderUserMenu();

    const button = screen.getByRole('button', { name: /user menu/i });
    await user.click(button);
    expect(button).toHaveAttribute('aria-expanded', 'true');
  });
});
