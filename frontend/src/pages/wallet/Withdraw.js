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
import { transferAPI, bridgeAPI, walletAPI } from '../../utils/api';
import { useNavigate } from 'react-router-dom';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import RefreshIcon from '@mui/icons-material/Refresh';
import CreditCardIcon from '@mui/icons-material/CreditCard';
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

// Helper function to detect user region based on browser language
const detectUserRegion = () => {
  const language = navigator.language || 'en-US';
  
  if (language.includes('es-MX')) return { region: 'mx', currency: 'mxn' };
  if (language.includes('en-US')) return { region: 'us', currency: 'usd' };
  if (language.startsWith('es')) return { region: 'mx', currency: 'mxn' };
  
  // Default to European
  const europeanLanguages = ['de', 'fr', 'it', 'es', 'pt', 'nl', 'el', 'pl'];
  for (const lang of europeanLanguages) {
    if (language.startsWith(lang)) return { region: 'eu', currency: 'eur' };
  }
  
  return { region: 'eu', currency: 'eur' };
};

export default function Withdraw() {
  const [step, setStep] = useState('select-method'); // select-method, link-bank, withdraw-form
  const [form, setForm] = useState({ 
    amount: '', 
    external_account_id: '',
    withdrawalType: 'standard' // standard or card
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [linkedAccounts, setLinkedAccounts] = useState([]);
  const [detectedRegion, setDetectedRegion] = useState(detectUserRegion());
  const [newAccountForm, setNewAccountForm] = useState({ 
    account_number: '', 
    routing_number: '', 
    account_type: 'checking',
    holder_name: ''
  });
  
  const [balanceData, setBalanceData] = useState({
    total: 4256.78,
    available: 3892.45,
    currency: 'USD'
  });
  
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    // Fetch linked accounts when component mounts
    const fetchLinkedAccounts = async () => {
      setLoading(true);
      try {
        // In a real app, this would be an API call to get user's linked accounts
        // For now, let's simulate it with mock data
        setTimeout(() => {
          setLinkedAccounts([
            { id: 'ext-001', name: 'Chase Bank', accountNumber: '****4582', status: 'verified' },
            { id: 'ext-002', name: 'Bank of America', accountNumber: '****7891', status: 'verified' }
          ]);
          setLoading(false);
        }, 500);
      } catch (err) {
        console.error(err);
        setError('Failed to load linked accounts');
        setLoading(false);
      }
    };
    
    fetchLinkedAccounts();
    
    // Fetch wallet data
    const fetchWalletData = async () => {
      try {
        const resp = await walletAPI.getOverview();
        if (resp.data && resp.data.wallets && resp.data.wallets.length > 0) {
          const mainWallet = resp.data.wallets[0];
          setBalanceData({
            total: mainWallet.total_balance || 0,
            available: mainWallet.available_balance || 0,
            currency: mainWallet.local_currency?.toUpperCase() || 'USD'
          });
        }
      } catch (err) {
        console.error('Failed to fetch wallet data', err);
      }
    };
    
    fetchWalletData();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
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
    setStep('withdraw-form');
  };

  const handleLinkNewAccount = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real app, you'd call an API here
      // For now, let's simulate it
      setTimeout(() => {
        const newAccount = {
          id: `ext-${Math.floor(Math.random() * 1000)}`,
          name: 'New Bank Account',
          accountNumber: `****${newAccountForm.account_number.slice(-4)}`,
          status: 'verified'
        };
        
        setLinkedAccounts(prev => [...prev, newAccount]);
        setForm(prev => ({ ...prev, external_account_id: newAccount.id }));
        setStep('withdraw-form');
        setLoading(false);
      }, 1000);
    } catch (err) {
      console.error(err);
      setError('Failed to link new account');
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    if (form.withdrawalType === 'card') {
      // Navigate to card page if card is selected
      navigate('/card');
      return;
    }
    
    try {
      const resp = await transferAPI.withdraw({
        amount: form.amount,
        currency: detectedRegion.currency,
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

  // Get rail name based on region
  const getRailName = () => {
    switch (detectedRegion.region) {
      case 'us': return 'ACH';
      case 'eu': return 'SEPA';
      case 'mx': return 'SPEI';
      default: return 'Bank Transfer';
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
                Balance: <Typography component="span" fontWeight="600" color="#fff">${balanceData.available.toLocaleString()}</Typography>
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
              
              {/* Step 1: Select Withdrawal Method */}
              {step === 'select-method' && (
                <>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                    Select Withdrawal Method
                  </Typography>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Box 
                        sx={{ 
                          p: 3, 
                          borderRadius: 2, 
                          background: 'rgba(17, 24, 39, 0.5)', 
                          border: '1px solid rgba(55, 65, 81, 0.5)',
                          height: '100%',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          '&:hover': {
                            background: 'rgba(59, 130, 246, 0.1)',
                            borderColor: 'rgba(59, 130, 246, 0.3)',
                          }
                        }}
                        onClick={() => linkedAccounts.length > 0 ? setStep('withdraw-form') : setStep('link-bank')}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Box sx={{ 
                            mr: 2, 
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
                          <Box>
                            <Typography variant="subtitle1" fontWeight="600">Bank Transfer</Typography>
                            <Typography variant="caption" color="text.secondary">1-3 business days</Typography>
                          </Box>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Transfer funds to your linked bank account. No fees. Standard processing time.
                        </Typography>
                      </Box>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Box 
                        sx={{ 
                          p: 3, 
                          borderRadius: 2, 
                          background: 'rgba(17, 24, 39, 0.5)', 
                          border: '1px solid rgba(55, 65, 81, 0.5)',
                          height: '100%',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          '&:hover': {
                            background: 'rgba(245, 158, 11, 0.05)',
                            borderColor: 'rgba(245, 158, 11, 0.3)',
                          }
                        }}
                        onClick={() => navigate('/card')}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Box sx={{ 
                            mr: 2, 
                            borderRadius: '50%', 
                            width: 40, 
                            height: 40, 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)'
                          }}>
                            <CreditCardIcon sx={{ color: '#f59e0b' }} />
                          </Box>
                          <Box>
                            <Typography variant="subtitle1" fontWeight="600">Spend via Card</Typography>
                            <Typography variant="caption" color="text.secondary">Available immediately</Typography>
                          </Box>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Use your Visa card to spend your funds instantly at millions of locations worldwide without withdrawal.
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </>
              )}
              
              {/* Select Bank Account */}
              {step === 'select-bank' && (
                <>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                    Select Bank Account
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
                        fullWidth
                        variant="outlined"
                        startIcon={<AddIcon />}
                        onClick={() => setStep('link-bank')}
                        sx={{ 
                          mt: 2,
                          py: 2,
                          borderColor: 'rgba(59, 130, 246, 0.3)',
                          color: 'primary.main',
                          borderStyle: 'dashed',
                          borderWidth: '1px',
                          '&:hover': {
                            borderColor: 'primary.main',
                            background: 'rgba(59, 130, 246, 0.05)',
                          }
                        }}
                      >
                        Link New Bank Account
                      </Button>
                    </List>
                  ) : (
                    <Box sx={{ py: 3, textAlign: 'center' }}>
                      <Typography color="text.secondary" sx={{ mb: 3 }}>
                        You don't have any linked bank accounts
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
                        Link Bank Account
                      </Button>
                    </Box>
                  )}
                </>
              )}
              
              {/* Step 2: Link New Bank Account */}
              {step === 'link-bank' && (
                <>
                  <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
                    Link New Bank Account
                  </Typography>
                  
                  <form>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Account Holder Name"
                          name="holder_name"
                          value={newAccountForm.holder_name}
                          onChange={handleNewAccountChange}
                          variant="outlined"
                          required
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '12px',
                            }
                          }}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Account Number"
                          name="account_number"
                          value={newAccountForm.account_number}
                          onChange={handleNewAccountChange}
                          variant="outlined"
                          required
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '12px',
                            }
                          }}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Routing Number"
                          name="routing_number"
                          value={newAccountForm.routing_number}
                          onChange={handleNewAccountChange}
                          variant="outlined"
                          required
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '12px',
                            }
                          }}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <TextField
                          select
                          fullWidth
                          label="Account Type"
                          name="account_type"
                          value={newAccountForm.account_type}
                          onChange={handleNewAccountChange}
                          variant="outlined"
                          SelectProps={{
                            native: true,
                          }}
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '12px',
                            }
                          }}
                        >
                          <option value="checking">Checking</option>
                          <option value="savings">Savings</option>
                        </TextField>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Typography variant="caption" color="text.secondary">
                          By linking your account, you authorize Liquicity to verify your account details and process funds transfers as requested.
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Button
                          fullWidth
                          variant="contained"
                          disabled={!newAccountForm.account_number || !newAccountForm.routing_number || !newAccountForm.holder_name || loading}
                          onClick={handleLinkNewAccount}
                          sx={{ 
                            py: 1.5,
                            backgroundColor: 'primary.main',
                            '&:hover': {
                              backgroundColor: 'primary.dark',
                              boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                            }
                          }}
                        >
                          {loading ? <CircularProgress size={24} color="inherit" /> : 'Link Bank Account'}
                        </Button>
                      </Grid>
                    </Grid>
                  </form>
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
                            Select Bank Account
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
                            onClick={() => setStep('link-bank')}
                            sx={{ 
                              mt: 1,
                              color: 'primary.main',
                            }}
                          >
                            Link another account
                          </Button>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Button
                          type="submit"
                          fullWidth
                          variant="contained"
                          disabled={loading || !form.amount || !form.external_account_id}
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
        
        {/* Card Info */}
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} md={6}>
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
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CreditCardIcon sx={{ color: 'primary.main', mr: 2 }} />
                <Typography variant="h6" fontWeight="600" color="#fff">
                  Need to spend your funds immediately?
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Use your Liquicity Visa card to spend your funds instantly at millions of locations worldwide without withdrawal.
              </Typography>
              <Button 
                variant="outlined" 
                onClick={() => navigate('/card')}
                startIcon={<CreditCardIcon />}
                sx={{ 
                  borderColor: 'rgba(59, 130, 246, 0.5)',
                  color: theme.palette.primary.main,
                  '&:hover': {
                    borderColor: theme.palette.primary.main,
                    background: 'rgba(59, 130, 246, 0.05)'
                  }
                }}
              >
                View Card Options
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
} 