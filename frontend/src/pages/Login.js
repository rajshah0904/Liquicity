import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper,
  CircularProgress,
  Alert,
  InputAdornment,
  Link
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

// Icons
import GoogleIcon from '@mui/icons-material/Google';
import EmailIcon from '@mui/icons-material/Email';

// Custom components
import { AnimatedBackground } from '../components/ui/ModernUIComponents';

const LoginContainer = styled(Container)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  position: 'relative',
  zIndex: 1,
}));

const LoginCard = styled(Box)(({ theme }) => ({
  background: '#111111',
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(4),
  width: '100%',
  maxWidth: 480,
  textAlign: 'center',
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.1)',
    }
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  '& .MuiInputBase-input': {
    color: '#FFFFFF',
    padding: '15px 15px 15px 50px',
  },
  '& .MuiInputAdornment-root': {
    position: 'absolute',
    left: '15px',
    top: '50%',
    transform: 'translateY(-50%)',
    pointerEvents: 'none',
  }
}));

const GoogleButton = styled(Button)(({ theme }) => ({
  backgroundColor: '#1e1e1e',
  color: '#FFFFFF',
  padding: '12px 0',
  textTransform: 'none',
  fontWeight: 500,
  border: '1px solid rgba(255, 255, 255, 0.1)',
  '&:hover': {
    backgroundColor: '#2a2a2a',
  }
}));

const EmailButton = styled(Button)(({ theme }) => ({
  backgroundColor: '#3B82F6',
  color: '#FFFFFF',
  padding: '12px 0',
  textTransform: 'none',
  fontWeight: 500,
  '&:hover': {
    backgroundColor: '#2563EB',
  }
}));

const DividerWithText = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  margin: theme.spacing(3, 0),
  '&::before, &::after': {
    content: '""',
    flex: 1,
    borderBottom: `1px solid rgba(255, 255, 255, 0.1)`,
  },
  '& > span': {
    padding: theme.spacing(0, 2),
    color: 'rgba(255, 255, 255, 0.5)',
    fontSize: '0.875rem',
  },
}));

// Add a styled Sign Up button
const SignUpButton = styled(Button)(({ theme }) => ({
  backgroundColor: 'transparent',
  color: '#3B82F6',
  padding: '12px 0',
  textTransform: 'none',
  fontWeight: 500,
  marginTop: theme.spacing(2),
  border: '1px solid rgba(59, 130, 246, 0.5)',
  '&:hover': {
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    borderColor: '#3B82F6',
  }
}));

const Login = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { loginWithPopup, isAuthenticated, getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();
  
  // After login, get token and navigate
  useEffect(() => {
    if (isAuthenticated) {
      getAccessTokenSilently().then(token => {
        import('../utils/api').then(({ default: api }) => {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          navigate('/dashboard');
        });
      });
    }
  }, [isAuthenticated, getAccessTokenSilently, navigate]);
  
  const handleEmailLogin = async e => {
    e.preventDefault();
    if (!email || !/\S+@\S+\.\S+/.test(email)) return setError('Please enter a valid email address');
    setError(''); setLoading(true);
    try {
      await loginWithPopup({ authorizationParams: { screen_hint: 'login', login_hint: email } });
    } catch (err) {
      setError(err.message || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      
      // In a production environment, this would trigger the Google OAuth flow
      const googleAuthWindow = window.open('', '_blank', 'width=500,height=600');
      if (googleAuthWindow) {
        googleAuthWindow.document.write('Loading Google authentication...');
        // The actual implementation would redirect to Google OAuth
        // and handle the callback with a token
      }
      
      // For demo purposes, we'll just simulate a successful login
      setTimeout(() => {
        // This would be a real API call in production
        // const response = await authAPI.googleLogin(token);
        // localStorage.setItem('auth_token', response.data.access_token);
        navigate('/dashboard');
      }, 1000);
      
    } catch (err) {
      setError('Google login failed. Please try again.');
      console.error('Google login error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSignUp = () => {
    navigate('/signup');
  };
  
  return (
    <>
      <AnimatedBackground />
      
      <LoginContainer maxWidth="sm">
        <Typography variant="h4" sx={{ color: 'white', mb: 4, fontWeight: 500 }}>
          Liquicity
        </Typography>
        
        <LoginCard>
          <Typography variant="h5" gutterBottom sx={{ color: 'white', mb: 1 }}>
            Sign in to your account
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
            Use your email below to sign in or create a new account
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <GoogleButton 
            fullWidth 
            startIcon={<GoogleIcon />}
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            Sign in with Google
          </GoogleButton>
          
          <DividerWithText>
            <span>OR</span>
          </DividerWithText>
          
          <form onSubmit={handleEmailLogin}>
            <Box sx={{ mb: 3, position: 'relative' }}>
              <Typography 
                variant="caption" 
                sx={{ 
                  position: 'absolute', 
                  left: 0, 
                  top: -20, 
                  color: 'rgba(255,255,255,0.7)',
                  textAlign: 'left'
                }}
              >
                Email address *
              </Typography>
              <StyledTextField
                fullWidth
                placeholder="name@example.com"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                variant="outlined"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailIcon sx={{ color: 'rgba(255,255,255,0.5)' }} />
                    </InputAdornment>
                  ),
                }}
                InputLabelProps={{ shrink: false }}
              />
            </Box>
            
            <EmailButton 
              fullWidth 
              type="submit"
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Continue with Email'}
            </EmailButton>
            
            {/* Add Sign Up button */}
            <SignUpButton 
              fullWidth 
              onClick={handleSignUp}
              disabled={loading}
            >
              Sign Up
            </SignUpButton>
          </form>
          
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              By clicking continue, you agree to our{' '}
              <Link href="#" underline="hover" sx={{ color: '#3B82F6' }}>
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="#" underline="hover" sx={{ color: '#3B82F6' }}>
                Privacy Policy
              </Link>
            </Typography>
          </Box>
        </LoginCard>
      </LoginContainer>
    </>
  );
};

export default Login; 