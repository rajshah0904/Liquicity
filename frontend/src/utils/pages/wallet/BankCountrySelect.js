import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  Grid,
  Stack,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ArrowBack, AccountBalance } from '@mui/icons-material';

// Available countries for bank linking
const SUPPORTED_COUNTRIES = [
  {
    code: 'US',
    name: 'United States',
    region: 'us',
    currency: 'USD',
    available: true
  },
  {
    code: 'EU',
    name: 'European Union',
    region: 'eu', 
    currency: 'EUR',
    available: true
  },
  {
    code: 'MX',
    name: 'Mexico',
    region: 'mx',
    currency: 'MXN', 
    available: false
  },
  {
    code: 'BR',
    name: 'Brazil',
    region: 'br',
    currency: 'BRL',
    available: false
  },
  {
    code: 'AR',
    name: 'Argentina', 
    region: 'ar',
    currency: 'ARS',
    available: false
  },
  {
    code: 'CO',
    name: 'Colombia',
    region: 'co',
    currency: 'COP',
    available: false
  },
  {
    code: 'PE',
    name: 'Peru',
    region: 'pe',
    currency: 'PEN',
    available: false
  }
];

export default function BankCountrySelect() {
  const navigate = useNavigate();

  const handleCountrySelect = (country) => {
    if (!country.available) return;
    
    // Navigate to appropriate linking flow based on country
    if (country.code === 'US') {
      navigate('/wallet/link-bank/us');
    } else if (country.code === 'EU') {
      navigate('/wallet/link-bank/eu');
    }
    // Other countries will be implemented later
  };

  const handleBack = () => {
    navigate('/wallet');
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={handleBack}
          sx={{ mb: 2 }}
        >
          Back to Wallet
        </Button>
        
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <AccountBalance sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" fontWeight={600} gutterBottom>
            Link Bank Account
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Select your country to link a bank account
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {SUPPORTED_COUNTRIES.map((country) => (
          <Grid item xs={12} sm={6} md={4} key={country.code}>
            <Card 
              sx={{ 
                cursor: country.available ? 'pointer' : 'not-allowed',
                opacity: country.available ? 1 : 0.6,
                '&:hover': country.available ? {
                  boxShadow: 4,
                  transform: 'translateY(-2px)'
                } : {},
                transition: 'all 0.2s ease-in-out',
                height: '100%'
              }}
              onClick={() => handleCountrySelect(country)}
            >
              <CardContent sx={{ p: 3 }}>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="h6" fontWeight={600}>
                      {country.name}
                    </Typography>
                    {!country.available && (
                      <Chip label="Coming Soon" size="small" color="default" />
                    )}
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary">
                    Currency: {country.currency}
                  </Typography>
                  
                  {country.available && (
                    <Button 
                      variant="contained" 
                      fullWidth 
                      sx={{ mt: 2 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCountrySelect(country);
                      }}
                    >
                      Select {country.name}
                    </Button>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
} 