import React from 'react';
import { Auth0Provider } from 'react-native-auth0';
import config from './src/auth0-configuration';
import Home from './src/components/Home';

const App = () => (
  <Auth0Provider domain={config.domain} clientId={config.clientId}>
    <Home />
  </Auth0Provider>
);

export default App;
