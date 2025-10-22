import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  CircularProgress,
  Alert
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
      
      const redirect = `${window.location.origin}/plaid/callback`;
      const response = await externalAccountsAPI.getPlaidLinkToken({ params: { redirect_uri: redirect } });
      
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
    
    const linkTokenUsed = token;  // pass same token back to server for Option A flow
    const isRedirectBack = window.location.href.includes('/plaid/callback');
    const handler = window.Plaid.create({
      token,
      // Required for OAuth institutions after redirect back to app
      ...(isRedirectBack ? { receivedRedirectUri: window.location.href } : {}),
      onSuccess: async (publicToken, metadata) => {
        try {
          setLoading(true);
          
          // Extract institution info from Plaid Link metadata (zero extra API calls!)
          const institutionName = metadata?.institution?.name || "Unknown Bank";
          const institutionId = metadata?.institution?.institution_id || null;
          
          console.log('🏦 Plaid Link Institution:', institutionName, institutionId);
          
          // Exchange the public token via Option A flow (Plaid → Identity verification → Manual Bridge account creation)
          const { data } = await externalAccountsAPI.exchangePlaidToken(linkTokenUsed, publicToken, {
            institution_name: institutionName,
            institution_id: institutionId
          });
          
          console.log('Plaid exchange successful:', data);
          
          // Show success message with account count
          const accountCount = data?.account_count || 0;
          if (accountCount > 0) {
            setError(null);
            // Navigate back to wallet on success
            navigate('/wallet');
          } else {
            setError('No accounts were linked. Please try again.');
          }
        } catch (err) {
          console.error('Error exchanging Plaid token:', err);
          const msg = err?.response?.data?.detail || err?.response?.data || err?.message || 'Failed to link your bank account. Please try again.';
          setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
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
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ maxWidth: 600, mx: 'auto' }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <LinkIcon sx={{ fontSize: 64, color: 'primary.main', mb: 3 }} />
          
          <Typography variant="h4" fontWeight={600} sx={{ mb: 2 }}>
            Link Bank Account
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, px: 2 }}>
            Connect your bank account securely to transfer funds instantly. Your login credentials are never shared with Liquicity.
          </Typography>
        </Box>

        <Card elevation={0} sx={{ border: '1px solid #e0e0e0', mb: 3 }}>
          <CardContent sx={{ p: 4 }}>
            <Button 
              variant="contained" 
              size="large"
              fullWidth
              onClick={initializePlaidLink}
              disabled={loading}
              sx={{ 
                py: 2.5,
                fontSize: '1.1rem',
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
                'Connect Bank Account'
              )}
            </Button>
            
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                🔒 Protected by bank-level encryption
              </Typography>
            </Box>
          </CardContent>
        </Card>

        <Box sx={{ textAlign: 'center', px: 3 }}>
          <Typography variant="body2" color="text.secondary">
            We use industry-standard security protocols to protect your information. Instant transfers, no routing numbers needed.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
} 