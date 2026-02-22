import { Amplify } from 'aws-amplify';

// Configure Amplify at module level (side effect) so it runs BEFORE
// @aws-amplify/auth is imported. The auth module auto-detects OAuth
// redirect codes on import and needs the config to already be set.

const userPoolId = import.meta.env.VITE_COGNITO_USER_POOL_ID;
const userPoolClientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
const domainPrefix = import.meta.env.VITE_COGNITO_DOMAIN;
const region = import.meta.env.VITE_AWS_REGION || 'us-east-2';
// Amplify v6 requires the full Cognito domain, not just the prefix
const domain = domainPrefix?.includes('.') ? domainPrefix : domainPrefix ? `${domainPrefix}.auth.${region}.amazoncognito.com` : undefined;

if (!userPoolId || !userPoolClientId) {
  console.warn('Cognito env vars not set — auth disabled');
} else {
  const redirectUrl = window.location.origin + '/';

  Amplify.configure({
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
  });
}
