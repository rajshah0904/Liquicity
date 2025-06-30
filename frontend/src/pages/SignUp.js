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

// Helpers / constants that were missing
const validateEmail = (email) => /.+@.+\..+/.test(email);
const API_URL = process.env.REACT_APP_API_URL || '';

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
  const { loginWithPopup, getAccessTokenSilently, isAuthenticated, logout, user } = useAuth0();
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

      // If the user record does not yet exist, explicitly register it now
      if (!res.data.exists) {
        try {
          const regResp = await api.post('/onboard/register', undefined, { headers: { Authorization: `Bearer ${token}` } });
          if (regResp.data.tos_url) {
            const cb = encodeURIComponent(`${window.location.origin}/tos-callback`);
            window.location.href = `${regResp.data.tos_url}&redirect_uri=${cb}`;
            return true; // browser navigation triggered – abort remaining flow
          }
        } catch (regErr) {
          console.error('Registration failed', regErr);
          setError('Unable to complete registration. Please try again.');
        }
      }

      // If the user already exists, prompt them to log in instead of signing up
      if (res.data.exists) {
        setError('Account already exists. Please log in.');
        await logout({ logoutParams: { returnTo: `${window.location.origin}/signup?existing=true` } });
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

  const handleEmailSignUp = async (e) => {
    e.preventDefault();
    if (!validateEmail(email)) {
      setError("Please enter a valid email address");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Check if account exists (public endpoint without auth)
      const emailExists = await checkEmailExistsPublic(email);
      if (emailExists) {
        setError("An account with this email already exists");
        setLoading(false);
        return;
      }

      // Register with Auth0 using popup
      localStorage.setItem('isNewSignup', 'true');
      await loginWithPopup({
        authorizationParams: {
          screen_hint: 'signup',
          login_hint: email,
        },
      });

      // Get token for API calls
      const token = await getAccessTokenSilently();

      // Ask backend where the user is in the onboarding funnel
      const { data: check } = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });

      const goToStep = async (stepData) => {
        switch (stepData.next_step) {
          case 'register': {
            // brand-new user → create DB row and obtain ToS link
            const reg = await api.post(
              '/onboard/register',
              { email: user?.email || email },
              { headers: { Authorization: `Bearer ${token}` } },
            );
            localStorage.setItem('tos_url', reg.data.tos_url);
            navigate('/select-country');
            break;
          }
          case 'country':
            navigate('/select-country');
            break;
          case 'tos': {
            const cb = encodeURIComponent(`${window.location.origin}/tos-callback`);
            const tos = stepData.tos_url || localStorage.getItem('tos_url');
            if (tos) {
              window.location.href = `${tos}&redirect_uri=${cb}`;
            } else {
              navigate('/signup');
            }
            break;
          }
          case 'kyc':
            if (stepData.kyc_url) {
              window.location.href = stepData.kyc_url;
            } else {
              navigate('/kyc-verification');
            }
            break;
          default:
            navigate('/dashboard');
        }
      };

      await goToStep(check);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    try {
      setLoading(true);
      setError(null);

      // Sign up with Google using Auth0 popup
      localStorage.setItem('isNewSignup', 'true');
      await loginWithPopup({
        authorizationParams: {
          connection: 'google-oauth2',
          screen_hint: 'signup'
        }
      });

      // Get token for API calls
      const token = await getAccessTokenSilently();

      // Ask backend where the user is in the onboarding funnel
      const { data: check } = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });

      const goToStep = async (stepData) => {
        switch (stepData.next_step) {
          case 'register': {
            // brand-new user → create DB row and obtain ToS link
            const reg = await api.post(
              '/onboard/register',
              { email: user?.email || email },
              { headers: { Authorization: `Bearer ${token}` } },
            );
            localStorage.setItem('tos_url', reg.data.tos_url);
            navigate('/select-country');
            break;
          }
          case 'country':
            navigate('/select-country');
            break;
          case 'tos': {
            const cb = encodeURIComponent(`${window.location.origin}/tos-callback`);
            const tos = stepData.tos_url || localStorage.getItem('tos_url');
            if (tos) {
              window.location.href = `${tos}&redirect_uri=${cb}`;
            } else {
              navigate('/signup');
            }
            break;
          }
          case 'kyc':
            if (stepData.kyc_url) {
              window.location.href = stepData.kyc_url;
            } else {
              navigate('/kyc-verification');
            }
            break;
          default:
            navigate('/dashboard');
        }
      };

      await goToStep(check);

    } catch (err) {
      setError(err.message);
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