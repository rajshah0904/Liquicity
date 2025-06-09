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
  const { loginWithPopup, getAccessTokenSilently, isAuthenticated, logout } = useAuth0();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // On mount, check for query param indicating duplicate account message
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('existing') === 'true') {
      setError('Account already exists. Please log in.');
    }
    if (params.get('noaccount') === 'true') {
      setError('No account found. Please sign up first.');
    }
  }, [location.search]);

  // Clear duplicate-account error as soon as user edits the email field
  useEffect(() => {
    if (error && error.startsWith('Account already exists') && email) {
      // Remove query param if still present
      if (location.search.includes('existing=true')) {
        navigate('/signup', { replace: true });
      }
      setError('');
    }
  }, [email]);

  // helper used after popup to see if account already exists
  const checkExists = async (token) => {
    try {
      const res = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });
      if (res.data.exists) {
        // User already exists – sign them out locally and show error on this screen
        setError('Account already exists. Please log in.');
        await logout({ logoutParams: { returnTo: `${window.location.origin}/signup?existing=true` } });
        return true;
      }
    } catch (e) {
      console.error('check user error', e);
    }
    return false;
  };

  // If user already authenticated, confirm they don't already exist
  useEffect(() => {
    const guard = async () => {
      if (!isAuthenticated) return;
      if (localStorage.getItem('isNewSignup') === 'true') return; // skip duplicate guard during fresh signup
      try {
        const token = await getAccessTokenSilently();
        const res = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });
        if (res.data.exists) {
          setError('Account already exists. Please log in.');
          await logout({ logoutParams: { returnTo: `${window.location.origin}/signup?existing=true` } });
        }
      } catch(e) { console.error(e); }
    };
    guard();
  }, [isAuthenticated, getAccessTokenSilently, logout]);

  // Public check without auth
  const checkEmailExistsPublic = async (emailToCheck) => {
    try {
      const res = await api.get('/user/email-exists', { params: { email: emailToCheck } });
      return res.data.exists;
    } catch (err) {
      console.error('email-exists check failed', err);
      return false;
    }
  };

  const handleEmailSignUp = async e => {
    e.preventDefault();
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    // Early duplicate check to avoid hitting Auth0 signup flow
    const already = await checkEmailExistsPublic(email);
    if (already) {
      setError('Account already exists. Please log in.');
      // add query param so page refresh still shows error
      navigate('/signup?existing=true', { replace: true });
      return; // do NOT open Auth0 popup
    }

    // Mark flow as new signup so other guards know
    localStorage.setItem('isNewSignup', 'true');

    setError('');
    setLoading(true);
    try {
      // Trigger Auth0 hosted signup page (popup) pre-filled with the email
      await loginWithPopup({
        authorizationParams: {
          screen_hint: 'signup',
          login_hint: email,
        },
      });

      // Get token and set API header for subsequent calls
      const token = await getAccessTokenSilently();
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // It is safe to go straight to the KYC route after successful signup
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
      // Mark flow as new signup
      localStorage.setItem('isNewSignup', 'true');

      // Open Auth0 Google signup popup
      await loginWithPopup({ authorizationParams: { connection: 'google-oauth2' } });
      // Get token and set API header
      const token = await getAccessTokenSilently();
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // If the account already exists we bail out early via duplicate guard
      const exists = await checkExists(token);
      if (exists) return;

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