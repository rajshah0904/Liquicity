import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  CircularProgress,
  Alert,
  Stack
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ArrowBack, Link as LinkIcon } from '@mui/icons-material';
import { externalAccountsAPI } from '../../utils/api';

export default function LinkBankUS() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleBack = () => {
    navigate('/wallet/link-bank');
  };

  // Function to initialize Plaid Link
  const initializePlaidLink = async () => {
    try {
      setLoading(true);
      setError(null);

      // Ensure Plaid script is present
      if (!window.Plaid) {
        // Try to load script dynamically and wait for it
        await new Promise((resolve, reject) => {
          const existing = document.querySelector('script[src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"]');
          if (existing) {
            existing.addEventListener('load', resolve);
            existing.addEventListener('error', () => reject(new Error('Plaid script failed to load')));
          } else {
            const script = document.createElement('script');
            script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
            script.async = true;
            script.onload = resolve;
            script.onerror = () => reject(new Error('Plaid script failed to load'));
            document.body.appendChild(script);
          }
        });
        if (!window.Plaid) {
          throw new Error('Plaid script not available after load');
        }
      }
      
      const response = await externalAccountsAPI.getPlaidLinkToken();
      
      if (response && response.data && response.data.link_token) {
        // Open Plaid Link automatically once we have the token
        openPlaidLink(response.data.link_token);
      } else {
        throw new Error('Failed to get Plaid link token');
      }
    } catch (err) {
      console.error('Error initializing Plaid Link:', err);
      setError('Failed to initialize Plaid Link. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Function to open Plaid Link
  const openPlaidLink = async (token) => {
    if (!token) return;
    
    const linkTokenUsed = token;  // pass same token back to server per Bridge docs
    const handler = window.Plaid.create({
      token,
      onSuccess: async (publicToken, metadata) => {
        try {
          setLoading(true);
          // Exchange the public token via Bridge
          await externalAccountsAPI.exchangePlaidToken(linkTokenUsed, publicToken);
          
          // Navigate back to wallet on success
          navigate('/wallet');
        } catch (err) {
          console.error('Error exchanging Plaid token:', err);
          setError('Failed to link your bank account. Please try again.');
        } finally {
          setLoading(false);
        }
      },
      onExit: (err) => {
        if (err) {
          console.error('Plaid Link exit with error:', err);
          setError('There was an issue connecting to your bank. Please try again.');
        } else {
          // User closed Plaid Link without completing
          console.log('User closed Plaid Link');
        }
      },
      onEvent: (eventName, metadata) => {
        console.log('Plaid Link Event:', eventName, metadata);
      }
    });
    
    handler.open();
  };

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={handleBack}
          sx={{ mb: 2 }}
        >
          Back to Country Selection
        </Button>
        
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" fontWeight={600} gutterBottom>
            Link US Bank Account
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Securely connect your US bank account with Plaid
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 4 }}>
          <Stack spacing={3} alignItems="center" textAlign="center">
            <LinkIcon sx={{ fontSize: 48, color: 'primary.main' }} />
            
            <Box>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Connect with Plaid
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Plaid securely connects to your bank account using bank-grade security. 
                Your login credentials are never shared with Liquicity.
              </Typography>
            </Box>

            <Button 
              variant="contained" 
              size="large"
              fullWidth
              onClick={initializePlaidLink}
              disabled={loading}
              sx={{ 
                py: 2,
                backgroundColor: 'primary.main',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                  boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                }
              }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Connect with Plaid'
              )}
            </Button>

            <Typography variant="caption" color="text.secondary" sx={{ mt: 2 }}>
              🔒 Secured by bank-level encryption
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Container>
  );
} 