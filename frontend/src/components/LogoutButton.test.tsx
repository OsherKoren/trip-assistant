import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LogoutButton } from './LogoutButton';
import { AuthContext } from '../auth/AuthContext';
import type { AuthContextType } from '../auth/types';

function mockAuthContext(overrides: Partial<AuthContextType> = {}): AuthContextType {
  return {
    user: { email: 'a@b.com' },
    isAuthenticated: true,
    isLoading: false,
    signIn: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
    getToken: vi.fn(),
    signInWithGoogle: vi.fn(),
    ...overrides,
  };
}

describe('LogoutButton', () => {
  it('renders sign out button', () => {
    const ctx = mockAuthContext();
    render(
      <AuthContext.Provider value={ctx}>
        <LogoutButton />
      </AuthContext.Provider>
    );
    expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument();
  });

  it('calls signOut on click', async () => {
    const user = userEvent.setup();
    const ctx = mockAuthContext();
    render(
      <AuthContext.Provider value={ctx}>
        <LogoutButton />
      </AuthContext.Provider>
    );

    await user.click(screen.getByRole('button', { name: /sign out/i }));
    expect(ctx.signOut).toHaveBeenCalled();
  });
});
