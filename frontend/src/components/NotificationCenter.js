import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, List, ListItem, ListItemText } from '@mui/material';
import api from '../utils/api';

export default function NotificationCenter() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const resp = await api.get('/notifications');
        setNotifications(resp.data.notifications || []);
      } catch (err) {
        console.error(err);
        setError(err?.response?.data?.detail || err.message || 'Failed to load notifications');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
        <CircularProgress size={20} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">{error}</Alert>
    );
  }

  if (notifications.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mt: 3, p: 2, border: (theme) => `1px solid ${theme.palette.divider}`, borderRadius: 1 }}>
      <Typography variant="h6" gutterBottom>
        Notifications
      </Typography>
      <List dense>
        {notifications.map((n) => (
          <ListItem key={n.id} divider>
            <ListItemText
              primary={n.message}
              secondary={new Date(n.created_at).toLocaleString()}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
} 