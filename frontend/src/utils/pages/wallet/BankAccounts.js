import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Button,
  Stack,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import { 
  AccountBalance as BankIcon,
  MoreVert as MoreVertIcon,
  Add as AddIcon 
} from '@mui/icons-material';
import { externalAccountsAPI } from '../../utils/api';

/**
 * BankAccounts page – displays linked bank accounts as payment methods
 * for deposits and withdrawals
 */
export default function BankAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch list on mount
  useEffect(() => {
    async function load() {
      try {
        const resp = await externalAccountsAPI.getAccounts();
        setAccounts(resp.data.accounts || []);
      } catch (e) {
        console.error(e);
        setError(e.response?.data?.detail || e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Box sx={{ pt: 10, display: 'flex', justifyContent: 'center' }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ mt: 4 }}>{error}</Alert>;

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>
          Linked Payment Methods
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => (window.location.href = '/wallet/link-bank')}
          sx={{ borderRadius: 2 }}
        >
          Add
        </Button>
      </Box>
      
      {accounts.length === 0 ? (
        <Card sx={{ p: 4, textAlign: 'center', bgcolor: 'grey.50' }}>
          <BankIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No payment methods linked
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Link a bank account to deposit and withdraw funds
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => (window.location.href = '/wallet/link-bank')}
          >
            Link Bank Account
          </Button>
        </Card>
      ) : (
        <Stack spacing={2}>
          {accounts.map((account) => (
            <PaymentMethodCard key={account.id} account={account} />
          ))}
        </Stack>
      )}
    </Box>
  );
}

function PaymentMethodCard({ account }) {
  const [anchorEl, setAnchorEl] = useState(null);
  
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDelete = async () => {
    try {
      await externalAccountsAPI.deleteAccount(account.id);
      // Refresh page to update list
      window.location.reload();
    } catch (error) {
      console.error('Failed to delete account:', error);
      alert('Failed to delete account. Please try again.');
    }
    handleMenuClose();
  };

  return (
    <Card sx={{ 
      p: 0, 
      border: 1, 
      borderColor: 'grey.200',
      '&:hover': { 
        borderColor: 'primary.main',
        boxShadow: 2
      }
    }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Avatar sx={{ bgcolor: '#1976d2', width: 48, height: 48 }}>
              <BankIcon />
            </Avatar>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography variant="h6" fontWeight={600}>
                  {account.bank_name}
                </Typography>
                <Box sx={{ 
                  px: 1, 
                  py: 0.25, 
                  borderRadius: 1, 
                  bgcolor: account.active ? 'success.main' : 'warning.main',
                  color: 'white'
                }}>
                  <Typography variant="caption" fontWeight={500}>
                    {account.active ? 'Active' : 'Inactive'}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="text.secondary">
                ****{account.last4}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => window.location.href = '/wallet/deposit'}
                disabled={!account.active}
                sx={{ minWidth: 80 }}
              >
                Deposit
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => window.location.href = '/wallet/withdraw'}
                disabled={!account.active}
                sx={{ minWidth: 80 }}
              >
                Withdraw
              </Button>
            </Stack>
            <IconButton onClick={handleMenuOpen}>
              <MoreVertIcon />
            </IconButton>
          </Box>
        </Box>
        
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
            Remove Account
          </MenuItem>
        </Menu>
      </CardContent>
    </Card>
  );
} 