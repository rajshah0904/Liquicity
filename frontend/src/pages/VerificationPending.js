import React, { useEffect } from 'react';
import { Box, Container, Typography, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const VerificationPending = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/dashboard');
    }, 5000); // redirect after 5 seconds
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <Container maxWidth="sm" sx={{ textAlign: 'center', pt: 8 }}>
      <Box sx={{ p: 4, bgcolor: '#111111', borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom sx={{ color: '#fff', mb: 2 }}>
          Verification Pending
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)', mb: 4 }}>
          Thanks for submitting your information. We&apos;re reviewing your details and will notify you once it's approved. You will be redirected to your dashboard shortly.
        </Typography>
        <CircularProgress color="inherit" />
      </Box>
    </Container>
  );
};

export default VerificationPending; 