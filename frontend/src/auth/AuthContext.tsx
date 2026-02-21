import { useEffect, useState, type ReactNode } from 'react';
import {
  getCurrentUser,
  signIn as amplifySignIn,
  signUp as amplifySignUp,
  signOut as amplifySignOut,
  signInWithRedirect,
  fetchAuthSession,
} from 'aws-amplify/auth';
import { Hub } from 'aws-amplify/utils';
import type { AuthUser } from './types';
import { AuthContext } from './context';

export { AuthContext };

async function resolveUser(): Promise<AuthUser> {
  const session = await fetchAuthSession();
  const claims = session.tokens?.idToken?.payload;
  return {
    email: (claims?.email as string) ?? '',
    name: claims?.name as string | undefined,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = Hub.listen('auth', async ({ payload }) => {
      console.log('[Auth] Hub event:', payload.event, payload);
      if (payload.event === 'signInWithRedirect') {
        const resolved = await resolveUser();
        setUser(resolved);
      }
      if (payload.event === 'signInWithRedirect_failure') {
        console.error('[Auth] OAuth redirect failed:', payload.data);
      }
      if (payload.event === 'signedOut') {
        setUser(null);
      }
    });
    return unsubscribe;
  }, []);

  useEffect(() => {
    getCurrentUser()
      .then(() => resolveUser())
      .then(setUser)
      .catch((err) => {
        console.log('[Auth] getCurrentUser failed:', err);
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const signIn = async (email: string, password: string) => {
    await amplifySignIn({ username: email, password });
    const resolved = await resolveUser();
    setUser(resolved);
  };

  const signUp = async (email: string, password: string, name: string) => {
    await amplifySignUp({
      username: email,
      password,
      options: { userAttributes: { email, name } },
    });
    await amplifySignIn({ username: email, password });
    const resolved = await resolveUser();
    setUser(resolved);
  };

  const handleSignOut = async () => {
    await amplifySignOut();
    setUser(null);
  };

  const getToken = async (): Promise<string> => {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();
    if (!token) throw new Error('No auth token available');
    return token;
  };

  const signInWithGoogle = () => {
    signInWithRedirect({ provider: 'Google' });
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isLoading,
        signIn,
        signUp,
        signOut: handleSignOut,
        getToken,
        signInWithGoogle,
        googleSignInUrl: null,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
