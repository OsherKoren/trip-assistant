import { render, screen, act, waitFor } from '@testing-library/react';
import { AuthProvider, AuthContext } from './AuthContext';
import { useContext } from 'react';

const mockGetCurrentUser = vi.fn();
const mockSignIn = vi.fn();
const mockSignUp = vi.fn();
const mockSignOut = vi.fn();
const mockFetchAuthSession = vi.fn();
const mockFetchUserAttributes = vi.fn();
const mockSignInWithRedirect = vi.fn();

vi.mock('aws-amplify/auth', () => ({
  getCurrentUser: (...args: unknown[]) => mockGetCurrentUser(...args),
  signIn: (...args: unknown[]) => mockSignIn(...args),
  signUp: (...args: unknown[]) => mockSignUp(...args),
  signOut: (...args: unknown[]) => mockSignOut(...args),
  fetchAuthSession: (...args: unknown[]) => mockFetchAuthSession(...args),
  fetchUserAttributes: (...args: unknown[]) => mockFetchUserAttributes(...args),
  signInWithRedirect: (...args: unknown[]) => mockSignInWithRedirect(...args),
}));

vi.mock('aws-amplify/utils', () => ({
  Hub: {
    listen: vi.fn(() => vi.fn()),
  },
}));

function TestConsumer() {
  const auth = useContext(AuthContext);
  if (!auth) return <div>no context</div>;
  return (
    <div>
      <span data-testid="loading">{String(auth.isLoading)}</span>
      <span data-testid="authenticated">{String(auth.isAuthenticated)}</span>
      <span data-testid="email">{auth.user?.email ?? 'none'}</span>
      <button onClick={() => auth.signIn('a@b.com', 'pass')}>sign in</button>
      <button onClick={() => auth.signUp('a@b.com', 'pass', 'Alice')}>sign up</button>
      <button onClick={() => auth.signOut()}>sign out</button>
      <button onClick={async () => {
        try {
          const t = await auth.getToken();
          document.title = t;
        } catch (err) {
          document.title = `ERROR:${(err as Error).message}`;
        }
      }}>get token</button>
    </div>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('restores session on mount when user exists', async () => {
    mockGetCurrentUser.mockResolvedValue({ userId: '1' });
    mockFetchUserAttributes.mockResolvedValue({ email: 'a@b.com', name: 'Alice' });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    expect(screen.getByTestId('email')).toHaveTextContent('a@b.com');
  });

  it('sets loading false when no session', async () => {
    mockGetCurrentUser.mockRejectedValue(new Error('no user'));

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
  });

  it('signIn sets user', async () => {
    mockGetCurrentUser.mockRejectedValue(new Error('no user'));
    mockSignIn.mockResolvedValue({});
    mockFetchUserAttributes.mockResolvedValue({ email: 'a@b.com' });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    await act(async () => {
      screen.getByText('sign in').click();
    });

    expect(mockSignIn).toHaveBeenCalledWith({ username: 'a@b.com', password: 'pass' });
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
  });

  it('signUp calls signUp then signIn', async () => {
    mockGetCurrentUser.mockRejectedValue(new Error('no user'));
    mockSignUp.mockResolvedValue({});
    mockSignIn.mockResolvedValue({});
    mockFetchUserAttributes.mockResolvedValue({ email: 'a@b.com', name: 'Alice' });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    await act(async () => {
      screen.getByText('sign up').click();
    });

    expect(mockSignUp).toHaveBeenCalledWith({
      username: 'a@b.com',
      password: 'pass',
      options: { userAttributes: { email: 'a@b.com', name: 'Alice' } },
    });
    expect(mockSignIn).toHaveBeenCalled();
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
  });

  it('signOut clears user', async () => {
    mockGetCurrentUser.mockResolvedValue({ userId: '1' });
    mockFetchUserAttributes.mockResolvedValue({ email: 'a@b.com' });
    mockSignOut.mockResolvedValue(undefined);

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    await act(async () => {
      screen.getByText('sign out').click();
    });

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
  });

  it('getToken returns id token', async () => {
    mockGetCurrentUser.mockResolvedValue({ userId: '1' });
    mockFetchUserAttributes.mockResolvedValue({ email: 'a@b.com' });
    mockFetchAuthSession.mockResolvedValue({
      tokens: { idToken: { toString: () => 'test-token-123' } },
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    await act(async () => {
      screen.getByText('get token').click();
    });

    expect(document.title).toBe('test-token-123');
  });

  it('getToken throws when no token available', async () => {
    mockGetCurrentUser.mockResolvedValue({ userId: '1' });
    mockFetchUserAttributes.mockResolvedValue({ email: 'a@b.com' });
    mockFetchAuthSession.mockResolvedValue({ tokens: undefined });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    await act(async () => {
      screen.getByText('get token').click();
    });

    expect(document.title).toBe('ERROR:No auth token available');
  });
});
