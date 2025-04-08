import React, { useState, useEffect } from 'react';
import { 
  Container, Box, Paper, Typography, Tab, Tabs, Button, 
  Grid, Card, CardContent, Divider, IconButton, Chip,
  List, ListItem, ListItemText, ListItemIcon, CircularProgress,
  Alert, Tooltip, Menu, MenuItem, alpha, FormControl, InputLabel,
  Select, Snackbar, TextField
} from '@mui/material';
import { 
  AccountBalanceWallet, Send, QrCode, SwapHoriz, 
  CurrencyExchange, ContentCopy, MoreVert, Visibility, 
  VisibilityOff, ArrowUpward, ArrowDownward, LinkOff, Link,
  AddCircleOutline, CurrencyBitcoin, AttachMoney
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { StaggerContainer, StaggerItem } from '../components/animations/AnimatedComponents';
import { useTheme } from '@mui/material/styles';

const Wallet = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const [walletData, setWalletData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currency, setCurrency] = useState('USD');
  const [success, setSuccess] = useState(null);
  
  // Crypto conversion states
  const [convertAmount, setConvertAmount] = useState('');
  const [selectedCrypto, setSelectedCrypto] = useState('USDT');
  const [convertDirection, setConvertDirection] = useState('toCrypto'); // 'toCrypto' or 'fromCrypto'
  const [convertLoading, setConvertLoading] = useState(false);
  
  // Available cryptocurrencies
  const cryptoCurrencies = [
    { symbol: 'USDT', name: 'Tether', stable: true },
    { symbol: 'USDC', name: 'USD Coin', stable: true },
    { symbol: 'BTC', name: 'Bitcoin', stable: false },
    { symbol: 'ETH', name: 'Ethereum', stable: false }
  ];

  useEffect(() => {
    if (currentUser && currentUser.id) {
      fetchWalletData();
      fetchRecentTransactions();
    }
  }, [currentUser]);

  const fetchWalletData = async () => {
    try {
      const response = await api.get(`/wallet/${currentUser.id}`);
      if (response.status === 200) {
        setWalletData(response.data);
        setCurrency(response.data.base_currency || 'USD');
      }
    } catch (err) {
      console.error('Error fetching wallet data:', err);
      setError('Unable to load your wallet. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentTransactions = async () => {
    try {
      const response = await api.get(`/transaction/user/${currentUser.id}?limit=5`);
      if (response.status === 200) {
        setTransactions(response.data);
      }
    } catch (err) {
      console.error('Error fetching transactions:', err);
      // Don't set error here to avoid overriding wallet error
    }
  };

  const formatCurrency = (amount, currency = 'USD') => {
    if (amount === undefined || amount === null) return '—';
    
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    
    return formatter.format(amount);
  };
  
  const formatCrypto = (amount, symbol = 'USDT') => {
    return `${parseFloat(amount).toFixed(6)} ${symbol}`;
  };
  
  const handleCryptoConversion = async () => {
    if (!convertAmount || isNaN(convertAmount) || parseFloat(convertAmount) <= 0) {
      setError('Please enter a valid amount to convert');
      return;
    }
    
    setConvertLoading(true);
    
    try {
      // In a real app, this would call your backend API to perform the conversion
      // For this demo, we'll simulate a successful conversion
      
      setTimeout(() => {
        setConvertLoading(false);
        
        const message = convertDirection === 'toCrypto' 
          ? `Converted ${formatCurrency(convertAmount, currency)} to ${formatCrypto(convertAmount, selectedCrypto)}` 
          : `Converted ${formatCrypto(convertAmount, selectedCrypto)} to ${formatCurrency(convertAmount, currency)}`;
        
        setSuccess(message);
        setConvertAmount('');
      }, 1500);
      
    } catch (err) {
      console.error('Error during conversion:', err);
      setError('Conversion failed. Please try again.');
      setConvertLoading(false);
    }
  };

  const getTransactionTypeLabel = (type) => {
    switch(type) {
      case 'SEND': return 'Money Sent';
      case 'RECEIVE': return 'Money Received';
      case 'DEPOSIT': return 'Deposit';
      case 'WITHDRAW': return 'Withdrawal';
      case 'EXCHANGE': return 'Currency Exchange';
      default: return 'Transaction';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ px: { xs: 2, md: 3 } }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
          {error}
        </Alert>
      )}
      
      <Snackbar
        open={Boolean(success)}
        autoHideDuration={3000}
        onClose={() => setSuccess(null)}
        message={success}
      />

      <Typography variant="h4" component="h1" fontWeight="700" gutterBottom>
        My Wallet
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
        Manage your funds and send money across borders
      </Typography>

      {/* Main Balance Card - reduced spacing */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Box sx={{ 
            p: { xs: 2, md: 3 },
            background: (theme) => theme.palette.background.paper,
            borderRadius: 2,
            border: (theme) => `1px solid ${theme.palette.divider}`,
            boxShadow: 'none',
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
              <Box>
                <Typography variant="h6" fontWeight="600" sx={{ color: 'text.primary' }}>
                  {currency} Balance
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Your main currency
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="h3" sx={{ fontWeight: 'bold', my: 1, color: 'text.primary' }}>
                {formatCurrency(walletData?.main_balance || 0, currency)}
              </Typography>
            </Box>
            
            <Box sx={{ 
              height: '1px', 
              width: '100%', 
              background: (theme) => theme.palette.divider,
              my: 2
            }} />

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button 
                  variant="contained" 
                  fullWidth
                  onClick={() => navigate('/deposit')}
                  sx={{ 
                    py: 1.5, 
                    color: (theme) => theme.palette.getContrastText(theme.palette.primary.main),
                    fontWeight: 'bold',
                    background: (theme) => theme.palette.primary.main,
                    borderRadius: 0,
                    '&:hover': {
                      background: (theme) => theme.palette.primary.dark,
                    }
                  }}
                >
                  <Typography fontSize="1.2rem" sx={{ mr: 1, color: 'inherit' }}>+</Typography>
                  Deposit
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button 
                  variant="outlined" 
                  fullWidth
                  onClick={() => navigate('/withdraw')}
                  sx={{ 
                    py: 1.5,
                    fontWeight: 'bold',
                    color: 'primary.main',
                    borderRadius: 0,
                    borderColor: 'primary.main',
                    borderWidth: 1,
                    '&:hover': {
                      borderColor: 'primary.dark',
                      borderWidth: 1,
                      background: (theme) => alpha(theme.palette.primary.main, 0.05),
                    }
                  }}
                >
                  <Typography fontSize="1.2rem" sx={{ mr: 1, color: 'inherit' }}>-</Typography>
                  Withdraw
                </Button>
              </Grid>
            </Grid>
          </Box>
        </Grid>

        {/* Transfer Information */}
        <Grid item xs={12} md={6}>
          <Box sx={{ 
            p: { xs: 2, md: 3 },
            background: (theme) => theme.palette.background.paper,
            borderRadius: 2,
            border: (theme) => `1px solid ${theme.palette.divider}`,
            boxShadow: 'none',
            height: '100%',
          }}>
            <Typography variant="h6" fontWeight="600" sx={{ color: 'text.primary', mb: 2 }}>
              Cross-Currency Transfers
            </Typography>
            
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
              Send money to recipients using any currency. TerraFlow automatically converts your {currency} to the recipient's currency using stablecoins as an intermediary.
            </Typography>

            <Box sx={{ 
              p: 2, 
              borderRadius: 0,
              border: (theme) => `1px solid ${theme.palette.divider}`,
              background: (theme) => alpha(theme.palette.primary.main, 0.03),
              mb: 2
            }}>
              <Typography variant="subtitle2" sx={{ color: 'text.primary', fontWeight: 600, mb: 1 }}>
                How it works:
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Box sx={{ 
                  width: 28, 
                  height: 28, 
                  borderRadius: '50%', 
                  bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mr: 1
                }}>
                  <Typography variant="caption" sx={{ color: 'text.primary', fontWeight: 600 }}>1</Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Your {currency} → USDT stablecoin
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Box sx={{ 
                  width: 28, 
                  height: 28, 
                  borderRadius: '50%', 
                  bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mr: 1
                }}>
                  <Typography variant="caption" sx={{ color: 'text.primary', fontWeight: 600 }}>2</Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  USDT transferred securely
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ 
                  width: 28, 
                  height: 28, 
                  borderRadius: '50%', 
                  bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mr: 1
                }}>
                  <Typography variant="caption" sx={{ color: 'text.primary', fontWeight: 600 }}>3</Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  USDT → Recipient's local currency
                </Typography>
              </Box>
            </Box>

            <Button 
              variant="outlined"
              onClick={() => navigate('/send')}
              fullWidth
              sx={{ 
                py: 1.5,
                fontWeight: 'bold',
                color: 'primary.main',
                borderRadius: 0,
                borderColor: 'primary.main',
                borderWidth: 1,
                '&:hover': {
                  borderColor: 'primary.dark',
                  borderWidth: 1,
                  background: (theme) => alpha(theme.palette.primary.main, 0.05),
                }
              }}
            >
              Make International Transfer
            </Button>
          </Box>
        </Grid>
      </Grid>
      
      {/* Crypto Conversion Section */}
      <Box sx={{ 
        p: { xs: 2, md: 3 },
        borderRadius: 2,
        background: (theme) => theme.palette.background.paper,
        boxShadow: 'none',
        border: (theme) => `1px solid ${theme.palette.divider}`,
        mb: 3
      }}>
        <Typography variant="h5" fontWeight="600" sx={{ color: 'text.primary', mb: 2, display: 'flex', alignItems: 'center' }}>
          <CurrencyBitcoin sx={{ mr: 1 }} />
          Currency Protection
        </Typography>
        
        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3 }}>
          Convert your funds between your main currency and cryptocurrency for additional protection against currency instability.
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Direction</InputLabel>
              <Select
                value={convertDirection}
                label="Direction"
                onChange={(e) => setConvertDirection(e.target.value)}
              >
                <MenuItem value="toCrypto">
                  {currency} to Cryptocurrency
                </MenuItem>
                <MenuItem value="fromCrypto">
                  Cryptocurrency to {currency}
                </MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              label="Amount"
              value={convertAmount}
              onChange={(e) => setConvertAmount(e.target.value)}
              type="number"
              InputProps={{ 
                inputProps: { min: 0, step: '0.01' },
                startAdornment: convertDirection === 'toCrypto' 
                  ? <Box sx={{ mr: 1, color: 'text.secondary' }}>{currency === 'USD' ? '$' : ''}</Box> 
                  : null
              }}
              sx={{ mb: 2 }}
            />
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Cryptocurrency</InputLabel>
              <Select
                value={selectedCrypto}
                label="Cryptocurrency"
                onChange={(e) => setSelectedCrypto(e.target.value)}
              >
                {cryptoCurrencies.map(crypto => (
                  <MenuItem key={crypto.symbol} value={crypto.symbol}>
                    {crypto.name} ({crypto.symbol})
                    {crypto.stable && 
                      <Chip 
                        label="Stable" 
                        size="small" 
                        color="success" 
                        sx={{ ml: 1, height: 20 }} 
                      />
                    }
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Button
              variant="contained"
              fullWidth
              startIcon={<SwapHoriz />}
              disabled={convertLoading}
              onClick={handleCryptoConversion}
              sx={{ 
                py: 1.5,
                color: '#FFFFFF',
                fontSize: '1.1rem'
              }}
            >
              {convertLoading ? <CircularProgress size={24} /> : 'Convert Currency'}
            </Button>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, borderRadius: 2, height: '100%', border: '1px dashed rgba(255, 255, 255, 0.2)' }}>
              <Typography variant="h6" gutterBottom>
                Why Use Cryptocurrency?
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main', mb: 0.5 }}>
                  Protection Against Inflation
                </Typography>
                <Typography variant="body2">
                  Shield your assets from local currency depreciation with stablecoins pegged to USD.
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main', mb: 0.5 }}>
                  Global Access
                </Typography>
                <Typography variant="body2">
                  Access your funds anywhere in the world without restrictions or bank holidays.
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main', mb: 0.5 }}>
                  Secure Storage
                </Typography>
                <Typography variant="body2">
                  Your assets are secured by blockchain technology with the highest security standards.
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>

      {/* Recent Transactions - reduced spacing */}
      <Box sx={{ 
        p: { xs: 2, md: 3 },
        borderRadius: 2,
        background: (theme) => theme.palette.background.paper,
        boxShadow: 'none',
        border: (theme) => `1px solid ${theme.palette.divider}`,
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" fontWeight="600" sx={{ color: 'text.primary' }}>
            Recent Transactions
          </Typography>
          <Button 
            variant="text" 
            onClick={() => navigate('/transactions')}
            sx={{ 
              color: 'primary.main',
              fontWeight: 'bold',
              '&:hover': { background: (theme) => alpha(theme.palette.primary.main, 0.05) }
            }}
          >
            View All
          </Button>
        </Box>
        
        {transactions.length > 0 ? (
          <List sx={{ p: 0 }}>
            {transactions.map((transaction, index) => {
              // Determine transaction type and direction for display
              const isIncoming = transaction.recipient_id === currentUser?.id;
              const transactionType = transaction.transaction_type || 
                (isIncoming ? 'RECEIVE' : 'SEND');
              
              return (
                <ListItem
                  key={transaction.id || index}
                  sx={{
                    borderBottom: (theme) => index < transactions.length - 1 ? `1px solid ${theme.palette.divider}` : 'none',
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.03),
                    },
                    borderRadius: 0,
                    my: 0,
                    py: 1.5
                  }}
                  secondaryAction={
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="subtitle2" fontWeight="600" 
                        sx={{ color: (theme) => isIncoming ? theme.palette.success.main : theme.palette.error.main }}
                      >
                        {isIncoming ? '+' : '-'}
                        {formatCurrency(
                          isIncoming ? transaction.target_amount : transaction.source_amount, 
                          isIncoming ? transaction.target_currency : transaction.source_currency || currency
                        )}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {transaction.status || 'completed'}
                      </Typography>
                    </Box>
                  }
                >
                  <ListItemIcon>
                    <Box sx={{ 
                      width: 36,
                      height: 36,
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      borderRadius: 0,
                      bgcolor: (theme) => alpha(theme.palette.primary.main, 0.05),
                      border: (theme) => `1px solid ${theme.palette.divider}`
                    }}>
                      <Typography fontSize="1.2rem" sx={{ 
                        color: (theme) => isIncoming ? theme.palette.success.main : theme.palette.error.main
                      }}>
                        {isIncoming ? '←' : '→'}
                      </Typography>
                    </Box>
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body1" sx={{ fontWeight: 500, color: 'text.primary' }}>
                        {transaction.description || getTransactionTypeLabel(transactionType)}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {new Date(transaction.timestamp).toLocaleDateString('en-US', {
                          day: 'numeric',
                          month: 'short',
                          hour: 'numeric',
                          minute: '2-digit'
                        })}
                      </Typography>
                    }
                  />
                </ListItem>
              );
            })}
          </List>
        ) : (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <Typography variant="body1" sx={{ color: 'text.secondary' }}>
              No recent transactions
            </Typography>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default Wallet; 