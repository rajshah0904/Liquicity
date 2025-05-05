import React from 'react';
import { Container, Paper, Typography, Avatar, Box, Divider, Grid } from '@mui/material';
import { useAuth0 } from '@auth0/auth0-react';
import Profile from '../components/auth/Profile';

const ProfilePage = () => {
  const { isLoading, isAuthenticated } = useAuth0();

  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="h4">Loading profile...</Typography>
      </Container>
    );
  }

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="h4">Please log in to view your profile</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Your Profile
      </Typography>
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Profile />
      </Paper>
    </Container>
  );
};

export default ProfilePage; 