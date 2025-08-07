import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { CircularProgress, Box, Typography, Alert } from '@mui/material';

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, isLoading, user, getAccessTokenSilently, logout } = useAuth0();
  const [error, setError] = useState('');

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        if (!isLoading && isAuthenticated) {
          console.log('AuthCallback: Auth0 authenticated user', user);
          
          // Get the token and set it for API calls with email scope
          const token = await getAccessTokenSilently({
            authorizationParams: {
              scope: 'openid profile email'
            }
          });
          localStorage.setItem('auth_token', token);
          
          // Import API and set headers
          const { default: api } = await import('../utils/api');
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Check user's current onboarding state
          const checkResp = await api.get('/user/check');
          const userData = checkResp.data;
          
          console.log('AuthCallback: User state', userData);
          
          // Route user based on their current state
          await routeUserBasedOnState(userData, api, token);
          
        } else if (!isLoading && !isAuthenticated) {
          console.log('AuthCallback: Not authenticated, going to login');
          navigate('/login');
        }
      } catch (err) {
        console.error('AuthCallback error:', err);
        setError(err.message || 'An error occurred during authentication');
      }
    };
    
    handleAuthCallback();
  }, [isLoading, isAuthenticated, navigate, location, user, getAccessTokenSilently, logout]);

  const routeUserBasedOnState = async (userData, api, token) => {
    const { exists, next_step, force_fresh_start } = userData;
    
    if (!exists) {
      // New user - start registration
      await handleRegistration(api, token);
      return;
    }
    
    // PRODUCTION SECURITY: Handle forced fresh start
    if (force_fresh_start) {
      console.log('AuthCallback: Force fresh start detected - clearing cache and going to region');
      localStorage.clear();
      sessionStorage.clear();
      navigate('/kyc-verification');
      return;
    }
    
    // Existing user - resume where they left off
    switch (next_step) {
      case 'kyc':
        console.log('AuthCallback: Redirecting to KYC');
        navigate('/kyc-verification');
        break;
        
      case 'create_wallet':
        console.log('AuthCallback: KYC approved, creating wallet');
        try {
          const walletResp = await api.post('/user/create-wallet', {}, {
            headers: { Authorization: `Bearer ${token}` }
          });
          console.log('Wallet created:', walletResp.data);
          navigate('/dashboard');
        } catch (e) {
          console.error('Wallet creation error:', e);
          navigate('/kyc-verification'); // Fallback
        }
        break;
        
      case 'done':
        console.log('AuthCallback: Onboarding complete, going to dashboard');
        navigate('/dashboard');
        break;
        
      default:
        console.log('AuthCallback: Unknown state, going to KYC');
        navigate('/kyc-verification');
    }
  };

  const handleRegistration = async (api, token) => {
    try {
      console.log('AuthCallback: Registering new user');
      console.log('AuthCallback: User object:', user);
      console.log('AuthCallback: User email specifically:', user?.email);
      
      // Prepare registration payload - include email from user object if JWT token doesn't have it
      const registrationPayload = {};
      if (user?.email) {
        registrationPayload.email = user.email;
        console.log('AuthCallback: Using email from user object:', user.email);
      } else {
        console.error('AuthCallback: No email in user object!', user);
      }
      
      console.log('AuthCallback: Final registration payload:', registrationPayload);
      
      const regResp = await api.post('/onboard/register', registrationPayload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('Registration successful:', regResp.data);
      navigate('/kyc-verification');
    } catch (regErr) {
      console.error('Registration error:', regErr);
      if (regErr.response?.status === 409) {
        // User already exists, check their state
        const checkResp = await api.get('/user/check');
        await routeUserBasedOnState(checkResp.data, api, token);
      } else if (regErr.response?.status === 400 && regErr.response?.data?.detail?.includes('email claim missing')) {
        // Email claim missing - try with email from user object if available
        if (user?.email && !regErr.config?.data?.includes(user.email)) {
          console.log('AuthCallback: Retrying registration with email from user object');
          try {
            const retryResp = await api.post('/onboard/register', { email: user.email }, {
              headers: { Authorization: `Bearer ${token}` }
            });
            console.log('Registration successful on retry:', retryResp.data);
            navigate('/kyc-verification');
            return;
          } catch (retryErr) {
            console.error('AuthCallback: Retry also failed:', retryErr);
          }
        }
        
        // Still failing - force fresh signup
        console.error('AuthCallback: Email claim missing and no user email - forcing fresh signup');
        localStorage.clear();
        sessionStorage.clear();
        navigate('/signup?error=email_missing');
      } else {
        console.error('AuthCallback: Registration failed with error:', regErr.response?.data);
        setError('Registration failed. Please try signing up again.');
      }
    }
  };
  
  if (error) {
    return (
      <Box sx={{ 
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        p: 3
      }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Typography variant="body2">
          Please try logging in again.
        </Typography>
      </Box>
    );
  }
  
  return (
    <Box sx={{ 
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh'
    }}>
      <CircularProgress size={60} sx={{ mb: 2 }} />
      <Typography variant="h6" sx={{ mb: 1 }}>
        Setting up your account...
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Please wait while we get everything ready for you.
      </Typography>
    </Box>
  );
};

export default AuthCallback; 