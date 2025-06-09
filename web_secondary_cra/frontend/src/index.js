import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { UserProvider } from './context/UserContext';
import { CustomThemeProvider } from './context/ThemeContext';
import { Auth0Provider } from '@auth0/auth0-react';

// Import the custom fonts
import '@fontsource/inter/300.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';

// Auth0 configuration
const domain = process.env.REACT_APP_AUTH0_DOMAIN 
const clientId = process.env.REACT_APP_AUTH0_CLIENT_ID 
const audience = process.env.REACT_APP_AUTH0_AUDIENCE 
const redirectUri = window.location.origin;

// Debug: log Auth0 config
console.log('Auth0 Config:', { domain, clientId, audience, redirectUri });

// Handle redirects from Auth0 loginWithRedirect
// Perform a full navigation to the target path so React Router properly loads that route
const onRedirectCallback = (appState) => {
  // Always redirect to the callback handler which will parse appState
  const target = '/callback'; 
  // Navigate to the returnTo URL (including origin) to clear code/state
  window.location.replace(`${window.location.origin}${target}`);
};

ReactDOM.render(
  <React.StrictMode>
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        audience: audience,
        redirect_uri: redirectUri,
        scope: 'openid profile email offline_access'
      }}
      useRefreshTokens={true}
      cacheLocation="localstorage"
    >
      <BrowserRouter>
        <CustomThemeProvider>
          <UserProvider>
            <App />
          </UserProvider>
        </CustomThemeProvider>
      </BrowserRouter>
    </Auth0Provider>
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals(); 