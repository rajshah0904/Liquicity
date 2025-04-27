import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Button, 
  CircularProgress, 
  Alert,
  Paper 
} from '@mui/material';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AnimatedBackground } from '../components/ui/ModernUIComponents';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

const VerifyEmail = () => {
  const [verifying, setVerifying] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  
  const { verifyEmailLink } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    const verifyToken = async () => {
      try {
        // Get token from URL query params
        const params = new URLSearchParams(location.search);
        const token = params.get('token');
        
        if (!token) {
          setError('Verification token is missing.');
          setVerifying(false);
          return;
        }
        
        const result = await verifyEmailLink(token);
        
        if (result) {
          setSuccess(true);
          // Redirect to dashboard after successful verification
          setTimeout(() => {
            navigate('/dashboard');
          }, 3000);
        } else {
          setError('Email verification failed. The link may have expired.');
        }
      } catch (err) {
        console.error('Verification error:', err);
        setError('Email verification failed. Please try again or contact support.');
      } finally {
        setVerifying(false);
      }
    };
    
    verifyToken();
  }, [verifyEmailLink, location, navigate]);
  
  return (
    <>
      <AnimatedBackground />
      <Container maxWidth="sm" sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        minHeight: '100vh',
        position: 'relative',
        zIndex: 1,
      }}>
        <Box
          sx={{
            background: '#111111',
            borderRadius: 2,
            padding: 4,
            width: '100%',
            maxWidth: 480,
            textAlign: 'center',
          }}
        >
          <Typography variant="h5" gutterBottom sx={{ color: 'white', mb: 3 }}>
            Email Verification
          </Typography>
          
          {verifying ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
              <CircularProgress size={60} sx={{ mb: 3 }} />
              <Typography variant="body1">
                Verifying your email...
              </Typography>
            </Box>
          ) : success ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
              <CheckCircleIcon sx={{ fontSize: 60, color: 'success.main', mb: 3 }} />
              <Typography variant="body1" paragraph>
                Your email has been successfully verified!
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                You will be redirected to the dashboard shortly.
              </Typography>
              <Button 
                variant="contained" 
                color="primary" 
                component={Link} 
                to="/dashboard"
                sx={{ mt: 2 }}
              >
                Continue to Dashboard
              </Button>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
              <ErrorOutlineIcon sx={{ fontSize: 60, color: 'error.main', mb: 3 }} />
              <Alert severity="error" sx={{ mb: 3, width: '100%' }}>
                {error}
              </Alert>
              <Typography variant="body2" paragraph>
                Please try again or contact support if the issue persists.
              </Typography>
              <Button 
                variant="contained" 
                color="primary" 
                component={Link} 
                to="/login"
                sx={{ mt: 2 }}
              >
                Return to Login
              </Button>
            </Box>
          )}
        </Box>
      </Container>
    </>
  );
};

export default VerifyEmail; 