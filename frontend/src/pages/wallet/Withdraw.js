import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Alert, 
  CircularProgress, 
  Container,
  Grid,
  ListItem,
  ListItemIcon,
  ListItemText, 
  List,
  Radio,
  RadioGroup,
  FormControlLabel,
  useTheme,
  useMediaQuery,
  IconButton,
  Divider,
  Paper
} from '@mui/material';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { transferAPI, bridgeAPI, authAPI, externalAccountsAPI } from '../../utils/api';
import useBridgeWallet from '../../hooks/useBridgeWallet';
import { useNavigate } from 'react-router-dom';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import RefreshIcon from '@mui/icons-material/Refresh';
import VerifiedIcon from '@mui/icons-material/Verified';
import PaymentsIcon from '@mui/icons-material/Payments';
import BoltIcon from '@mui/icons-material/Bolt';
import AddIcon from '@mui/icons-material/Add';

import {
  FloatingCard,
  GlassContainer,
  GradientText,
  GradientDivider,
  AnimatedBackground,
  NeonButton
} from '../../components/ui/ModernUIComponents';

import {
  SlideRightBox,
  StaggerContainer,
  StaggerItem
} from '../../components/animations/AnimatedComponents';

import LinkPaymentDialog from '../../components/LinkPaymentDialog';

// Replace the region detection with a function that gets the user's region directly from profile
const getUserRegion = (userData) => {
  // Get the user's country from their profile
  const country = userData?.country || 'US';
  
  // Map country to region and currency
  if (country === 'MX') return { region: 'mx', currency: 'mxn' };
  if (country === 'US') return { region: 'us', currency: 'usd' };
  
  // Check if country is in EU
  const EU_COUNTRIES = [
    'AT','BE','BG','CH','CY','CZ','DE','DK','EE','ES','FI','FR','GB',
    'GR','HR','HU','IE','IS','IT','LI','LT','LU','LV','MT','NL','NO',
    'PL','PT','RO','SE','SI','SK'
  ];
  
  if (EU_COUNTRIES.includes(country)) return { region: 'eu', currency: 'eur' };
  
  // Default to US if unknown
  return { region: 'us', currency: 'usd' };
};

// Add a helper function to get the correct currency symbol
const getCurrencySymbol = (currencyCode) => {
  const code = currencyCode?.toUpperCase() || 'USD';
  switch(code) {
    case 'EUR': return '€';
    case 'GBP': return '£';
    case 'MXN': return '₱';
    case 'CAD': return 'C$';
    default: return '$';
  }
};

export default function Withdraw() {
  const [step, setStep] = useState('select-bank'); // select-bank, withdraw-form
  const [form, setForm] = useState({ 
    amount: '', 
    external_account_id: '',
    withdrawalType: 'standard' // standard or card
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [linkedAccounts, setLinkedAccounts] = useState([]);
  const [userRegion, setUserRegion] = useState({ region: 'us', currency: 'usd' });
  const [newAccountForm, setNewAccountForm] = useState({ 
    bank_name: '',
    account_owner_name: '',
    account_number: '', 
    routing_number: '', 
    iban: '',
    account_type: 'checking',
    account_name: '',
    address: {
      street_line_1: '',
      street_line_2: '',
      city: '',
      state: '',
      postal_code: '',
      country: ''
    }
  });
  
  const { wallet: bridgeWallet, loading: walletLoading } = useBridgeWallet();
  const [balanceData, setBalanceData] = useState({ total: 0, available: 0, currency: 'USD' });
  const [linkDialogOpen, setLinkDialogOpen] = useState(false);
  
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const fetchLinkedAccounts = async () => {
    setLoading(true);
    try {
      // First sync accounts with Bridge to get latest status and balance
      await externalAccountsAPI.syncAccounts();
      
      // Then fetch the updated accounts
      const response = await externalAccountsAPI.getAccounts();
      setLinkedAccounts(response.data.accounts || []);
    } catch (err) {
      console.error('Error fetching linked accounts:', err);
      setError('Failed to load your linked payment methods');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch linked accounts when component mounts
    fetchLinkedAccounts();
    
    // Fetch user profile and wallet data (no auto Plaid launch)
    const fetchUserProfile = async () => {
      try {
        const userResp = await authAPI.getCurrentUser();
        if (userResp.data) {
          // Set region based on user's country from profile
          const region = getUserRegion(userResp.data);
          setUserRegion(region);

          // Preload Plaid script for US users (without auto-opening)
          if (region.region === 'us' && !window.Plaid) {
            const script = document.createElement('script');
            script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
            script.async = true;
            document.body.appendChild(script);
          }

          // Set address country in new account form
          setNewAccountForm(prev => ({
            ...prev,
            address: {
              ...prev.address,
              country: userResp.data.country || 'US'
            }
          }));
        }
      } catch (err) {
        console.error('Failed to fetch user profile', err);
      }
    };
    
    fetchUserProfile();
  }, []);

  // Update balance when wallet changes
  useEffect(() => {
    if (bridgeWallet) {
      const total = bridgeWallet.balances?.reduce((s,b)=>s+parseFloat(b.balance||0),0) || 0;
      setBalanceData({ total, available: total, currency: 'USD' });
    }
  }, [bridgeWallet]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleNewAccountChange = (e) => {
    const { name, value } = e.target;
    // Check if this is an address field
    if (name.includes('street_line') || name === 'city' || name === 'state' || name === 'postal_code') {
      setNewAccountForm(prev => ({
        ...prev,
        address: {
          ...prev.address,
          [name]: value
        }
      }));
    } else {
      setNewAccountForm(prev => ({ 
        ...prev, 
        [name]: value 
      }));
    }
  };

  const handleSelectAccount = (accountId) => {
    setForm((prev) => ({ 
      ...prev, 
      external_account_id: accountId 
    }));
    setStep('withdraw-form');
  };

  const handleLinkNewAccount = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Create payload for API call
      const payload = {
        bank_name: newAccountForm.bank_name,
        account_owner_name: newAccountForm.account_owner_name,
        account_name: newAccountForm.account_name,
        account_type: newAccountForm.account_type,
        currency: userRegion.currency,
        address: newAccountForm.address
      };
      
      // Add account number and routing number for US accounts
      if (userRegion.region === 'us') {
        payload.account_number = newAccountForm.account_number;
        payload.routing_number = newAccountForm.routing_number;
      } else {
        // Add IBAN for EU accounts
        payload.iban = newAccountForm.iban;
      }
      
      const response = await externalAccountsAPI.createAccount(payload);
      
      // Refresh the accounts list
      fetchLinkedAccounts();
      
      // Move to withdraw form with the new account selected
      setForm(prev => ({ ...prev, external_account_id: response.data.id }));
      setStep('withdraw-form');
    } catch (err) {
      console.error('Error linking bank account:', err);
      setError('Failed to link your bank account. Please check your information and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    if (form.withdrawalType === 'virtual_account') {
      // Navigate to virtual account page if selected
      navigate('/virtual-account');
      return;
    }
    
    try {
      const resp = await transferAPI.withdraw({
        amount: form.amount,
        currency: userRegion.currency.toLowerCase(),
        external_account_id: form.external_account_id
      });
      
      setSuccess(resp.data);
      // Reset form but keep the selected account
      setForm(prev => ({ 
        amount: '', 
        external_account_id: prev.external_account_id,
        withdrawalType: 'standard'
      }));
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err.message || 'Withdrawal failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (step === 'withdraw-form') {
      setStep('select-bank');
    } else if (step === 'link-bank') {
      setStep('select-bank');
    }
  };

  // Animation variants
  const pageVariants = {
    initial: { opacity: 0 },
    animate: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { type: "spring", damping: 15 }
    }
  };

  // Get rail name based on user's region
  const getRailName = () => {
    switch (userRegion.region) {
      case 'us': return 'ACH';
      case 'eu': return 'SEPA';
      case 'mx': return 'SPEI';
      default: return 'Bank Transfer';
    }
  };

  // Set up the "Add Account" click handler to automatically direct users based on region
  const handleAddAccount = () => {
    // Redirect to the shared Link Bank Account page implemented in Deposit route
    navigate('/wallet/link-bank');
  };
  
  // Function to initialize Plaid Link
  const initializePlaidLink = async () => {
    try {
      // First check if Plaid script is loaded
      if (!window.Plaid) {
        throw new Error('Plaid script not loaded. Please refresh the page and try again.');
      }
      
      setLoading(true);
      const response = await externalAccountsAPI.getPlaidLinkToken();
      
      if (response && response.data && response.data.link_token) {
        // Open Plaid Link automatically once we have the token
        openPlaidLink(response.data.link_token);
      } else {
        throw new Error('Failed to get Plaid link token');
      }
    } catch (err) {
      console.error('Error initializing Plaid Link:', err);
      setError('Failed to initialize Plaid Link. Please try manual entry instead.');
      // Fall back to manual entry if Plaid fails
      setStep('link-bank');
    } finally {
      setLoading(false);
    }
  };
  
  // Function to open Plaid Link
  const openPlaidLink = (token) => {
    if (!token) return;
    
    const linkTokenUsed = token;
    const handler = window.Plaid.create({
      token,
      onSuccess: async (publicToken, metadata) => {
        try {
          setLoading(true);
          await externalAccountsAPI.exchangePlaidToken(linkTokenUsed, publicToken);
          
          // Fetch updated list of accounts after linking
          fetchLinkedAccounts();
          // Move to withdrawal form
          setStep('withdraw-form');
        } catch (err) {
          console.error('Error exchanging Plaid token:', err);
          setError('Failed to link your bank account. Please try again.');
        } finally {
          setLoading(false);
        }
      },
      onExit: (err) => {
        if (err) {
          console.error('Plaid Link exit with error:', err);
          setError('There was an issue connecting to your bank. Please try manual entry.');
          setStep('link-bank');
        } else {
          // User closed Plaid Link without completing
          setStep('select-bank');
        }
      },
      onEvent: (eventName, metadata) => {
        console.log('Plaid Link Event:', eventName, metadata);
      }
    });
    
    handler.open();
  };

  return (
    <Box 
      component={motion.div}
      initial="initial"
      animate="animate"
      variants={pageVariants}
      sx={{ 
        width: '100%', 
        minHeight: 'calc(100vh - 64px)',
        background: '#000000',
        pb: 8,
        position: 'relative'
      }}
    >
      <AnimatedBackground />
      
      <Container maxWidth="lg" sx={{ pt: 3 }}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} md={6}>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              mb: 2
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {step !== 'select-bank' && (
                  <Button 
                    startIcon={<ArrowBackIcon />} 
                    onClick={handleBack}
                    sx={{ mr: 2, color: 'text.secondary' }}
                  >
                    Back
                  </Button>
                )}
              </Box>
              <Typography variant="body2" color="text.secondary">
                Balance: <Typography component="span" fontWeight="600" color="#fff">{getCurrencySymbol(balanceData.currency)}{balanceData.available.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</Typography>
              </Typography>
            </Box>
            
            <Paper
              elevation={0}
              sx={{
                borderRadius: 3,
                bgcolor: 'rgba(17, 25, 40, 0.75)',
                backdropFilter: 'blur(16px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                p: 3,
                mb: 4
              }}
            >
              <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" fontWeight="600" color="#fff">
                  Withdraw Funds
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  Transfer money from your Liquicity account to your bank
                </Typography>
              </Box>
              
              {/* The method selection step was removed – we go straight to bank selection */}
              
              {/* Select Payment Method */}
              {step === 'select-bank' && (
                <>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                    Select Payment Method
                  </Typography>
                  
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : linkedAccounts.length > 0 ? (
                    <List sx={{ p: 0 }}>
                      {linkedAccounts.map((account) => (
                        <ListItem 
                          key={account.id}
                          sx={{ 
                            p: 2, 
                            mb: 2, 
                            borderRadius: 2,
                            background: 'rgba(17, 24, 39, 0.5)',
                            border: '1px solid rgba(55, 65, 81, 0.5)',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            '&:hover': {
                              background: 'rgba(59, 130, 246, 0.1)',
                              borderColor: 'rgba(59, 130, 246, 0.3)',
                            }
                          }}
                          onClick={() => handleSelectAccount(account.id)}
                        >
                          <ListItemIcon sx={{ minWidth: 40 }}>
                            <Box sx={{ 
                              borderRadius: '50%', 
                              width: 40, 
                              height: 40, 
                              display: 'flex', 
                              alignItems: 'center', 
                              justifyContent: 'center',
                              backgroundColor: 'rgba(59, 130, 246, 0.1)'
                            }}>
                              <AccountBalanceIcon color="primary" />
                            </Box>
                          </ListItemIcon>
                          <ListItemText 
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Typography variant="subtitle1" fontWeight={500}>
                                  {account.name}
                                </Typography>
                                {account.status === 'verified' && (
                                  <Box sx={{ 
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    ml: 1,
                                    color: 'success.main',
                                    fontSize: '0.75rem'
                                  }}>
                                    <VerifiedIcon fontSize="inherit" sx={{ mr: 0.5 }} />
                                    <Typography variant="caption" color="success.main">Verified</Typography>
                                  </Box>
                                )}
                              </Box>
                            }
                            secondary={`Account ${account.accountNumber}`}
                          />
                        </ListItem>
                      ))}
                      
                        <Button
                          variant="outlined"
                          fullWidth
                          startIcon={<AddIcon />}
                          onClick={() => setLinkDialogOpen(true)}
                          sx={{ 
                            py: 1.5, 
                            mt: 2,
                            borderColor: 'rgba(255, 255, 255, 0.2)',
                            color: 'white',
                            '&:hover': {
                              borderColor: 'primary.main',
                              bgcolor: 'rgba(59, 130, 246, 0.05)'
                            }
                          }}
                        >
                        Link Payment Method
                        </Button>
                    </List>
                  ) : (
                    <Box sx={{ py: 3, textAlign: 'center' }}>
                      <Typography color="text.secondary" sx={{ mb: 3 }}>
                        You don't have any linked payment methods
                      </Typography>
                      <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={() => setStep('link-bank')}
                        sx={{ 
                          py: 1.5,
                          backgroundColor: 'primary.main',
                          '&:hover': {
                            backgroundColor: 'primary.dark',
                            boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                          }
                        }}
                      >
                        Link Payment Method
                      </Button>
                    </Box>
                  )}
                </>
              )}
              
              {/* Step 3: Withdraw Form */}
              {step === 'withdraw-form' && (
                <>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                    Withdraw Funds
                  </Typography>
                  
                  <form onSubmit={handleSubmit}>
                    <Grid container spacing={3}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Amount"
                          name="amount"
                          type="number"
                          inputProps={{ step: '0.01', min: '0.01' }}
                          value={form.amount}
                          onChange={handleChange}
                          required
                          variant="outlined"
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '12px',
                            }
                          }}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Box sx={{ p: 3, border: '1px solid rgba(55, 65, 81, 0.5)', borderRadius: 2 }}>
                          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                            Select Payment Method
                          </Typography>
                          
                          <RadioGroup
                            name="bank_account"
                            value={form.external_account_id}
                            onChange={handleChange}
                          >
                            {linkedAccounts.map((account) => (
                              <Box 
                                key={account.id}
                                sx={{ 
                                  mb: 2, 
                                  p: 2, 
                                  borderRadius: 2, 
                                  border: form.external_account_id === account.id ? '1px solid rgba(59, 130, 246, 0.5)' : '1px solid rgba(55, 65, 81, 0.3)', 
                                  background: form.external_account_id === account.id ? 'rgba(59, 130, 246, 0.05)' : 'transparent'
                                }}
                              >
                                <FormControlLabel 
                                  value={account.id}
                                  name="external_account_id" 
                                  control={<Radio />} 
                                  label={
                                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                      <Typography variant="subtitle2">{account.name}</Typography>
                                      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                        ({account.accountNumber})
                                      </Typography>
                                    </Box>
                                  }
                                  sx={{ width: '100%', m: 0 }}
                                />
                              </Box>
                            ))}
                          </RadioGroup>
                          
                          <Button
                            size="small"
                            startIcon={<AddIcon />}
                            onClick={() => setLinkDialogOpen(true)}
                            sx={{ 
                              mt: 1,
                              color: 'primary.main',
                            }}
                          >
                            Link another payment method
                          </Button>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Button
                          type="submit"
                          fullWidth
                          variant="contained"
                          disabled={loading}
                          sx={{ 
                            py: 1.8,
                            backgroundColor: 'primary.main',
                            '&:hover': {
                              backgroundColor: 'primary.dark',
                              boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                            }
                          }}
                        >
                          {loading ? <CircularProgress size={24} color="inherit" /> : 'Withdraw Funds'}
                        </Button>
                      </Grid>
                    </Grid>
                  </form>
                  
                  {error && (
                    <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>
                      {typeof error === 'string' ? error : JSON.stringify(error)}
                    </Alert>
                  )}
                  
                  {success && (
                    <Alert severity="success" sx={{ mt: 3, borderRadius: 2 }}>
                      Withdrawal initiated! Transfer ID: {success.transfer_id || success.id}
                    </Alert>
                  )}
                </>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>
      <LinkPaymentDialog open={linkDialogOpen} onClose={()=>setLinkDialogOpen(false)} />
    </Box>
  );
} 