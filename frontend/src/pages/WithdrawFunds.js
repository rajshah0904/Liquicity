import React, { useState, useEffect } from 'react';
import { 
  Container, Box, Typography, TextField, Button, 
  Grid, Paper, CircularProgress, Alert, FormControl,
  InputLabel, Select, MenuItem, Divider
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { initiateWithdrawal, listBankAccounts, linkBankAccount } from '../utils/stripeUtils';
import api from '../utils/api';

const WithdrawFunds = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [bankAccounts, setBankAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [walletBalance, setWalletBalance] = useState(0);
  
  // Check URL parameters for status
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const withdrawalSuccess = params.get('withdrawal_success');
    const withdrawalError = params.get('withdrawal_error');
    const linkStatus = params.get('linkStatus');
    
    if (withdrawalSuccess === 'true') {
      setSuccess('Withdrawal initiated successfully. Funds will be deposited into your bank account within 1-3 business days.');
    } else if (withdrawalError === 'true') {
      setError('Withdrawal could not be processed. Please try again or contact support.');
    } else if (linkStatus === 'success') {
      setSuccess('Bank account linked successfully!');
      // Refresh bank accounts list
      fetchBankAccounts();
    } else if (linkStatus === 'canceled') {
      setError('Bank account linking was canceled.');
    }
    
    // Clear URL parameters
    if (withdrawalSuccess || withdrawalError || linkStatus) {
      navigate('/withdraw', { replace: true });
    }
  }, [location, navigate]);
  
  useEffect(() => {
    const fetchData = async () => {
      if (currentUser?.id) {
        try {
          // Fetch bank accounts
          fetchBankAccounts();
          
          // Fetch wallet balance
          const walletResponse = await api.get(`/wallet/${currentUser.id}`);
          if (walletResponse.status === 200) {
            setWalletBalance(walletResponse.data.main_balance || 0);
            setCurrency(walletResponse.data.base_currency || 'USD');
          }
        } catch (err) {
          console.error('Failed to fetch data', err);
          setError('Unable to load your accounts. Please try again later.');
        }
      }
    };
    
    fetchData();
  }, [currentUser]);
  
  const fetchBankAccounts = async () => {
    if (!currentUser?.id) return;
    
    try {
      const accounts = await listBankAccounts(currentUser.id);
      setBankAccounts(accounts);
      if (accounts.length > 0) {
        setSelectedAccount(accounts[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch bank accounts', err);
    }
  };
  
  const handleAmountChange = (e) => {
    const value = e.target.value;
    if (value === '' || (/^\d+(\.\d{0,2})?$/.test(value) && parseFloat(value) > 0)) {
      setAmount(value);
    }
  };
  
  const handleWithdraw = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }
    
    if (parseFloat(amount) > walletBalance) {
      setError(`Insufficient funds. Your balance is ${formatCurrency(walletBalance)}`);
      return;
    }
    
    if (!selectedAccount) {
      setError('Please select a bank account or add a new one');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Convert amount to cents for Stripe
      const amountInCents = Math.round(parseFloat(amount) * 100);
      
      // Initiate withdrawal to bank account
      const result = await initiateWithdrawal(
        amountInCents,
        currency.toLowerCase(),
        selectedAccount,
        currentUser.id
      );
      
      if (result.success) {
        setSuccess(`Withdrawal of ${formatCurrency(parseFloat(amount))} initiated successfully. Funds will be deposited into your bank account within 1-3 business days.`);
        setAmount('');
        
        // Update wallet balance
        setWalletBalance(prev => prev - parseFloat(amount));
      } else {
        setError('Failed to process withdrawal. Please try again later.');
      }
    } catch (err) {
      console.error('Withdrawal error:', err);
      setError('Failed to process withdrawal. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddBankAccount = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const linkUrl = await linkBankAccount(currentUser.id);
      // For Stripe Financial Connections, we need to use their SDK
      // For simplicity in this example, we'll just redirect
      window.location.href = linkUrl;
    } catch (err) {
      console.error('Error creating bank link:', err);
      setError('Unable to link bank account right now. Please try again later.');
      setLoading(false);
    }
  };
  
  const getCurrencySymbol = (currencyCode) => {
    switch(currencyCode) {
      case 'USD': return '$';
      case 'EUR': return '€';
      case 'GBP': return '£';
      default: return currencyCode;
    }
  };
  
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };
  
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper sx={{ p: 4, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom align="center" fontWeight="bold">
          Withdraw Funds
        </Typography>
        
        <Typography variant="body1" paragraph align="center" color="textSecondary" sx={{ mb: 4 }}>
          Transfer funds from your TerraFlow wallet to your bank account
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ my: 2 }}>
            {success}
          </Alert>
        )}
        
        <Box sx={{ 
          p: 2, 
          textAlign: 'center', 
          mb: 4, 
          bgcolor: 'rgba(0, 0, 0, 0.03)', 
          borderRadius: 1 
        }}>
          <Typography variant="subtitle1">
            Available Balance
          </Typography>
          <Typography variant="h4" fontWeight="bold">
            {formatCurrency(walletBalance)}
          </Typography>
        </Box>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, border: '1px solid rgba(0, 0, 0, 0.1)', borderRadius: 1, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Bank Account
              </Typography>
              
              {bankAccounts.length > 0 ? (
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="bank-account-label">Select Account</InputLabel>
                  <Select
                    labelId="bank-account-label"
                    value={selectedAccount}
                    label="Select Account"
                    onChange={(e) => setSelectedAccount(e.target.value)}
                  >
                    {bankAccounts.map(account => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.bank_name} •••• {account.last4}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ) : (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="textSecondary" paragraph>
                    You need to link a bank account to make withdrawals.
                  </Typography>
                </Box>
              )}
              
              <Button 
                variant="outlined" 
                onClick={handleAddBankAccount}
                fullWidth
              >
                {bankAccounts.length > 0 ? 'Link Another Account' : 'Link Bank Account'}
              </Button>
              
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Withdrawal Information
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Withdrawals typically take 1-3 business days to arrive in your bank account.
                </Typography>
              </Box>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, border: '1px solid rgba(0, 0, 0, 0.1)', borderRadius: 1, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Withdrawal Amount
              </Typography>
              
              <TextField
                label="Amount"
                variant="outlined"
                fullWidth
                value={amount}
                onChange={handleAmountChange}
                type="text"
                placeholder="0.00"
                InputProps={{
                  startAdornment: <Box component="span" sx={{ mr: 1 }}>{getCurrencySymbol(currency)}</Box>
                }}
                sx={{ mb: 3 }}
              />
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Fee:
                </Typography>
                <Typography variant="body2">
                  {formatCurrency(0)} {/* You could calculate fees here */}
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="body2" color="textSecondary">
                  You'll receive:
                </Typography>
                <Typography variant="body2" fontWeight="bold">
                  {amount ? formatCurrency(parseFloat(amount)) : formatCurrency(0)}
                </Typography>
              </Box>
              
              <Button
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                onClick={handleWithdraw}
                disabled={loading || !amount || parseFloat(amount) <= 0 || parseFloat(amount) > walletBalance || !selectedAccount}
                sx={{ py: 1.5, fontSize: '1.1rem' }}
              >
                {loading ? <CircularProgress size={24} /> : `Withdraw ${amount ? formatCurrency(parseFloat(amount)) : formatCurrency(0)}`}
              </Button>
            </Box>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 4 }} />
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="subtitle2" gutterBottom>
            Secure Processing
          </Typography>
          <Typography variant="body2" color="textSecondary">
            All withdrawals are securely processed through our banking partners. For security reasons, 
            your first withdrawal may require additional verification.
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <Button
              variant="text"
              onClick={() => navigate('/wallet')}
              sx={{ mx: 1 }}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default WithdrawFunds; 