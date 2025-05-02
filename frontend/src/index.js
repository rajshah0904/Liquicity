import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { UserProvider } from './context/UserContext';
import { Auth0Provider } from '@auth0/auth0-react';
import { CustomThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';

// Import the custom fonts
import '@fontsource/inter/300.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
// Pull Auth0 values from environment
const domain   = process.env.REACT_APP_AUTH0_DOMAIN;
const clientId = process.env.REACT_APP_AUTH0_CLIENT_ID;
const audience = process.env.REACT_APP_AUTH0_AUDIENCE;

// Debug: log Auth0 config
console.log('Auth0 Config:', { domain, clientId, audience, redirectUri: window.location.origin });

root.render(
  <React.StrictMode>
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{ redirect_uri: window.location.origin, audience }}
      useRefreshTokens={true}
      cacheLocation="localstorage"
    >
      <AuthProvider>
        <BrowserRouter>
          <CustomThemeProvider>
            <UserProvider>
              <App />
            </UserProvider>
          </CustomThemeProvider>
        </BrowserRouter>
      </AuthProvider>
    </Auth0Provider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals(); 