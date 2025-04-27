import React, { useState } from 'react';
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
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../utils/api';

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
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showVerification, setShowVerification] = useState(false);
  
  const navigate = useNavigate();
  
  const handleEmailSignUp = async (e) => {
    e.preventDefault();
    
    // Validate email
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    setError('');
    setLoading(true);
    
    try {
      // Send email verification link for signup
      await authAPI.sendSignupLink(email);
      setShowVerification(true);
    } catch (err) {
      setError('Failed to send verification email. Please try again.');
      console.error('Email verification error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleGoogleSignUp = async () => {
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
      
      // For demo purposes, we'll just simulate a successful signup
      setTimeout(() => {
        // This would be a real API call in production
        navigate('/register', { state: { email: email, fromGoogle: true } });
      }, 1000);
      
    } catch (err) {
      setError('Google signup failed. Please try again.');
      console.error('Google signup error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleLogin = () => {
    navigate('/login');
  };
  
  // If showing verification screen
  if (showVerification) {
    return (
      <>
        <AnimatedBackground />
        <SignUpContainer maxWidth="sm">
          <SignUpCard>
            <Typography variant="h5" align="center" gutterBottom>
              Check your email
            </Typography>
            
            <Box sx={{ textAlign: 'center', my: 4 }}>
              <EmailIcon sx={{ fontSize: 60, color: '#3B82F6', mb: 2 }} />
              <Typography variant="body1" paragraph>
                We've sent a verification link to:
              </Typography>
              <Typography variant="body1" fontWeight="500" paragraph>
                {email}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Click the link in the email to create your account and continue to registration
              </Typography>
            </Box>
            
            <Button 
              fullWidth 
              variant="outlined" 
              onClick={() => setShowVerification(false)}
              sx={{ mt: 2 }}
            >
              Back to Sign up
            </Button>
          </SignUpCard>
        </SignUpContainer>
      </>
    );
  }
  
  return (
    <>
      <AnimatedBackground />
      
      <SignUpContainer maxWidth="sm">
        <Typography variant="h4" sx={{ color: 'white', mb: 4, fontWeight: 500 }}>
          TerraFlow
        </Typography>
        
        <SignUpCard>
          <Typography variant="h5" gutterBottom sx={{ color: 'white', mb: 1 }}>
            Create your account
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
            Sign up with your email or Google account to get started
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <GoogleButton 
            fullWidth 
            startIcon={<GoogleIcon />}
            onClick={handleGoogleSignUp}
            disabled={loading}
          >
            Sign up with Google
          </GoogleButton>
          
          <DividerWithText>
            <span>OR</span>
          </DividerWithText>
          
          <form onSubmit={handleEmailSignUp}>
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
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Create Account'}
            </EmailButton>
            
            {/* Add Login button */}
            <Button 
              fullWidth 
              onClick={handleLogin}
              disabled={loading}
              sx={{
                backgroundColor: 'transparent',
                color: '#3B82F6',
                padding: '12px 0',
                textTransform: 'none',
                fontWeight: 500,
                marginTop: 2,
                border: '1px solid rgba(59, 130, 246, 0.5)',
                '&:hover': {
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  borderColor: '#3B82F6',
                }
              }}
            >
              Sign In Instead
            </Button>
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
        </SignUpCard>
      </SignUpContainer>
    </>
  );
};

export default SignUp; 