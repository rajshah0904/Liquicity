const authConfig = {
  domain: process.env.REACT_APP_AUTH0_DOMAIN,
  clientId: process.env.REACT_APP_AUTH0_CLIENT_ID,
  audience: process.env.REACT_APP_AUTH0_AUDIENCE,
  redirectUri: window.location.origin,
  postLogoutRedirectUri: window.location.origin,
  scope: 'openid profile email offline_access read:messages',
  cacheLocation: 'localstorage',
  useRefreshTokens: true,
  auth0Client: {
    domain: process.env.REACT_APP_AUTH0_DOMAIN,
    clientId: process.env.REACT_APP_AUTH0_CLIENT_ID,
  },
};

export default authConfig;
