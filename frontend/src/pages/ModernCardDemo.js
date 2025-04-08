import React from 'react';
import { Container, Grid, Typography } from '@mui/material';
import ModernCard from '../components/ModernCard';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import SendIcon from '@mui/icons-material/Send';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import SecurityIcon from '@mui/icons-material/Security';

const ModernCardDemo = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Typography
        variant="h2"
        sx={{
          mb: 6,
          textAlign: 'center',
          color: '#FFFFFF',
          fontWeight: 700,
          letterSpacing: '-0.02em',
        }}
      >
        Modern Card Demo
      </Typography>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <ModernCard
            title="Secure Payments"
            subtitle="Bank-grade security"
            content="Experience the future of secure transactions with our advanced encryption and blockchain technology."
            icon={<SecurityIcon />}
            animationDelay={0.1}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <ModernCard
            title="Instant Transfers"
            subtitle="Send money globally"
            content="Transfer funds instantly to any corner of the world with our lightning-fast payment network."
            icon={<SendIcon />}
            animationDelay={0.2}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <ModernCard
            title="Multi-Currency"
            subtitle="Seamless conversion"
            content="Convert between currencies with minimal fees and real-time exchange rates."
            icon={<SwapHorizIcon />}
            animationDelay={0.3}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <ModernCard
            title="Smart Banking"
            subtitle="AI-powered insights"
            content="Get personalized financial insights and recommendations powered by advanced AI algorithms."
            icon={<AccountBalanceIcon />}
            animationDelay={0.4}
          />
        </Grid>
      </Grid>
    </Container>
  );
};

export default ModernCardDemo; 