import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Alert,
  InputAdornment,
  Link,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import api from '../utils/api';

// Icons
import GoogleIcon from '@mui/icons-material/Google';
import EmailIcon from '@mui/icons-material/Email';
import PersonIcon from '@mui/icons-material/Person';

// Custom components
import { AnimatedBackground } from '../components/ui/ModernUIComponents';

const SignUpContainer = styled(Container)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  position: 'relative',
  zIndex: 1,
}));

const SignUpCard = styled(Box)(({ theme }) => ({
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

const SignUp = () => {
  const { loginWithPopup, getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleEmailSignUp = async e => {
    e.preventDefault();
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }
    setError('');
    setLoading(true);
    try {
      // Open Auth0 signup popup
      await loginWithPopup({ authorizationParams: { screen_hint: 'signup', login_hint: email } });
      // Get token and set API header
      const token = await getAccessTokenSilently();
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Navigate to KYC page
      navigate('/kyc-verification');
    } catch (err) {
      setError(err.message || 'Signup failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    setError('');
    setLoading(true);
    try {
      // Open Auth0 Google signup popup
      await loginWithPopup({ authorizationParams: { connection: 'google-oauth2' } });
      // Get token and set API header
      const token = await getAccessTokenSilently();
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Navigate to KYC page
      navigate('/kyc-verification');
    } catch (err) {
      setError(err.message || 'Google signup failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = () => navigate('/login');

  return (
    <>
      <AnimatedBackground />
      <SignUpContainer maxWidth="sm">
        <SignUpCard>
          <Typography variant="h5" gutterBottom sx={{ color:'white'}}>Create an Account</Typography>
          {error && <Alert severity="error">{error}</Alert>}
          <Box component="form" onSubmit={handleEmailSignUp} sx={{ mt:2 }}>
            <StyledTextField
              fullWidth
              placeholder="name@example.com"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              InputProps={{ startAdornment: (<InputAdornment position="start"><EmailIcon/></InputAdornment>) }}
            />
            <EmailButton fullWidth type="submit" sx={{ mt:2 }}>
              Sign up with Email
            </EmailButton>
          </Box>
          <DividerWithText><span>OR</span></DividerWithText>
          <GoogleButton fullWidth onClick={handleGoogleSignUp}>
            <GoogleIcon sx={{ mr:1 }}/> Continue with Google
          </GoogleButton>
          <Box sx={{ mt:2 }}>Already have an account? <Link component="button" onClick={handleLogin}>Log in</Link></Box>
        </SignUpCard>
      </SignUpContainer>
    </>
  );
};

export default SignUp;