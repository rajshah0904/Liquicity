import React, { useEffect, useState } from 'react';
import { Box, Typography, Card as MuiCard, CardContent, CircularProgress, Alert, Button } from '@mui/material';
import { bridgeAPI } from '../utils/api';

export default function CardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [card, setCard] = useState(null);

  useEffect(() => {
    async function fetchCard() {
      setLoading(true);
      setError(null);
      try {
        // Ensure customer exists and fetch their card(s)
        await bridgeAPI.getOrCreateCustomer();
        // There is no dedicated endpoint yet; assume backend exposes card via /wallet/overview?? TODO. For now placeholder
      } catch (err) {
        console.error(err);
        setError(err?.response?.data?.detail || err.message || 'Failed to load card');
      } finally {
        setLoading(false);
      }
    }
    fetchCard();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!card) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography>No card found.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Your Liquicity Visa Card
      </Typography>
      <MuiCard sx={{ maxWidth: 400 }}>
        <CardContent>
          <Typography variant="h6">•••• {card.last4}</Typography>
          <Typography variant="body2" color="text.secondary">Status: {card.state}</Typography>
        </CardContent>
      </MuiCard>
      {/* TODO: Freeze/unfreeze and add to mobile wallet later */}
      <Box sx={{ mt: 2 }}>
        <Button variant="contained" disabled>Freeze / Unfreeze (Coming soon)</Button>
      </Box>
    </Box>
  );
} 