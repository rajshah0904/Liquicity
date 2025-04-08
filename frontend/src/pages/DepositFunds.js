import React, { useState, useEffect } from 'react';
import { 
  Container, Box, Typography, TextField, Button, 
  Grid, Paper, CircularProgress, Alert, FormControl,
  InputLabel, Select, MenuItem, Divider
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { createDepositCheckout, listBankAccounts, linkBankAccount, initiateDirectDeposit } from '../utils/stripeUtils';
import api from '../utils/api';

const DepositFunds = () => {
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
  const [depositMethod, setDepositMethod] = useState('card');
  
  // Check URL parameters for payment status
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const paymentSuccess = params.get('payment_success');
    const paymentCanceled = params.get('payment_canceled');
    const linkStatus = params.get('linkStatus');
    
    if (paymentSuccess === 'true') {
      setSuccess('Payment successful! Your funds have been added to your wallet.');
    } else if (paymentCanceled === 'true') {
      setError('Payment was canceled. No funds have been charged.');
    } else if (linkStatus === 'success') {
      setSuccess('Bank account linked successfully!');
      // Refresh bank accounts list
      fetchBankAccounts();
    } else if (linkStatus === 'canceled') {
      setError('Bank account linking was canceled.');
    }
    
    // Clear URL parameters
    if (paymentSuccess || paymentCanceled || linkStatus) {
      navigate('/deposit', { replace: true });
    }
  }, [location, navigate]);
  
  useEffect(() => {
    const fetchData = async () => {
      if (currentUser?.id) {
        try {
          // Fetch user's wallet to get default currency
          const walletResponse = await api.get(`/wallet/${currentUser.id}`);
          if (walletResponse.status === 200) {
            setCurrency(walletResponse.data.base_currency || 'USD');
          }
          
          // Fetch bank accounts
          fetchBankAccounts();
        } catch (err) {
          console.error('Failed to fetch user data', err);
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
  
  const handleDepositMethodChange = (e) => {
    setDepositMethod(e.target.value);
  };
  
  const handleDeposit = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Convert amount to cents for Stripe
      const amountInCents = Math.round(parseFloat(amount) * 100);
      
      if (depositMethod === 'card') {
        // Credit card deposit via Stripe Checkout
        const checkoutUrl = await createDepositCheckout(amountInCents, currency.toLowerCase(), currentUser);
        
        // Redirect to Stripe checkout
        window.location.href = checkoutUrl;
      } else if (depositMethod === 'bank') {
        // ACH transfer from saved bank account
        if (!selectedAccount) {
          setError('Please select a bank account or add a new one');
          setLoading(false);
          return;
        }
        
        // Direct deposit from bank account
        const response = await initiateDirectDeposit(
          amountInCents,
          currency.toLowerCase(),
          selectedAccount,
          currentUser.id
        );
        
        if (response.success) {
          setSuccess(`Bank transfer initiated successfully for ${getCurrencySymbol(currency)}${amount}. Funds will appear in your account once the transfer completes.`);
          setAmount('');
        } else {
          setError('Failed to initiate bank transfer. Please try again.');
        }
      }
    } catch (err) {
      console.error('Deposit error:', err);
      setError('Failed to process deposit. Please try again later.');
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
  
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper sx={{ p: 4, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom align="center" fontWeight="bold">
          Deposit Funds
        </Typography>
        
        <Typography variant="body1" paragraph align="center" color="textSecondary" sx={{ mb: 4 }}>
          Add funds to your TerraFlow wallet in {currency}
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
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, border: '1px solid rgba(0, 0, 0, 0.1)', borderRadius: 1, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Deposit Method
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="deposit-method-label">Select Method</InputLabel>
                <Select
                  labelId="deposit-method-label"
                  value={depositMethod}
                  label="Select Method"
                  onChange={handleDepositMethodChange}
                >
                  <MenuItem value="card">Credit or Debit Card</MenuItem>
                  <MenuItem value="bank">Bank Transfer (ACH)</MenuItem>
                </Select>
              </FormControl>
              
              {depositMethod === 'bank' && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    Your Linked Bank Accounts
                  </Typography>
                  
                  {bankAccounts.length > 0 ? (
                    <FormControl fullWidth sx={{ mb: 2 }}>
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
                    <Typography variant="body2" color="textSecondary" paragraph>
                      You don't have any linked bank accounts.
                    </Typography>
                  )}
                  
                  <Button 
                    variant="outlined" 
                    onClick={handleAddBankAccount}
                    fullWidth
                    sx={{ mt: 1 }}
                  >
                    {bankAccounts.length > 0 ? 'Link Another Account' : 'Link Bank Account'}
                  </Button>
                </>
              )}
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, border: '1px solid rgba(0, 0, 0, 0.1)', borderRadius: 1, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Deposit Amount
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
              
              <Typography variant="body2" color="textSecondary" paragraph>
                Funds will be immediately available in your wallet after the deposit is processed.
              </Typography>
              
              <Button
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                onClick={handleDeposit}
                disabled={loading || !amount || parseFloat(amount) <= 0 || (depositMethod === 'bank' && bankAccounts.length === 0)}
                sx={{ py: 1.5, fontSize: '1.1rem' }}
              >
                {loading ? <CircularProgress size={24} /> : `Deposit ${getCurrencySymbol(currency)}${amount || '0.00'}`}
              </Button>
            </Box>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 4 }} />
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="subtitle2" gutterBottom>
            Secure Payment Processing
          </Typography>
          <Typography variant="body2" color="textSecondary">
            All payments are securely processed by Stripe. Your financial information is never stored on our servers.
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

export default DepositFunds; 