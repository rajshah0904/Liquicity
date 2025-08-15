import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Container,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  useTheme,
  useMediaQuery,
  LinearProgress,
  Tooltip,
  IconButton,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import CountUp from 'react-countup';
import {
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  SwapHoriz as SwapHorizIcon,
  Add as AddIcon,
  Download as DepositIcon,
  Upload as WithdrawIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  ArrowDownward as ArrowDownwardIcon,
  ArrowUpward as ArrowUpwardIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';
import VerifiedIcon from '@mui/icons-material/Verified';

// Use clean_backend hooks
import useBridgeWallet from '../hooks/useBridgeWallet';
import { externalAccountsAPI } from '../utils/api';
import { calculateLiquicityBalance } from '../utils/balanceUtils';
import { getCurrencySymbol } from '../utils/currency';

import {
  FloatingCard,
  GlassContainer,
  GradientText,
  GradientDivider,
  AnimatedBackground,
  NeonButton
} from '../components/ui/ModernUIComponents';

import {
  SlideRightBox,
  StaggerContainer,
  StaggerItem
} from '../components/animations/AnimatedComponents';

import LinkPaymentDialog from '../components/LinkPaymentDialog';

export default function Wallet() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data] = useState({ wallets: [], transactions: [] });
  const [linkedAccounts, setLinkedAccounts] = useState([]);
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Live Bridge wallet hook
  const { wallet: bridgeWallet, loading: walletLoading, refetch: refetchWallet } = useBridgeWallet();

  const [linkDialogOpen, setLinkDialogOpen] = useState(false);

  useEffect(() => {
    // No overview endpoint on clean backend – everything comes from hooks now
    
    // Fetch linked accounts
    async function fetchLinkedAccounts() {
      try {
        // Fetch the accounts directly from our local database
        const response = await externalAccountsAPI.getAccounts();
        setLinkedAccounts(response.data.accounts || []);
      } catch (err) {
        console.error('Error fetching linked accounts:', err);
        // Don't set the main error state to avoid blocking the whole page
      }
    }
    fetchLinkedAccounts();
  }, []);

  const totalLocalBalance = useMemo(() => {
    return calculateLiquicityBalance(bridgeWallet);
  }, [bridgeWallet]);

  const pendingBalance = useMemo(() => {
    // This is a mock value, in a real app you would calculate this from transactions
    return 364.33;
  }, []);

  const lockedBalance = useMemo(() => {
    // This is a mock value, in a real app you would calculate this from transactions
    return 0.00;
  }, []);

  const currency = useMemo(() => {
    return (bridgeWallet?.fiat_currency || 'USD').toUpperCase();
  }, [bridgeWallet]);
  
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
  const handleCardManagement = () => navigate('/virtual-account');
  const handleAddAccount = () => setLinkDialogOpen(true);

  if (walletLoading) {
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
                onClick={refetchWallet}
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
                    prefix={`${getCurrencySymbol(currency)}`}
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
                    Virtual Account
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  View your bank details to receive funds directly into your wallet via ACH or wire transfers.
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<AccountBalanceIcon />}
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
                  View Account Details
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
                Linked Payment Methods
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
                          {account.bank_name}
                        </Typography>
                        {account.active && (
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            ml: 1,
                            color: 'success.main',
                            fontSize: '0.75rem'
                          }}>
                            <VerifiedIcon fontSize="inherit" sx={{ mr: 0.5 }} />
                            <Typography variant="caption" color="success.main">Active</Typography>
                          </Box>
                        )}
                      </Box>
                    }
                    secondary={`****${account.last4}`}
                  />
                </ListItem>
              ))}
            </List>
            <LinkPaymentDialog open={linkDialogOpen} onClose={()=>setLinkDialogOpen(false)} />
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
                  To link a new bank account, go to the "Linked Payment Methods" section and click "Add". You'll need your bank account details and may need to verify small test deposits.
                </Typography>
              </AccordionDetails>
            </Accordion>
          </FloatingCard>
        </motion.div>
      </Container>
    </Box>
  );
} 