import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginPage } from './LoginPage';
import { AuthContext } from '../auth/AuthContext';
import type { AuthContextType } from '../auth/types';

function mockAuthContext(overrides: Partial<AuthContextType> = {}): AuthContextType {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    signIn: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
    getToken: vi.fn(),
    signInWithGoogle: vi.fn(),
    googleSignInUrl: 'https://example.com/oauth2/authorize?test=1',
    ...overrides,
  };
}

function renderLoginPage(auth: Partial<AuthContextType> = {}) {
  const ctx = mockAuthContext(auth);
  render(
    <AuthContext.Provider value={ctx}>
      <LoginPage />
    </AuthContext.Provider>
  );
  return ctx;
}

describe('LoginPage', () => {
  it('renders sign in form by default', () => {
    renderLoginPage();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    expect(screen.queryByLabelText('Name')).not.toBeInTheDocument();
  });

  it('toggles to sign up mode', async () => {
    const user = userEvent.setup();
    renderLoginPage();

    await user.click(screen.getByText('Sign Up'));
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign Up' })).toBeInTheDocument();
  });

  it('calls signIn with email and password', async () => {
    const user = userEvent.setup();
    const ctx = renderLoginPage();

    await user.type(screen.getByLabelText('Email'), 'a@b.com');
    await user.type(screen.getByLabelText('Password'), 'secret');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(ctx.signIn).toHaveBeenCalledWith('a@b.com', 'secret');
  });

  it('calls signUp with email, password, and name', async () => {
    const user = userEvent.setup();
    const ctx = renderLoginPage();

    await user.click(screen.getByText('Sign Up'));
    await user.type(screen.getByLabelText('Name'), 'Alice');
    await user.type(screen.getByLabelText('Email'), 'a@b.com');
    await user.type(screen.getByLabelText('Password'), 'secret');
    await user.click(screen.getByRole('button', { name: 'Sign Up' }));

    expect(ctx.signUp).toHaveBeenCalledWith('a@b.com', 'secret', 'Alice');
  });

  it('shows error on sign in failure', async () => {
    const user = userEvent.setup();
    const signIn = vi.fn().mockRejectedValue(new Error('Invalid credentials'));
    renderLoginPage({ signIn });

    await user.type(screen.getByLabelText('Email'), 'a@b.com');
    await user.type(screen.getByLabelText('Password'), 'wrong');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials');
  });

  it('renders Google sign in as a link', () => {
    renderLoginPage();
    const link = screen.getByRole('link', { name: 'Sign in with Google' });
    expect(link).toHaveAttribute('href', 'https://example.com/oauth2/authorize?test=1');
  });

  it('shows disabled button when Google URL is not available', () => {
    renderLoginPage({ googleSignInUrl: null });
    expect(screen.getByText('Google sign-in unavailable')).toBeDisabled();
  });

  it('disables submit button while submitting', async () => {
    const user = userEvent.setup();
    const signIn = vi.fn(() => new Promise(() => {})); // never resolves
    renderLoginPage({ signIn });

    await user.type(screen.getByLabelText('Email'), 'a@b.com');
    await user.type(screen.getByLabelText('Password'), 'pass');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(screen.getByRole('button', { name: 'Please wait...' })).toBeDisabled();
  });
});
