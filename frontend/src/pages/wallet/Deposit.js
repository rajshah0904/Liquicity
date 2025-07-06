import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  FormControlLabel, 
  Switch, 
  Button, 
  Alert, 
  CircularProgress, 
  Container,
  Grid,
  Stack,
  ListItem,
  ListItemIcon,
  ListItemText,
  List,
  Radio,
  RadioGroup,
  FormControl,
  FormLabel,
  useTheme,
  useMediaQuery,
  IconButton,
  Divider,
  Paper,
  InputAdornment,
  MenuItem,
  Tooltip,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { transferAPI, bridgeAPI, authAPI, externalAccountsAPI } from '../../utils/api';
import useBridgeWallet from '../../hooks/useBridgeWallet';
import { useNavigate, useLocation } from 'react-router-dom';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import RefreshIcon from '@mui/icons-material/Refresh';
import BoltIcon from '@mui/icons-material/Bolt';
import VerifiedIcon from '@mui/icons-material/Verified';
import AddIcon from '@mui/icons-material/Add';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { 
  INSTANT_DEPOSIT_FEE_RATE, 
  UI_INSTANT_DEPOSIT_FEE,
  calculateFee
} from '../../utils/feeConstants';

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

export default function Deposit() {
  const [step, setStep] = useState('select-method'); // select-method, link-bank, deposit-form
  const [form, setForm] = useState({ 
    amount: '', 
    external_account_id: '',
    depositType: 'instant' // only instant deposit supported
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
  
  const [plaidLinkToken, setPlaidLinkToken] = useState(null);
  
  const { wallet: bridgeWallet, loading: walletLoading } = useBridgeWallet();
  const [balanceData, setBalanceData] = useState({ total: 0, available: 0, currency: 'USD' });
  
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isLinkBankMode = location.pathname.includes('/link-bank');

  // If deposit page is opened with ?action=link-account, just show link-bank step
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('action') === 'link-account' || isLinkBankMode) {
      setStep('link-bank');
    }
  }, [location.pathname, location.search]);

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
      setError('Failed to load your linked bank accounts');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    // Fetch linked accounts when component mounts
    fetchLinkedAccounts();
    
    // Set region from profile once
    (async () => {
      try {
        const userResp = await authAPI.getCurrentUser();
        if (userResp.data) {
          const region = getUserRegion(userResp.data);
          setUserRegion(region);
        }
      } catch (e) {}
    })();
  }, [location.search, userRegion.region]);

  // Update balance when bridgeWallet changes
  useEffect(() => {
    if (bridgeWallet) {
      const total = bridgeWallet.balances?.reduce((s,b)=>s+parseFloat(b.balance||0),0) || 0;
      setBalanceData({ total, available: total, currency: 'USD' });
    }
  }, [bridgeWallet]);

  // Load Plaid script once based on user region
  useEffect(() => {
    if (userRegion.region === 'us' && !window.Plaid) {
      try {
        const script = document.createElement('script');
        script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
        script.async = true;
        script.onerror = () => {
          console.error('Failed to load Plaid script');
        };
        document.body.appendChild(script);
      } catch (err) {
        console.error('Error loading Plaid script:', err);
      }
    }
  }, [userRegion.region]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? checked : value 
    }));
  };

  const handleNewAccountChange = (e) => {
    const { name, value } = e.target;
    setNewAccountForm((prev) => ({ 
      ...prev, 
      [name]: value 
    }));
  };

  const handleSelectAccount = (accountId) => {
    setForm((prev) => ({ 
      ...prev, 
      external_account_id: accountId 
    }));
    setStep('deposit-form');
  };

  // Function to initialize Plaid Link
  const initializePlaidLink = async () => {
    try {
      // Ensure Plaid script is present
      if (!window.Plaid) {
        // Try to load script dynamically and wait for it
        await new Promise((resolve, reject) => {
          const existing = document.querySelector('script[src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"]');
          if (existing) {
            existing.addEventListener('load', resolve);
            existing.addEventListener('error', () => reject(new Error('Plaid script failed to load')));
          } else {
            const script = document.createElement('script');
            script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
            script.async = true;
            script.onload = resolve;
            script.onerror = () => reject(new Error('Plaid script failed to load'));
            document.body.appendChild(script);
          }
        });
        if (!window.Plaid) {
          throw new Error('Plaid script not available after load');
        }
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
  const openPlaidLink = async (token) => {
    if (!token) return;
    
    const linkTokenUsed = token;  // pass same token back to server per Bridge docs
    const handler = window.Plaid.create({
      token,
      onSuccess: async (publicToken, metadata) => {
        try {
          setLoading(true);
          // Exchange the public token via Bridge
          await externalAccountsAPI.exchangePlaidToken(linkTokenUsed, publicToken);
          
          // Fetch updated list of accounts after linking
          fetchLinkedAccounts();
          // Move to deposit form
          setStep('deposit-form');
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
          setStep('select-method');
        }
      },
      onEvent: (eventName, metadata) => {
        console.log('Plaid Link Event:', eventName, metadata);
      }
    });
    
    handler.open();
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
      
      // Move to deposit form with the new account selected
      setForm(prev => ({ ...prev, external_account_id: response.data.id }));
      setStep('deposit-form');
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
    
    try {
      const resp = await transferAPI.deposit({
        amount: form.amount,
        currency: userRegion.currency,
        external_account_id: form.external_account_id,
        instant: form.depositType === 'instant',
      });
      
      setSuccess(resp.data);
      // Reset form but keep the selected account
      setForm(prev => ({ 
        amount: '', 
        external_account_id: prev.external_account_id,
        depositType: 'instant'
      }));
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err.message || 'Deposit failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (step === 'deposit-form') {
      setStep('select-method');
    } else if (step === 'link-bank') {
      setStep('select-method');
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
    if (userRegion.region === 'us') {
      // US users go to Plaid
      initializePlaidLink();
    } else {
      // Non-US users go to manual entry
      setStep('link-bank');
    }
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
                {step !== 'select-method' && (
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
                  {(isLinkBankMode || step==='link-bank') ? 'Link Bank Account' : 'Deposit Funds'}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {(isLinkBankMode || step==='link-bank') ? 'Securely connect your bank account' : 'Add money to your Liquicity account'}
                </Typography>
              </Box>
              
              {/* Step 1: Select Bank Account or Link New One */}
              {step === 'select-method' && (
                <>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                    Select Bank Account
                  </Typography>
                  
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                      <CircularProgress />
                    </Box>
                  ) : linkedAccounts.length > 0 ? (
                    <List disablePadding>
                      {linkedAccounts.map(account => (
                        <ListItem 
                          key={account.id}
                          sx={{ 
                            mb: 2, 
                            p: 2, 
                            borderRadius: 2, 
                            cursor: 'pointer',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            '&:hover': {
                              borderColor: 'primary.main',
                              bgcolor: 'rgba(59, 130, 246, 0.1)'
                            }
                          }}
                          onClick={() => handleSelectAccount(account.id)}
                        >
                          <ListItemIcon sx={{ minWidth: 42 }}>
                            <AccountBalanceIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={account.bank_name || account.name} 
                            secondary={account.last4 ? `****${account.last4}` : account.accountNumber}
                            primaryTypographyProps={{ fontWeight: 600 }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Box sx={{ 
                      p: 3, 
                      borderRadius: 2, 
                      textAlign: 'center',
                      border: '1px dashed rgba(255, 255, 255, 0.2)',
                      mb: 3
                    }}>
                      <Typography color="text.secondary" sx={{ mb: 1 }}>
                        No bank accounts linked yet
                      </Typography>
                    </Box>
                  )}
                  
                    <Button
                      startIcon={<AddIcon />}
                      variant="outlined"
                      fullWidth
                    onClick={() => navigate('/wallet/link-bank')}
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
                    Link Bank Account
                    </Button>
                </>
              )}
              
              {/* Step 2: Link New Bank Account */}
              {step === 'link-bank' && (
                <>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                    Add Bank Account
                  </Typography>
                  
                  {userRegion.region === 'us' && (
                    <Box sx={{ mb: 4, p: 3, borderRadius: 2, bgcolor: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                      <Typography variant="subtitle1" fontWeight="600" sx={{ mb: 1 }}>
                          Recommended: Connect with Plaid
                        </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Securely connect your US bank account with Plaid for faster verification and setup.
                      </Typography>
                      <Button 
                        variant="contained" 
                        color="primary" 
                        fullWidth 
                        onClick={initializePlaidLink}
                        sx={{ mt: 2 }}
                      >
                        Connect with Plaid
                      </Button>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 1 }}>
                        Or continue with manual entry below if your bank isn't supported
                      </Typography>
                    </Box>
                  )}
                  
                  <form onSubmit={handleLinkNewAccount}>
                    <Grid container spacing={3}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Bank Name"
                          name="bank_name"
                          value={newAccountForm.bank_name}
                          onChange={(e) => setNewAccountForm({...newAccountForm, bank_name: e.target.value})}
                          required
                          variant="outlined"
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Account Owner Name"
                          name="account_owner_name"
                          value={newAccountForm.account_owner_name}
                          onChange={(e) => setNewAccountForm({...newAccountForm, account_owner_name: e.target.value})}
                          required
                          variant="outlined"
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Account Name (optional)"
                          name="account_name"
                          value={newAccountForm.account_name}
                          onChange={(e) => setNewAccountForm({...newAccountForm, account_name: e.target.value})}
                          variant="outlined"
                          helperText="A nickname for your account, e.g., 'Personal Checking'"
                        />
                      </Grid>
                      
                      {userRegion.region === 'us' ? (
                        // US account fields
                        <>
                          <Grid item xs={12} sm={6}>
                            <TextField
                              fullWidth
                              label="Account Number"
                              name="account_number"
                              value={newAccountForm.account_number}
                              onChange={(e) => setNewAccountForm({...newAccountForm, account_number: e.target.value})}
                              required
                              variant="outlined"
                            />
                          </Grid>
                          
                          <Grid item xs={12} sm={6}>
                            <TextField
                              fullWidth
                              label="Routing Number"
                              name="routing_number"
                              value={newAccountForm.routing_number}
                              onChange={(e) => setNewAccountForm({...newAccountForm, routing_number: e.target.value})}
                              required
                              variant="outlined"
                            />
                          </Grid>
                        </>
                      ) : (
                        // EU account fields
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            label="IBAN"
                            name="iban"
                            value={newAccountForm.iban}
                            onChange={(e) => setNewAccountForm({...newAccountForm, iban: e.target.value})}
                            required
                            variant="outlined"
                          />
                        </Grid>
                      )}
                      
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" sx={{ mb: 2 }}>
                          Account Address
                        </Typography>
                        
                        <Grid container spacing={2}>
                          <Grid item xs={12}>
                            <TextField
                              fullWidth
                              label="Street Address"
                              name="street_line_1"
                              value={newAccountForm.address.street_line_1}
                              onChange={(e) => setNewAccountForm({
                                ...newAccountForm, 
                                address: {...newAccountForm.address, street_line_1: e.target.value}
                              })}
                              required
                              variant="outlined"
                            />
                          </Grid>
                          
                          <Grid item xs={12}>
                            <TextField
                              fullWidth
                              label="Street Address Line 2 (optional)"
                              name="street_line_2"
                              value={newAccountForm.address.street_line_2}
                              onChange={(e) => setNewAccountForm({
                                ...newAccountForm, 
                                address: {...newAccountForm.address, street_line_2: e.target.value}
                              })}
                              variant="outlined"
                            />
                          </Grid>
                          
                          <Grid item xs={12} sm={6}>
                            <TextField
                              fullWidth
                              label="City"
                              name="city"
                              value={newAccountForm.address.city}
                              onChange={(e) => setNewAccountForm({
                                ...newAccountForm, 
                                address: {...newAccountForm.address, city: e.target.value}
                              })}
                              required
                              variant="outlined"
                            />
                          </Grid>
                          
                          <Grid item xs={12} sm={6}>
                            <TextField
                              fullWidth
                              label={userRegion.region === 'us' ? "State" : "Province/Region"}
                              name="state"
                              value={newAccountForm.address.state}
                              onChange={(e) => setNewAccountForm({
                                ...newAccountForm, 
                                address: {...newAccountForm.address, state: e.target.value}
                              })}
                              required
                              variant="outlined"
                            />
                          </Grid>
                          
                          <Grid item xs={12} sm={6}>
                            <TextField
                              fullWidth
                              label={userRegion.region === 'us' ? "ZIP Code" : "Postal Code"}
                              name="postal_code"
                              value={newAccountForm.address.postal_code}
                              onChange={(e) => setNewAccountForm({
                                ...newAccountForm, 
                                address: {...newAccountForm.address, postal_code: e.target.value}
                              })}
                              required
                              variant="outlined"
                            />
                          </Grid>
                        </Grid>
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
                          {loading ? <CircularProgress size={24} color="inherit" /> : 'Link Account'}
                        </Button>
                      </Grid>
                    </Grid>
                  </form>
                </>
              )}
              
              {/* Step 3: Deposit Form */}
              {step === 'deposit-form' && (
                <>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                    Make a Deposit
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
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="subtitle1" fontWeight={600}>
                              Instant Deposit
                            </Typography>
                            <Typography variant="caption" component="span" sx={{ bgcolor: 'rgba(59, 130, 246, 0.1)', px: 1, py: 0.5, borderRadius: 1, fontWeight: 'medium' }}>
                              No Fee
                            </Typography>
                          </Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                            Deposits are credited instantly (under&nbsp;1&nbsp;minute).
                          </Typography>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Button
                          type="submit"
                          fullWidth
                          variant="contained"
                          disabled={loading || !form.amount}
                          sx={{ 
                            py: 1.8,
                            backgroundColor: 'primary.main',
                            '&:hover': {
                              backgroundColor: 'primary.dark',
                              boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                            }
                          }}
                        >
                          {loading ? <CircularProgress size={24} color="inherit" /> : 'Make Deposit'}
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
                      Deposit initiated! Transfer ID: {success.on_ramp_transfer_id || success.id}
                    </Alert>
                  )}
                </>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
} 