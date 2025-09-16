import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Paper,
  Stack
} from '@mui/material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { AnimatedBackground } from '../components/ui/ModernUIComponents';

const ComingSoon = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [countryInfo, setCountryInfo] = useState({ name: '', region: '' });

  useEffect(() => {
    const countryCode = searchParams.get('country');
    const region = searchParams.get('region');
    
    // Map country codes to full names
    const countryNames = {
      'MX': 'Mexico',
      'BR': 'Brazil', 
      'CO': 'Colombia',
      'PE': 'Peru',
      'AR': 'Argentina'
    };
    
    setCountryInfo({
      name: countryNames[countryCode] || 'this country',
      region: region || ''
    });
  }, [searchParams]);

  const handleBackToRegionSelect = () => {
    navigate('/kyc-verification');
  };

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  return (
    <>
      <AnimatedBackground />
      <Box sx={{ 
        backgroundColor: 'transparent', 
        color: '#fff', 
        minHeight: '100vh', 
        display: 'flex',
        alignItems: 'center',
        py: 8 
      }}>
        <Container maxWidth="md">
          <Paper 
            elevation={24}
            sx={{
              background: 'linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 4,
              p: 6,
              textAlign: 'center'
            }}
          >
            <Stack spacing={4} alignItems="center">
              {/* Icon or Logo */}
              <Box
                sx={{
                  width: 120,
                  height: 120,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '3rem'
                }}
              >
                🚀
              </Box>

              {/* Title */}
              <Typography 
                variant="h3" 
                component="h1" 
                gutterBottom
                sx={{ 
                  fontWeight: 'bold',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Coming Soon!
              </Typography>

              {/* Message */}
              <Typography 
                variant="h5" 
                sx={{ mb: 2, color: 'rgba(255,255,255,0.9)' }}
              >
                KYC verification for {countryInfo.name}
              </Typography>

              <Typography 
                variant="body1" 
                sx={{ 
                  mb: 4, 
                  color: 'rgba(255,255,255,0.7)',
                  maxWidth: 600,
                  lineHeight: 1.6
                }}
              >
                We're working hard to bring Liquicity to {countryInfo.name}! 
                Our team is currently setting up compliance and partnerships 
                to ensure the best possible experience for users in your region.
              </Typography>

              <Typography 
                variant="body2" 
                sx={{ 
                  mb: 4, 
                  color: 'rgba(255,255,255,0.6)',
                  fontStyle: 'italic'
                }}
              >
                Want to be notified when we launch? Contact us at support@liquicity.io
              </Typography>

              {/* Action Buttons */}
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <Button 
                  variant="outlined"
                  size="large"
                  onClick={handleBackToRegionSelect}
                  sx={{
                    borderColor: 'rgba(255,255,255,0.3)',
                    color: 'white',
                    '&:hover': {
                      borderColor: 'rgba(255,255,255,0.5)',
                      backgroundColor: 'rgba(255,255,255,0.1)'
                    }
                  }}
                >
                  Select Different Region
                </Button>
                
                <Button 
                  variant="contained"
                  size="large" 
                  onClick={handleGoToDashboard}
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                    }
                  }}
                >
                  Go to Dashboard
                </Button>
              </Stack>
            </Stack>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default ComingSoon; 