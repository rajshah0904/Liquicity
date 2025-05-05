import React, { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AuthFlow = () => {
  const { user, isAuthenticated, isLoading, getAccessTokenSilently } = useAuth0();
  const [status, setStatus] = useState('checking');
  const navigate = useNavigate();

  useEffect(() => {
    const checkUserAndRedirect = async () => {
      if (isLoading || !isAuthenticated) return;

      try {
        setStatus('checking');
        // Get token from Auth0
        const token = await getAccessTokenSilently();
        
        // Check if user exists in our database
        const checkResponse = await axios.get(`/user/check`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        const { exists, kyc_complete } = checkResponse.data;
        
        if (!exists) {
          // Register the user in our database
          setStatus('registering');
          await axios.post(`/user/register`, {
            email: user.email,
            name: user.name,
            auth0_id: user.sub
          }, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          
          // After registration, redirect to KYC
          setStatus('redirecting_to_kyc');
          navigate('/kyc');
        } else if (!kyc_complete) {
          // User exists but KYC not complete
          setStatus('redirecting_to_kyc');
          navigate('/kyc');
        } else {
          // User exists and KYC complete
          setStatus('complete');
          navigate('/dashboard');
        }
      } catch (error) {
        console.error('Auth flow error:', error);
        setStatus('error');
      }
    };

    checkUserAndRedirect();
  }, [isAuthenticated, isLoading, user, getAccessTokenSilently, navigate]);

  if (isLoading) {
    return <div className="loading">Loading authentication...</div>;
  }

  if (!isAuthenticated) {
    return <div className="not-authenticated">Please log in to continue</div>;
  }

  // Different statuses in the auth flow
  const statusMessages = {
    checking: "Checking your account...",
    registering: "Setting up your account...",
    redirecting_to_kyc: "Redirecting to verification...",
    complete: "Account verified!",
    error: "There was an error processing your account"
  };

  return (
    <div className="auth-flow">
      <h2>Account Setup</h2>
      <div className="status-message">{statusMessages[status]}</div>
    </div>
  );
};

export default AuthFlow; 