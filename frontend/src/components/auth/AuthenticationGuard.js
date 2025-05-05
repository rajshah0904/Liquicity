import { withAuthenticationRequired } from '@auth0/auth0-react';
import React from 'react';

const LoadingComponent = () => (
  <div className="loading-container">
    <div className="loading-spinner"></div>
    <p>Loading...</p>
  </div>
);

export const AuthenticationGuard = ({ component, ...props }) => {
  const Component = withAuthenticationRequired(component, {
    onRedirecting: () => <LoadingComponent />,
  });

  return <Component {...props} />;
};

export default AuthenticationGuard; 