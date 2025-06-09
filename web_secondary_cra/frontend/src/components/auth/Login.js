import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';

export const LoginButton = () => {
  const { loginWithRedirect } = useAuth0();

  return (
    <button 
      onClick={() => loginWithRedirect()}
      className="btn btn-primary"
    >
      Log In
    </button>
  );
};

export const SignupButton = () => {
  const { loginWithRedirect } = useAuth0();

  return (
    <button 
      onClick={() => loginWithRedirect({
        authorizationParams: {
          screen_hint: 'signup',
        }
      })}
      className="btn btn-secondary"
    >
      Sign Up
    </button>
  );
};

export default LoginButton; 