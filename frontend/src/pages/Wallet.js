import React, { useEffect, useState, useMemo } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  CircularProgress, 
  Alert, 
  Container, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  IconButton, 
  useTheme,
  useMediaQuery,
  Button
} from '@mui/material';
import { walletAPI, bridgeAPI } from '../utils/api';
import { getUserCurrency, getCurrencySymbol } from '../utils/currencyUtils';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import RefreshIcon from '@mui/icons-material/Refresh';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import BoltIcon from '@mui/icons-material/Bolt';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import VerifiedIcon from '@mui/icons-material/Verified';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import LockIcon from '@mui/icons-material/Lock';
import AddIcon from '@mui/icons-material/Add';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CountUp from 'react-countup';

import {
  FloatingCard,
  GlassContainer,
  GradientText,
  GradientDivider,
  AnimatedBackground,
  GradientBorder,
  FuturisticAvatar,
  NeonButton
} from '../components/ui/ModernUIComponents';

import {
  SlideRightBox,
  StaggerContainer,
  StaggerItem
} from '../components/animations/AnimatedComponents';

export default function Wallet() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({ wallets: [], transactions: [] });
  const [linkedAccounts, setLinkedAccounts] = useState([
    { id: 1, name: 'Chase Bank', accountNumber: '****4582', status: 'verified' },
    { id: 2, name: 'Bank of America', accountNumber: '****7891', status: 'verified' }
  ]);
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user } = useAuth0();

  useEffect(() => {
    async function fetchOverview() {
      setLoading(true);
      setError(null);
      try {
        // Force refresh balances first to ensure data is current
        if (window.localStorage) {
          console.log("Wallet: Direct localStorage check");
          try {
            const storedBalances = localStorage.getItem('mockUserBalances');
            if (storedBalances) {
              const balances = JSON.parse(storedBalances);
              console.log("Wallet: Found stored balances:", balances);
            } else {
              console.log("Wallet: No balances found in localStorage");
            }
          } catch (e) {
            console.error("Wallet: Error checking localStorage", e);
          }
        }
        
        const resp = await walletAPI.getOverview();
        console.log("Wallet API response:", resp.data);
        setData(prev => ({
          ...prev,
          wallets: resp.data.wallets || []
        }));
        
        // Fetch transactions
        const historyResp = await walletAPI.getAllTransactions();
        const transactions = (historyResp.data && historyResp.data.transactions) ? historyResp.data.transactions : [];
        setData(prev => ({ ...prev, transactions }));
      } catch (err) {
        console.error("Wallet fetch error:", err);
        setError(err?.response?.data?.detail || err.message || 'Failed to load wallet');
      } finally {
        setLoading(false);
      }
    }
    fetchOverview();
    
    // Set up an interval to refresh data every 15 seconds
    const intervalId = setInterval(fetchOverview, 15000);
    
    // Clean up the interval when component unmounts
    return () => clearInterval(intervalId);
  }, []);

  const totalLocalBalance = useMemo(() => {
    // Special case for Hadeer - use EUR wallet balance
    if (user && user.email === 'hadeermotair@gmail.com') {
      const eurWallet = data.wallets.find(w => w.currency === 'eur');
      return eurWallet ? eurWallet.balance : 0;
    }
    
    // For other users, use USD wallet balance
    const usdWallet = data.wallets.find(w => w.currency === 'usd');
    return usdWallet ? usdWallet.balance : 0;
  }, [data.wallets, user]);

  const pendingBalance = useMemo(() => {
    // Get pending transactions
    const pendingTxns = data.transactions.filter(t => t.status === 'pending');
    return pendingTxns.reduce((sum, t) => sum + parseFloat(t.amount || 0), 0);
  }, [data.transactions]);

  const lockedBalance = useMemo(() => {
    // Special case for Hadeer - always show zero
    if (user && user.email === 'hadeermotair@gmail.com') {
      return 0;
    }
    // This is a mock value, in a real app you would calculate this from transactions
    return 0.00;
  }, [user]);

  const currency = useMemo(() => {
    // Handle special case for Hadeer
    if (user && user.email === 'hadeermotair@gmail.com') {
      return 'EUR';
    }
    
    // For other users, prefer USD
    const usdWallet = data.wallets.find(w => w.currency === 'usd');
    return usdWallet ? 'USD' : (data.wallets[0]?.currency?.toUpperCase() || 'USD');
  }, [data.wallets, user]);
  
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

  const handleDeposit = () => navigate('/wallet/deposit');
  const handleWithdraw = () => navigate('/wallet/withdraw');
  const handleCardManagement = () => navigate('/card');
  const handleAddAccount = () => alert('Add new account functionality would open here');

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress color="primary" />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

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
        pb: 8
      }}
    >
      <AnimatedBackground />
      
      <Container maxWidth="lg" sx={{ pt: 3 }}>
        {/* Header */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 4,
          flexDirection: isMobile ? 'column' : 'row',
          gap: isMobile ? 2 : 0
        }}>
          <Box component={motion.div} variants={itemVariants}>
            <Typography variant="h4" component="h1" fontWeight="600">
              Wallet
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ mt: 0.5, display: 'flex', alignItems: 'center' }}
            >
              Last updated: {format(new Date(), 'MMM dd, yyyy • HH:mm')}
              <IconButton 
                size="small" 
                sx={{ ml: 1 }}
                onClick={() => window.location.reload()}
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Typography>
          </Box>
        </Box>

        {/* Balance Summary */}
        <SlideRightBox variants={itemVariants}>
          <FloatingCard 
            sx={{ 
              p: 3, 
              mb: 4,
              background: 'rgba(17, 24, 39, 0.7)',
              borderColor: 'rgba(59, 130, 246, 0.1)'
            }}
          >
            <Box>
              <Typography variant="body2" color="text.secondary" fontWeight="500">Total Balance</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography variant="h3" component="div" fontWeight={700}>
                  <CountUp
                    start={0}
                    end={totalLocalBalance}
                    duration={1.5}
                    separator=","
                    decimals={2}
                    decimal="."
                    prefix={getCurrencySymbol(currency)}
                  />
                </Typography>
              </Box>
            </Box>
          </FloatingCard>
        </SlideRightBox>

        {/* Wallet Actions */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <motion.div variants={itemVariants}>
              <FloatingCard sx={{ 
                p: 3,
                height: '100%',
                background: 'rgba(17, 24, 39, 0.7)',
                borderColor: 'rgba(59, 130, 246, 0.1)'
              }}>
                <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                  Wallet Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Button
                      variant="contained"
                      fullWidth
                      startIcon={<ArrowDownwardIcon />}
                      onClick={handleDeposit}
                      sx={{ 
                        py: 1.5, 
                        backgroundColor: 'primary.main',
                        '&:hover': {
                          backgroundColor: 'primary.dark',
                          boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                        }
                      }}
                    >
                      Deposit
                    </Button>
                  </Grid>
                  <Grid item xs={6}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<ArrowUpwardIcon />}
                      onClick={handleWithdraw}
                      sx={{ 
                        py: 1.5,
                        borderColor: 'rgba(59, 130, 246, 0.6)',
                        color: 'primary.main',
                        '&:hover': {
                          borderColor: 'primary.main',
                          boxShadow: '0 0 15px rgba(59, 130, 246, 0.3)'
                        }
                      }}
                    >
                      Withdraw
                    </Button>
                  </Grid>
                </Grid>
              </FloatingCard>
            </motion.div>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <motion.div variants={itemVariants}>
              <FloatingCard sx={{ 
                p: 3,
                height: '100%',
                background: 'rgba(17, 24, 39, 0.7)',
                borderColor: 'rgba(59, 130, 246, 0.1)'
              }}>
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  mb: 2 
                }}>
                  <Typography variant="h6" fontWeight="600">
                    Card
                  </Typography>
                  <Button
                    size="small"
                    variant="text"
                    onClick={handleCardManagement}
                    endIcon={<CreditCardIcon />}
                    sx={{ color: 'primary.main' }}
                  >
                    Manage Card
                  </Button>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Use your wallet funds for purchases anywhere with our card. Instantly convert your balance to spend at millions of locations worldwide.
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<CreditCardIcon />}
                  onClick={handleCardManagement}
                  sx={{ 
                    mt: 2,
                    py: 1.5,
                    backgroundColor: 'primary.main',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                      boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                    }
                  }}
                >
                  Go to Card Page
                </Button>
              </FloatingCard>
            </motion.div>
          </Grid>
        </Grid>

        {/* Linked Accounts */}
        <motion.div variants={itemVariants}>
          <FloatingCard sx={{ 
            p: 3,
            mb: 4,
            background: 'rgba(17, 24, 39, 0.7)',
            borderColor: 'rgba(59, 130, 246, 0.1)'
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight="600">
                Linked Accounts
              </Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                variant="text"
                onClick={handleAddAccount}
                sx={{ color: 'primary.main' }}
              >
                Add
              </Button>
            </Box>
            
            <List sx={{ p: 0 }}>
              {linkedAccounts.map((account, index) => (
                <ListItem 
                  key={account.id}
                  sx={{ 
                    p: 2, 
                    mb: index < linkedAccounts.length - 1 ? 2 : 0, 
                    borderRadius: 2,
                    background: 'rgba(17, 24, 39, 0.5)',
                    border: '1px solid rgba(55, 65, 81, 0.5)',
                  }}
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
                    secondary={`Checking ${account.accountNumber}`}
                  />
                </ListItem>
              ))}
            </List>
          </FloatingCard>
        </motion.div>

        {/* FAQs */}
        <motion.div variants={itemVariants}>
          <FloatingCard sx={{ 
            p: 3,
            background: 'rgba(17, 24, 39, 0.7)',
            borderColor: 'rgba(59, 130, 246, 0.1)'
          }}>
            <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
              Frequently Asked Questions
            </Typography>
            
            <Accordion 
              sx={{ 
                background: 'rgba(17, 24, 39, 0.5)', 
                mb: 2,
                '&::before': {
                  display: 'none',
                }
              }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={500}>How long do bank transfers take?</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary">
                  Bank transfers typically take 1-3 business days to complete, depending on your bank and location.
                </Typography>
              </AccordionDetails>
            </Accordion>
            
            <Accordion 
              sx={{ 
                background: 'rgba(17, 24, 39, 0.5)', 
                mb: 2,
                '&::before': {
                  display: 'none',
                }
              }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={500}>Are there any withdrawal limits?</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary">
                  Yes, withdrawal limits depend on your account verification level. Standard accounts can withdraw up to $5,000 per day.
                </Typography>
              </AccordionDetails>
            </Accordion>
            
            <Accordion 
              sx={{ 
                background: 'rgba(17, 24, 39, 0.5)',
                '&::before': {
                  display: 'none',
                }
              }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={500}>How do I link a new bank account?</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary">
                  To link a new bank account, go to the "Linked Accounts" section and click "Add". You'll need your bank account details and may need to verify small test deposits.
                </Typography>
              </AccordionDetails>
            </Accordion>
          </FloatingCard>
        </motion.div>
      </Container>
    </Box>
  );
} 