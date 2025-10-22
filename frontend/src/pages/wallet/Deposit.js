import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Alert, 
  CircularProgress, 
  Container,
  MenuItem,
  Select,
  FormControl,
  Divider,
  InputAdornment,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemButton,
  ListItemAvatar,
  ListItemText,
  IconButton
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { transferAPI, authAPI, externalAccountsAPI } from '../../utils/api';
import useBridgeWallet from '../../hooks/useBridgeWallet';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import BoltIcon from '@mui/icons-material/Bolt';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import CloseIcon from '@mui/icons-material/Close';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { getCurrencySymbol } from '../../utils/currency';
import { calculateFee } from '../../utils/feeConstants';

// Supported currencies with their info
const SUPPORTED_CURRENCIES = [
  { code: 'USDC', name: 'USD Coin', flag: '💵', symbol: '$' },
  { code: 'USD', name: 'United States dollar', flag: '🇺🇸', symbol: '$' },
  { code: 'EUR', name: 'Euro', flag: '🇪🇺', symbol: '€' },
  { code: 'MXN', name: 'Mexican peso', flag: '🇲🇽', symbol: '$' },
  { code: 'BRL', name: 'Brazilian real', flag: '🇧🇷', symbol: 'R$' },
  { code: 'ARS', name: 'Argentine peso', flag: '🇦🇷', symbol: '$' },
  { code: 'COP', name: 'Colombian peso', flag: '🇨🇴', symbol: '$' },
  { code: 'PEN', name: 'Peruvian sol', flag: '🇵🇪', symbol: 'S/' }
];

export default function Deposit() {
  const navigate = useNavigate();
  const { wallet: bridgeWallet } = useBridgeWallet();
  
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [amount, setAmount] = useState('');
  const [linkedAccounts, setLinkedAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [paymentMethodDialogOpen, setPaymentMethodDialogOpen] = useState(false);
  const [exchangeRate, setExchangeRate] = useState(null);
  const [homeCurrency, setHomeCurrency] = useState('USD');

  // Fetch linked accounts and set default currency
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Set home currency from wallet
        if (bridgeWallet?.fiat_currency) {
          setHomeCurrency(bridgeWallet.fiat_currency.toUpperCase());
        }

        // Fetch linked payment methods
        const response = await externalAccountsAPI.getAccounts();
        const accounts = response.data.accounts || [];
        setLinkedAccounts(accounts);

        // Find preferred account or first active account
        const preferredAccount = accounts.find(acc => acc.is_preferred && acc.active);
        const defaultAccount = preferredAccount || accounts.find(acc => acc.active);
        
        if (defaultAccount) {
          setSelectedAccount(defaultAccount);
          // Set currency based on account
          if (defaultAccount.currency) {
            setSelectedCurrency(defaultAccount.currency.toUpperCase());
          }
        } else {
          // Default to USDC (no fees for crypto deposits)
          setSelectedCurrency('USDC');
        }
      } catch (err) {
        console.error('Error fetching accounts:', err);
      }
    };

    fetchData();
  }, [bridgeWallet]);

  const handleCurrencyChange = (event) => {
    const newCurrency = event.target.value;
    setSelectedCurrency(newCurrency);
    
    // Find a payment method that supports this currency
    const supportedAccount = linkedAccounts.find(
      acc => acc.active && acc.currency?.toUpperCase() === newCurrency
    );
    
    if (supportedAccount) {
      setSelectedAccount(supportedAccount);
    } else {
      setSelectedAccount(null);
    }
  };

  // Fetch exchange rate when amount or currency changes
  useEffect(() => {
    const fetchExchangeRate = async () => {
      if (!amount || parseFloat(amount) <= 0) {
        setExchangeRate(null);
        return;
      }

      // If same currency or USDC to USD, no conversion needed
      if (selectedCurrency === homeCurrency || (selectedCurrency === 'USDC' && homeCurrency === 'USD')) {
        setExchangeRate({ rate: 1, same_currency: true });
        return;
      }

      try {
        // Use a simple exchange rate API (you can replace this with your backend endpoint)
        const response = await fetch(`https://api.exchangerate-api.com/v4/latest/${selectedCurrency}`);
        const data = await response.json();
        const rate = data.rates[homeCurrency] || 1;
        setExchangeRate({ rate, same_currency: false });
      } catch (err) {
        console.error('Error fetching exchange rate:', err);
        setExchangeRate({ rate: 1, same_currency: true });
      }
    };

    fetchExchangeRate();
  }, [amount, selectedCurrency, homeCurrency]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedAccount) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const resp = await transferAPI.deposit({
        amount: amount,
        currency: selectedCurrency.toLowerCase(),
        external_account_id: selectedAccount.id,
        instant: true,
      });

      setSuccess('Deposit successful!');
      setAmount('');
      setTimeout(() => navigate('/wallet'), 2000);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err.message || 'Deposit failed');
    } finally {
      setLoading(false);
    }
  };

  // Calculate fees and amounts
  const depositAmount = amount ? parseFloat(amount) : 0;
  
  // Fee calculation: 0% for USDC, 1.5% for USD and EUR, use calculateFee for others
  const getFee = () => {
    if (!amount || depositAmount <= 0) return 0;
    if (selectedCurrency === 'USDC') return 0; // No fees for USDC
    if (selectedCurrency === 'USD' || selectedCurrency === 'EUR') {
      return depositAmount * 0.015; // 1.5% fee
    }
    return calculateFee(depositAmount); // Default fee calculation for other currencies
  };
  
  const fee = getFee();
  const totalWithFees = depositAmount + fee;
  const amountInHomeCurrency = exchangeRate && !exchangeRate.same_currency 
    ? depositAmount * exchangeRate.rate 
    : depositAmount;

  const currencyInfo = SUPPORTED_CURRENCIES.find(c => c.code === selectedCurrency);
  const supportedAccount = linkedAccounts.find(
    acc => acc.active && acc.currency?.toUpperCase() === selectedCurrency
  );

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#ffffff', py: 4 }}>
      <Container maxWidth="sm">
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/wallet')}
          sx={{ mb: 3, color: '#666' }}
        >
          Back
        </Button>

        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h4" fontWeight={600} sx={{ mb: 1, color: '#1a1a1a' }}>
              Add Money
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Deposit funds to your Liquicity account
            </Typography>
          </Box>
          
          {/* Exchange Rate Display */}
          {exchangeRate && !exchangeRate.same_currency && amount && parseFloat(amount) > 0 && (
            <Box sx={{ 
              p: 1.5, 
              bgcolor: '#f5f5f5', 
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 0.5
            }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                🔒
              </Typography>
              <Typography variant="body2" fontWeight={600} sx={{ fontSize: '0.9rem' }}>
                1 {selectedCurrency} = {exchangeRate.rate.toFixed(4)} {homeCurrency}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Currency Selector */}
        <Box sx={{ mb: 5 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontSize: '0.95rem', fontWeight: 400 }}>
            You add
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'nowrap' }}>
            <FormControl sx={{ flexShrink: 0 }}>
              <Select
                value={selectedCurrency}
                onChange={handleCurrencyChange}
                renderValue={(value) => {
                  const currency = SUPPORTED_CURRENCIES.find(c => c.code === value);
                  return (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                      <Typography sx={{ fontSize: '1.2rem' }}>{currency?.flag}</Typography>
                      <Typography fontWeight={600} fontSize="1rem">{currency?.code}</Typography>
                    </Box>
                  );
                }}
                MenuProps={{
                  PaperProps: {
                    sx: {
                      borderRadius: 2,
                      mt: 1,
                      maxHeight: 400,
                      '& .MuiList-root': {
                        py: 1
                      }
                    }
                  }
                }}
                sx={{
                  bgcolor: '#f5f5f5',
                  borderRadius: '24px',
                  fontSize: '1rem',
                  fontWeight: 600,
                  minWidth: '130px',
                  width: '130px',
                  '& .MuiOutlinedInput-notchedOutline': { border: 'none' },
                  '& .MuiSelect-select': { 
                    py: 1.2, 
                    px: 2,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.8
                  },
                  '&:hover': {
                    bgcolor: '#eeeeee'
                  }
                }}
              >
                {/* Preferred Method - USDC (No fees) */}
                <Box sx={{ px: 2, py: 1, pointerEvents: 'none' }}>
                  <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                    Preferred method • <Box component="span" sx={{ fontWeight: 700, color: '#1976d2' }}>No fees</Box>
                  </Typography>
                </Box>
                <MenuItem 
                  value="USDC"
                  sx={{
                    py: 1.5,
                    px: 2,
                    '&.Mui-selected': {
                      bgcolor: '#f5f5f5',
                      '&:hover': {
                        bgcolor: '#eeeeee'
                      }
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', pointerEvents: 'none' }}>
                    <Typography sx={{ fontSize: '1.5rem' }}>💵</Typography>
                    <Box sx={{ flex: 1 }}>
                      <Typography fontWeight={600} fontSize="1rem">
                        USDC
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        USD Coin
                      </Typography>
                    </Box>
                    {selectedCurrency === 'USDC' && (
                      <CheckCircleIcon sx={{ color: '#4caf50', fontSize: '1.2rem' }} />
                    )}
                  </Box>
                </MenuItem>

                <Divider sx={{ my: 1 }} />

                {/* Your Currencies - Linked bank accounts */}
                {linkedAccounts.filter(acc => acc.active).length > 0 && (
                  <Box sx={{ px: 2, py: 1, pointerEvents: 'none' }}>
                    <Typography variant="body2" fontWeight={600} color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                      Your currencies
                    </Typography>
                  </Box>
                )}
                {SUPPORTED_CURRENCIES
                  .filter(currency => {
                    if (currency.code === 'USDC') return false; // Exclude USDC from this section
                    return linkedAccounts.some(
                      acc => acc.active && acc.currency?.toUpperCase() === currency.code
                    );
                  })
                  .map(currency => (
                    <MenuItem 
                      key={currency.code} 
                      value={currency.code}
                      sx={{
                        py: 1.5,
                        px: 2,
                        '&.Mui-selected': {
                          bgcolor: '#f5f5f5',
                          '&:hover': {
                            bgcolor: '#eeeeee'
                          }
                        }
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', pointerEvents: 'none' }}>
                        <Typography sx={{ fontSize: '1.5rem' }}>{currency.flag}</Typography>
                        <Box sx={{ flex: 1 }}>
                          <Typography fontWeight={600} fontSize="1rem">
                            {currency.code}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {currency.name}
                          </Typography>
                        </Box>
                        {selectedCurrency === currency.code && (
                          <CheckCircleIcon sx={{ color: '#4caf50', fontSize: '1.2rem' }} />
                        )}
                      </Box>
                    </MenuItem>
                  ))}
                
                {linkedAccounts.filter(acc => acc.active).length > 0 && (
                  <Divider sx={{ my: 1 }} />
                )}

                {/* New Currency - Not linked yet */}
                <Box sx={{ px: 2, py: 1, pointerEvents: 'none' }}>
                  <Typography variant="body2" fontWeight={600} color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                    New currency
                  </Typography>
                </Box>
                {SUPPORTED_CURRENCIES
                  .filter(currency => {
                    if (currency.code === 'USDC') return false; // Exclude USDC
                    return !linkedAccounts.some(
                      acc => acc.active && acc.currency?.toUpperCase() === currency.code
                    );
                  })
                  .map(currency => (
                    <MenuItem 
                      key={currency.code} 
                      value={currency.code}
                      sx={{
                        py: 1.5,
                        px: 2,
                        '&.Mui-selected': {
                          bgcolor: '#f5f5f5',
                          '&:hover': {
                            bgcolor: '#eeeeee'
                          }
                        }
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', pointerEvents: 'none' }}>
                        <Typography sx={{ fontSize: '1.5rem' }}>{currency.flag}</Typography>
                        <Box sx={{ flex: 1 }}>
                          <Typography fontWeight={600} fontSize="1rem">
                            {currency.code}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {currency.name}
                          </Typography>
                        </Box>
                        {selectedCurrency === currency.code && (
                          <CheckCircleIcon sx={{ color: '#4caf50', fontSize: '1.2rem' }} />
                        )}
                      </Box>
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>

            <Box sx={{ flex: 1, minWidth: 0, ml: 1 }}>
              <TextField
                fullWidth
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                inputProps={{ step: '0.01', min: '0.01' }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    fontSize: '3rem',
                    fontWeight: 600,
                    fontFamily: '"SF Pro Display", "Inter", "-apple-system", "BlinkMacSystemFont", "Roboto", sans-serif',
                    bgcolor: '#ffffff',
                    borderRadius: 1,
                    '& fieldset': { border: 'none', borderBottom: '2px solid #e0e0e0' },
                    '&:hover fieldset': { borderBottom: '2px solid #bdbdbd' },
                    '&.Mui-focused fieldset': { borderBottom: '2px solid #1976d2' },
                    '& input': { 
                      textAlign: 'left', 
                      color: '#333',
                      py: 1,
                      px: 0,
                      letterSpacing: '-0.02em'
                    }
                  }
                }}
              />
            </Box>
          </Box>
        </Box>

        {/* Show payment method if currency is supported and amount is entered */}
        {amount && parseFloat(amount) > 0 && supportedAccount ? (
          <Box>
            {/* Paying with section */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Paying with
              </Typography>
              <Box 
                onClick={() => setPaymentMethodDialogOpen(true)}
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  mb: 2,
                  p: 2,
                  bgcolor: '#f8f9fa',
                  borderRadius: 2,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    bgcolor: '#e3f2fd',
                    transform: 'translateY(-1px)'
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ bgcolor: '#e3f2fd', width: 48, height: 48 }}>
                    <AccountBalanceIcon sx={{ color: '#1976d2' }} />
                  </Avatar>
                  <Box>
                    <Typography variant="body1" fontWeight={600} sx={{ color: '#1a1a1a' }}>
                      {supportedAccount.bank_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {supportedAccount.currency?.toUpperCase()} • ****{supportedAccount.last4}
                    </Typography>
                  </Box>
                </Box>
                <KeyboardArrowDownIcon sx={{ color: '#666' }} />
              </Box>
              <Divider />
            </Box>

            {/* Arrival time */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Avatar sx={{ bgcolor: '#f5f5f5', width: 40, height: 40 }}>
                  <BoltIcon sx={{ color: '#666' }} />
                </Avatar>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Arrives
                  </Typography>
                  <Typography variant="body1" fontWeight={600} sx={{ color: '#1a1a1a' }}>
                    Today - in seconds
                  </Typography>
                </Box>
              </Box>
              <Divider />
            </Box>

            {/* Fee breakdown */}
            {amount && parseFloat(amount) > 0 && (
              <Box sx={{ mb: 3, p: 3, bgcolor: '#f8f9fa', borderRadius: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <ReceiptIcon sx={{ color: '#666', fontSize: '1.2rem' }} />
                  <Typography variant="body2" fontWeight={600} color="text.secondary">
                    Payment breakdown
                  </Typography>
                </Box>

                {/* Subtotal */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2" color="text.secondary">
                    Subtotal
                  </Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {currencyInfo?.symbol}{depositAmount.toFixed(2)} {selectedCurrency}
                  </Typography>
                </Box>

                {/* Fees */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2" color="text.secondary">
                    Fees
                  </Typography>
                  <Typography variant="body2" fontWeight={500} sx={{ color: fee === 0 ? '#4caf50' : 'inherit' }}>
                    {fee === 0 ? 'No fees' : `${currencyInfo?.symbol}${fee.toFixed(2)}`}
                  </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Amount in deposit currency */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2" fontWeight={600}>
                    You pay
                  </Typography>
                  <Typography variant="body1" fontWeight={600}>
                    {currencyInfo?.symbol}{totalWithFees.toFixed(2)} {selectedCurrency}
                  </Typography>
                </Box>

                {/* Amount in home currency (if different) */}
                {exchangeRate && !exchangeRate.same_currency && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 1.5, borderTop: '1px dashed #e0e0e0' }}>
                    <Typography variant="body2" fontWeight={600} color="text.secondary">
                      You receive
                    </Typography>
                    <Typography variant="body1" fontWeight={600} sx={{ color: '#1976d2' }}>
                      {getCurrencySymbol(homeCurrency)}{amountInHomeCurrency.toFixed(2)} {homeCurrency}
                    </Typography>
                  </Box>
                )}
              </Box>
            )}

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {success && (
              <Alert severity="success" sx={{ mb: 3 }}>
                {success}
              </Alert>
            )}

            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleSubmit}
              disabled={loading || !amount || parseFloat(amount) <= 0}
              sx={{
                py: 2,
                bgcolor: '#1976d2',
                color: '#ffffff',
                textTransform: 'none',
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: 2,
                '&:hover': {
                  bgcolor: '#1565c0'
                },
                '&:disabled': {
                  bgcolor: '#e0e0e0',
                  color: '#9e9e9e'
                }
              }}
            >
              {loading ? <CircularProgress size={24} sx={{ color: '#fff' }} /> : 'Continue'}
            </Button>
          </Box>
        ) : amount && parseFloat(amount) > 0 ? (
          /* No payment method for selected currency */
          <Box sx={{ 
            p: 4, 
            textAlign: 'center',
            border: '1px dashed #e0e0e0',
            borderRadius: 2
          }}>
            <AccountBalanceIcon sx={{ fontSize: 48, color: '#bbb', mb: 2 }} />
            <Typography variant="body1" fontWeight={500} sx={{ mb: 1, color: '#1a1a1a' }}>
              No payment method for {selectedCurrency}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {selectedCurrency === 'USDC' 
                ? 'Link a crypto wallet that supports USDC to continue'
                : `Link a bank account that supports ${selectedCurrency} to continue`
              }
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate(selectedCurrency === 'USDC' ? '/wallet/link-wallet' : '/wallet/link-bank')}
              sx={{
                bgcolor: '#1976d2',
                color: '#ffffff',
                textTransform: 'none',
                '&:hover': {
                  bgcolor: '#1565c0'
                }
              }}
            >
              Link Payment Method
            </Button>
          </Box>
        ) : null}

        {/* Payment Method Selection Dialog */}
        <Dialog
          open={paymentMethodDialogOpen}
          onClose={() => setPaymentMethodDialogOpen(false)}
          maxWidth="sm"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: 3,
              maxHeight: '80vh'
            }
          }}
        >
          <DialogTitle sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            pb: 2
          }}>
            <Typography variant="h6" fontWeight={600}>
              Choose how to pay
            </Typography>
            <IconButton 
              onClick={() => setPaymentMethodDialogOpen(false)}
              size="small"
            >
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent sx={{ px: 0 }}>
            <List>
              {linkedAccounts
                .filter(acc => acc.active && acc.currency?.toUpperCase() === selectedCurrency)
                .map((account) => (
                  <ListItem key={account.id} disablePadding>
                    <ListItemButton
                      onClick={() => {
                        setSelectedAccount(account);
                        setPaymentMethodDialogOpen(false);
                      }}
                      selected={selectedAccount?.id === account.id}
                      sx={{
                        py: 2,
                        px: 3,
                        '&.Mui-selected': {
                          bgcolor: '#f0f7ff',
                          '&:hover': {
                            bgcolor: '#e3f2fd'
                          }
                        }
                      }}
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: '#e3f2fd', width: 48, height: 48 }}>
                          <AccountBalanceIcon sx={{ color: '#1976d2' }} />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body1" fontWeight={600}>
                            {account.bank_name}
                          </Typography>
                        }
                        secondary={
                          <Typography variant="body2" color="text.secondary">
                            {account.currency?.toUpperCase()} Checking • ****{account.last4}
                          </Typography>
                        }
                      />
                      {selectedAccount?.id === account.id && (
                        <CheckCircleIcon sx={{ color: '#4caf50', ml: 2 }} />
                      )}
                    </ListItemButton>
                  </ListItem>
                ))}
              
              {linkedAccounts.filter(acc => acc.active && acc.currency?.toUpperCase() === selectedCurrency).length === 0 && (
                <Box sx={{ p: 4, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No payment methods available for {selectedCurrency}
                  </Typography>
                </Box>
              )}
            </List>
          </DialogContent>
        </Dialog>
      </Container>
    </Box>
  );
}
