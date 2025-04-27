import React, { useState, useEffect } from 'react';
import { 
  Container, Box, Typography, TextField, Button, 
  Grid, Paper, CircularProgress, Alert, FormControl,
  InputLabel, Select, MenuItem, Divider, Card, CardContent,
  Switch, FormControlLabel
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { API_URL } from '../utils/constants';
import { 
  listBankAccounts, 
  linkBankAccount, 
  initiateDirectDeposit 
} from '../utils/paymentUtils';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import CreditCardIcon from '@mui/icons-material/CreditCard';

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
  const [depositMethod, setDepositMethod] = useState('bank');
  const [depositToWallet, setDepositToWallet] = useState(true);
  
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
      setLoading(true);
      const accounts = await listBankAccounts(currentUser.id);
      setBankAccounts(accounts);
      if (accounts.length > 0) {
        setSelectedAccount(accounts[0].id);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch bank accounts', err);
      setLoading(false);
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
  
  const handleDepositToggleChange = (e) => {
    setDepositToWallet(e.target.checked);
  };
  
  const handleDeposit = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const amountInCents = Math.round(parseFloat(amount) * 100);
      
      if (depositMethod === 'card') {
        // Direct API call to handle card payment
        const response = await api.post('/payment/deposit/card', {
          amount: amountInCents,
          currency: currency.toLowerCase(),
          userId: currentUser.id,
          depositToWallet
        });
        
        if (response.data.success) {
          setSuccess(`Card payment initiated successfully for ${getCurrencySymbol(currency)}${amount}.`);
          setAmount('');
        } else {
          setError('Failed to process card payment. Please try again.');
        }
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
          currentUser.id,
          depositToWallet
        );
        
        if (response.success) {
          setSuccess(`Bank transfer initiated successfully for ${getCurrencySymbol(currency)}${amount}. ${depositToWallet ? 'Funds will appear in your account once the transfer completes.' : 'Your payment method has been saved for future transactions.'}`);
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
      // Redirect to bank linking page
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
      <Paper sx={{ p: 4, borderRadius: 2, bgcolor: '#111', color: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
        <Typography variant="h4" gutterBottom align="center" fontWeight="bold">
          Deposit Funds
        </Typography>
        
        <Typography variant="body1" paragraph align="center" color="text.secondary" sx={{ mb: 4 }}>
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
            <Box sx={{ p: 2, border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Deposit Method
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="deposit-method-label">Payment Method</InputLabel>
                <Select
                  labelId="deposit-method-label"
                  id="deposit-method"
                  value={depositMethod}
                  onChange={handleDepositMethodChange}
                  label="Payment Method"
                >
                  <MenuItem value="card">Credit/Debit Card</MenuItem>
                  <MenuItem value="bank">Bank Account (ACH)</MenuItem>
                </Select>
              </FormControl>
              
              <FormControlLabel
                control={
                  <Switch 
                    checked={depositToWallet}
                    onChange={handleDepositToggleChange}
                    color="primary"
                  />
                }
                label={depositToWallet ? "Deposit to wallet" : "Save payment method for later"}
                sx={{ mb: 2 }}
              />
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {depositToWallet 
                  ? "Funds will be added to your wallet balance and can be used for payments."
                  : "Your payment method will be saved for future transactions without adding funds to your wallet."}
              </Typography>
              
              {depositMethod === 'bank' && (
                <>
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel id="bank-account-label">Select Bank Account</InputLabel>
                    <Select
                      labelId="bank-account-label"
                      id="bank-account"
                      value={selectedAccount}
                      onChange={(e) => setSelectedAccount(e.target.value)}
                      label="Select Bank Account"
                      disabled={bankAccounts.length === 0}
                    >
                      {bankAccounts.map((account) => (
                        <MenuItem key={account.id} value={account.id}>
                          {account.bank_name} (*{account.last4})
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <Button 
                    variant="outlined" 
                    color="primary" 
                    onClick={handleAddBankAccount}
                    startIcon={<AccountBalanceIcon />}
                    fullWidth
                  >
                    Link New Bank Account
                  </Button>
                </>
              )}
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Amount Details
              </Typography>
              
              <TextField
                fullWidth
                label="Amount"
                value={amount}
                onChange={handleAmountChange}
                type="text"
                placeholder="0.00"
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1 }}>{getCurrencySymbol(currency)}</Typography>
                }}
                sx={{ mb: 3 }}
              />
              
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="currency-label">Currency</InputLabel>
                <Select
                  labelId="currency-label"
                  id="currency"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  label="Currency"
                >
                  <MenuItem value="USD">USD - US Dollar</MenuItem>
                  <MenuItem value="EUR">EUR - Euro</MenuItem>
                  <MenuItem value="GBP">GBP - British Pound</MenuItem>
                </Select>
              </FormControl>
              
              <Button
                variant="contained"
                color="primary"
                onClick={handleDeposit}
                disabled={loading || !amount || parseFloat(amount) <= 0 || (depositMethod === 'bank' && !selectedAccount)}
                fullWidth
                sx={{ mt: 2 }}
              >
                {loading ? (
                  <CircularProgress size={24} sx={{ color: 'white' }} />
                ) : (
                  depositToWallet ? 'Deposit Funds' : 'Save Payment Method'
                )}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default DepositFunds; 