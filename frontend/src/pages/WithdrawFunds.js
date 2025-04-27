import React, { useState, useEffect } from 'react';
import { 
  Container, Box, Typography, TextField, Button, 
  Grid, Paper, CircularProgress, Alert, FormControl,
  InputLabel, Select, MenuItem, Divider, Card, CardContent
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { API_URL } from '../utils/constants';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import MoneyOffIcon from '@mui/icons-material/MoneyOff';

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
            setWalletBalance(walletResponse.data.fiat_balance || 0);
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
      setLoading(true);
      const response = await api.get(`/payment/bank-accounts/${currentUser.id}`);
      const accounts = response.data || [];
      
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
      const amountDecimal = parseFloat(amount);
      
      const result = await api.post('/payment/withdraw', {
        amount: amountDecimal,
        currency: currency,
        bankAccountId: selectedAccount,
        userId: currentUser.id
      });
      
      if (result.data.success) {
        setSuccess(`Withdrawal of ${formatCurrency(parseFloat(amount))} initiated successfully. Funds will be deposited into your bank account within 1-3 business days.`);
        setAmount('');
        
        setWalletBalance(prev => prev - parseFloat(amount));
      } else if (result.data.redirectUrl) {
        window.location.href = result.data.redirectUrl;
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
      
      const response = await api.post('/payment/link-bank-account', {
        userId: currentUser.id
      });
      
      if (response.data && response.data.redirectUrl) {
        window.location.href = response.data.redirectUrl;
      } else {
        throw new Error('Failed to get bank linking URL');
      }
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
      <Paper sx={{ p: 4, borderRadius: 2, bgcolor: '#111', color: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}>
        <Typography variant="h4" gutterBottom align="center" fontWeight="bold">
          Withdraw Funds
        </Typography>
        
        <Typography variant="body1" paragraph align="center" color="text.secondary" sx={{ mb: 4 }}>
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
          borderRadius: 2,
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}>
          <Typography variant="h6" gutterBottom>
            Available Balance
          </Typography>
          <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            {formatCurrency(walletBalance)}
          </Typography>
        </Box>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Bank Account
              </Typography>
              
              {bankAccounts.length > 0 ? (
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel id="bank-account-label">Select Bank Account</InputLabel>
                  <Select
                    labelId="bank-account-label"
                    id="bank-account"
                    value={selectedAccount}
                    onChange={(e) => setSelectedAccount(e.target.value)}
                    label="Select Bank Account"
                  >
                    {bankAccounts.map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.bank_name} (*{account.last4})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ) : (
                <Card sx={{ bgcolor: '#222', color: 'white', mb: 3 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <MoneyOffIcon sx={{ mr: 1 }} />
                      <Typography variant="body2">
                        No bank accounts linked
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      You need to link a bank account to withdraw funds
                    </Typography>
                  </CardContent>
                </Card>
              )}
              
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={handleAddBankAccount}
                startIcon={<AccountBalanceIcon />}
                fullWidth
              >
                {bankAccounts.length > 0 ? 'Link Another Bank Account' : 'Link Bank Account'}
              </Button>
              
              <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
              
              <Typography variant="body2" color="text.secondary">
                Bank withdrawals typically take 1-3 business days to process. 
                Funds will be debited from your TerraFlow wallet immediately.
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Withdrawal Amount
              </Typography>
              
              <TextField
                fullWidth
                label="Amount"
                variant="outlined"
                value={amount}
                onChange={handleAmountChange}
                placeholder="0.00"
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1 }}>{getCurrencySymbol(currency)}</Typography>
                }}
                sx={{ mb: 3 }}
              />
              
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleWithdraw}
                disabled={!amount || loading || !selectedAccount || bankAccounts.length === 0}
                sx={{ 
                  py: 1.5, 
                  background: 'linear-gradient(90deg, #4776E6 0%, #8E54E9 100%)',
                  '&:hover': {
                    background: 'linear-gradient(90deg, #4776E6 0%, #8E54E9 70%)',
                  }
                }}
              >
                {loading ? <CircularProgress size={24} /> : 'Withdraw to Bank Account'}
              </Button>
              
              {parseFloat(amount || 0) > walletBalance && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  The amount you're trying to withdraw exceeds your available balance.
                </Alert>
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default WithdrawFunds; 