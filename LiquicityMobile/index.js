/**
 * @format
 */

import 'react-native-get-random-values';
import {AppRegistry} from 'react-native';
import App from './App';
import {name as appName} from './app.json';
import { Auth0Provider } from 'react-native-auth0';
import config from './src/auth0-configuration';

const AppEntry = () => (
  <Auth0Provider domain={config.domain} clientId={config.clientId}>
    <App />
  </Auth0Provider>
);

AppRegistry.registerComponent(appName, () => AppEntry);
