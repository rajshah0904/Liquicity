import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { CircularProgress, Box, Typography, Alert } from '@mui/material';

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, isLoading, user, getAccessTokenSilently, logout } = useAuth0();
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // This parses Auth0's appState from URL if available
    const parseAppState = async () => {
      try {
        if (!isLoading && isAuthenticated) {
          // Log for debugging
          console.log('AuthCallback: Auth0 authenticated user', user);
          console.log('AuthCallback: Location', location);
  
          // Get the token and set it for API calls
          const token = await getAccessTokenSilently();
          localStorage.setItem('auth_token', token);
          
          // Import API and set headers
          const { default: api } = await import('../utils/api');
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Check for signup flag (used for new registrations)
          const isNewSignup = localStorage.getItem('isNewSignup') === 'true';
          
          // Verify the user exists in our backend unless we are processing a fresh signup
          let userRowExists = true;
          try {
            const checkResp = await api.get('/user/check');
            userRowExists = checkResp.data?.exists;
          } catch (checkErr) {
            console.error('AuthCallback: /user/check failed', checkErr);
            userRowExists = false;
          }

          if (!userRowExists) {
            if (isNewSignup) {
              // Legitimate first-time signup – allow the flow to continue to KYC
              console.log('AuthCallback: user not yet registered but isNewSignup=true – continue');
            } else {
              // Something is wrong (row deleted?) – force remote logout and send to signup page
              localStorage.removeItem('auth_token');
              await logout({ logoutParams: { returnTo: `${window.location.origin}/signup?noaccount=true` } });
              return; // stop further navigation
            }
          }
          
          // Check URL for Auth0 state parameter to detect appState
          const params = new URLSearchParams(location.search);
          const hasCode = params.has('code');
          const hasState = params.has('state');
          
          console.log('AuthCallback: isNewSignup=', isNewSignup, 'hasCode=', hasCode, 'hasState=', hasState);
          
          if (isNewSignup) {
            // Clear the flag
            localStorage.removeItem('isNewSignup');
            console.log('AuthCallback: Redirecting to KYC');
            navigate('/kyc-verification');
          } else {
            console.log('AuthCallback: Redirecting to dashboard');
            navigate('/dashboard');
          }
        } else if (!isLoading && !isAuthenticated) {
          console.log('AuthCallback: Not authenticated, going to login');
          navigate('/login');
        }
      } catch (err) {
        console.error('AuthCallback error:', err);
        setError(err.message || 'An error occurred during authentication');
      }
    };
    
    parseAppState();
  }, [isLoading, isAuthenticated, navigate, location, user, getAccessTokenSilently, logout]);
  
  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh'
    }}>
      {isLoading ? (
        <>
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 3 }}>
            Processing your sign-in...
          </Typography>
        </>
      ) : error ? (
        <Alert severity="error" sx={{ maxWidth: 500 }}>
          {error}
        </Alert>
      ) : (
        <>
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 3 }}>
            Redirecting you...
          </Typography>
        </>
      )}
    </Box>
  );
};

export default AuthCallback; 