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
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

// Icons
import GoogleIcon from '@mui/icons-material/Google';
import EmailIcon from '@mui/icons-material/Email';

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

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.1)',
    }
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

const SignUp = () => {
  const { loginWithRedirect } = useAuth0();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('existing') === 'true') setError('Account already exists. Please log in.');
    if (params.get('noaccount') === 'true') setError('No account found. Please sign up.');
  }, [location.search]);

  const handleEmailSignUp = async (e) => {
    e.preventDefault();
    if (!/.+@.+\..+/.test(email)) { setError('Please enter a valid email'); return; }
    setLoading(true); setError('');
    try {
      await loginWithRedirect({
        authorizationParams: {
          screen_hint: 'signup',
          login_hint: email,
          redirect_uri: `${window.location.origin}/callback`
        },
        appState: { returnTo: '/callback' }
      });
    } catch (err) {
      setError(err.message || 'Sign up failed.');
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    setLoading(true); setError('');
    try {
      await loginWithRedirect({
        authorizationParams: {
          connection: 'google-oauth2',
          screen_hint: 'signup',
          redirect_uri: `${window.location.origin}/callback`
        },
        appState: { returnTo: '/callback' }
      });
    } catch (err) {
      setError(err.message || 'Google sign up failed.');
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
              InputProps={{ startAdornment: (<InputAdornment position="start">@</InputAdornment>) }}
            />
            <EmailButton fullWidth type="submit" sx={{ mt:2 }} disabled={loading}>
              {loading ? <CircularProgress size={20} color="inherit"/> : 'Sign up with Email'}
            </EmailButton>
          </Box>
          <Button fullWidth sx={{ mt:2 }} startIcon={<GoogleIcon/>} onClick={handleGoogleSignUp} disabled={loading}>Continue with Google</Button>
          <Box sx={{ mt:2 }}>Already have an account? <Link component="button" onClick={handleLogin}>Log in</Link></Box>
        </SignUpCard>
      </SignUpContainer>
    </>
  );
};

export default SignUp;