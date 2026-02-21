import { Amplify } from '@aws-amplify/core';

export function configureAuth(): void {
  const userPoolId = import.meta.env.VITE_COGNITO_USER_POOL_ID;
  const userPoolClientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
  const domain = import.meta.env.VITE_COGNITO_DOMAIN;

  if (!userPoolId || !userPoolClientId) {
    console.warn('Cognito env vars not set — auth disabled');
    return;
  }

  const redirectUrl = window.location.origin + '/';

  const authConfig = {
    Auth: {
      Cognito: {
        userPoolId,
        userPoolClientId,
        loginWith: domain
          ? {
              oauth: {
                domain,
                scopes: ['openid', 'email', 'profile'],
                redirectSignIn: [redirectUrl],
                redirectSignOut: [redirectUrl],
                responseType: 'code' as const,
              },
            }
          : undefined,
      },
    },
  };

  console.log('[Auth] Configuring Amplify:', JSON.stringify(authConfig, null, 2));
  Amplify.configure(authConfig);
}
