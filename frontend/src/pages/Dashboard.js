import React, { useEffect, useState } from 'react';
import { 
  Box,
  Container, 
  Typography, 
  CircularProgress,
  Alert,
  Divider,
  Chip,
  Grid,
  IconButton,
  Stack,
  useTheme,
  useMediaQuery,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Tooltip,
  alpha,
  ListItemIcon
} from '@mui/material';
import { walletAPI } from '../utils/api';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import SendIcon from '@mui/icons-material/Send';
import ReceiveIcon from '@mui/icons-material/CallReceived';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PaidIcon from '@mui/icons-material/Paid';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import { format } from 'date-fns';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import AddIcon from '@mui/icons-material/Add';
import PaymentsIcon from '@mui/icons-material/Payments';
import AccountBalanceWallet from '@mui/icons-material/AccountBalanceWallet';
import { useAuth0 } from '@auth0/auth0-react';
import NotificationCenter from '../components/NotificationCenter';
import useBridgeWallet from '../hooks/useBridgeWallet';
import useBridgeTransactions from '../hooks/useBridgeTransactions';
import { calculateLiquicityBalance } from '../utils/balanceUtils';
import { getCurrencySymbol } from '../utils/currency';

// Import our custom UI components
import {
  FloatingCard,
  NeonButton,
  GradientBorder,
  GradientDivider,
  GradientChip,
  GlassIconButton,
  GradientText,
  AnimatedBackground,
  FuturisticAvatar,
  GlassContainer,
} from '../components/ui/ModernUIComponents';

import {
  AnimatedCard,
  SlideUpBox,
  SlideRightBox,
  FadeInBox,
  ScaleUpBox,
  StaggerContainer,
  StaggerItem,
  MotionBox
} from '../components/animations/AnimatedComponents';

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth0();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pending, setPending] = useState(0);
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isMediumScreen = useMediaQuery(theme.breakpoints.down('md'));
  const [mainBalance, setMainBalance] = useState(0);
  const [mainCurrency, setMainCurrency] = useState('USD');
  const [stablecoinBalance, setStablecoinBalance] = useState(0);
  const [recentTransactions, setRecentTransactions] = useState([]);

  // Bridge wallet hook
  const { wallet: bridgeWallet, loading: walletLoading } = useBridgeWallet();

  // Hook for live transactions
  const { txns: transactions, loading: txLoading } = useBridgeTransactions();

  // Derive pending, recent, etc. whenever transactions update
  useEffect(() => {
    if (!transactions) return;
    const sorted = [...transactions].sort((a,b)=> new Date(b.created_at)- new Date(a.created_at));
    setRecentTransactions(sorted.slice(0,5));
    const pendingAmount = transactions.filter(tx=> tx.status==='pending').reduce((s,tx)=> s+Number(tx.amount||0),0);
    setPending(pendingAmount);
  }, [transactions]);

  // Update balances whenever live wallet changes
  useEffect(() => {
    if (bridgeWallet) {
      // Use new fiat_balance_by_rate calculation
      const total = calculateLiquicityBalance(bridgeWallet);
      setMainBalance(total);
      setMainCurrency(bridgeWallet.fiat_currency || 'USD');
    }
  }, [bridgeWallet]);

  // Format currency
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

  // Quick actions
  const handleSendMoney = () => navigate('/payments/send');
  const handleReceiveMoney = () => navigate('/payments/request');
  const handleAddFunds = () => navigate('/wallet/deposit');
  const handleWithdraw = () => navigate('/wallet/withdraw');
  const handleHistory = () => navigate('/transactions');
  const handleSwap = () => navigate('/wallet');
  const handleLink = () => navigate('/wallet');

  // Helper functions for transactions
  const getTransactionTypeColor = (type) => {
    switch(type) {
      case 'DEPOSIT':
      case 'RECEIVE':
        return alpha(theme.palette.success.main, 0.1);
      case 'WITHDRAW':
      case 'SEND':
        return alpha(theme.palette.error.main, 0.1);
      case 'EXCHANGE':
        return alpha(theme.palette.warning.main, 0.1);
      default:
        return alpha(theme.palette.primary.main, 0.1);
    }
  };

  const getTransactionIcon = (type) => {
    switch(type) {
      case 'DEPOSIT':
      case 'RECEIVE':
        return <ReceiveIcon sx={{ color: theme.palette.success.main }} />;
      case 'WITHDRAW':
      case 'SEND':
        return <SendIcon sx={{ color: theme.palette.error.main }} />;
      case 'EXCHANGE':
        return <SwapHorizIcon sx={{ color: theme.palette.warning.main }} />;
      default:
        return <PaymentsIcon sx={{ color: theme.palette.primary.main }} />;
    }
  };

  const getTransactionTypeLabel = (type) => {
    switch(type) {
      case 'DEPOSIT':
        return 'Money Deposited';
      case 'WITHDRAW':
        return 'Money Withdrawn';
      case 'SEND':
        return 'Money Sent';
      case 'RECEIVE':
        return 'Money Received';
      case 'EXCHANGE':
        return 'Currency Exchange';
      default:
        return type;
    }
  };

  // Get transaction color based on status and type
  const getTransactionColor = (transaction) => {
    if (transaction.status === 'pending') return 'warning';
    if (transaction.status === 'failed') return 'error';
    if (transaction.type === 'deposit' || transaction.type === 'receive') return 'success';
    if (transaction.type === 'withdraw' || transaction.type === 'send') return 'error';
    return 'primary';
  };

  // Format transaction date
  const formatTransactionDate = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return format(date, 'MMM dd, yyyy');
    } catch (error) {
      return 'Unknown date';
    }
  };

  // Page animation variants
  const pageVariants = {
    initial: { 
      opacity: 0 
    },
    animate: { 
      opacity: 1,
      transition: { 
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    initial: { 
      opacity: 0, 
      y: 20 
    },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: {
        type: "spring",
        damping: 15
      }
    }
  };

  // Get wallet for the current user
  const wallet = bridgeWallet;

  // Dashboard rendering
  if (walletLoading || txLoading) {
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
        background: '#ffffff',
        pb: 8
      }}
    >
      <Container maxWidth="lg" sx={{ pt: 3 }}>
        {/* Balance Summary */}
        <SlideRightBox variants={itemVariants}>
          <Box sx={{ mb: 5 }}>
            <Typography variant="body2" sx={{ color: '#666', fontWeight: 400, mb: 2, fontSize: '1rem' }}>
              Total Balance
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h2" component="div" fontWeight={700} sx={{ color: '#1a1a1a', fontSize: '3.5rem' }}>
                <CountUp
                  start={0}
                  end={mainBalance}
                  duration={1.5}
                  separator=","
                  decimals={2}
                  decimal="."
                  prefix={`${getCurrencySymbol(mainCurrency)}`}
                />
              </Typography>
            </Box>
          </Box>
        </SlideRightBox>

        {/* Quick Actions */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 4 }}>
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                mb: 2 
              }}
            >
              <Typography variant="h6" fontWeight="600" sx={{ color: '#1a1a1a' }}>
                Quick Actions
              </Typography>
            </Box>
            
            <Grid container spacing={2}>
              {[
                { 
                  title: 'Wallet', 
                  icon: <AccountBalanceWallet />, 
                  onClick: () => navigate('/wallet'),
                },
                { 
                  title: 'Virtual Account', 
                  icon: <AccountBalanceIcon />, 
                  onClick: () => navigate('/virtual-account'),
                },
                { 
                  title: 'Pay', 
                  icon: <SendIcon />, 
                  onClick: handleSendMoney,
                },
                { 
                  title: 'Deposit', 
                  icon: <AddIcon />, 
                  onClick: handleAddFunds,
                }
              ].map((action, index) => (
                <Grid item xs={6} sm={3} key={index}>
                  <Box 
                    sx={{ 
                      borderRadius: 3,
                      p: 3,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: '#f5f5f5',
                      border: 'none',
                      transition: 'all 0.2s ease',
                      cursor: 'pointer',
                      height: 120,
                      '&:hover': {
                        background: '#e8e8e8',
                      }
                    }}
                    onClick={action.onClick}
                  >
                    <Box 
                      sx={{ 
                        width: 56, 
                        height: 56, 
                        borderRadius: '50%', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        color: '#1976d2',
                        background: '#e3f2fd',
                        mb: 1.5
                      }}
                    >
                      {action.icon}
                    </Box>
                    <Typography variant="body2" fontWeight="500" sx={{ color: '#333' }}>
                      {action.title}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        </motion.div>

        {/* Notifications */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 4 }}>
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                mb: 2 
              }}
            >
              <Typography variant="h6" fontWeight="600" sx={{ color: '#1a1a1a' }}>
                Notifications
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ cursor: 'pointer', color: '#1976d2' }}
                onClick={() => navigate('/notifications')}
              >
                View all
              </Typography>
            </Box>
            
            <Box sx={{ 
              p: 0, 
              overflow: 'hidden',
              background: '#ffffff',
              borderRadius: 3,
              border: '1px solid #e0e0e0'
            }}>
              <List sx={{ p: 0 }}>
                <ListItem 
                  sx={{ 
                    borderBottom: '1px solid #e0e0e0', 
                    py: 2,
                    '&:hover': { background: '#f5f5f5' }
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ backgroundColor: '#1976d2' }}>
                      <AttachMoneyIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary={<Typography sx={{ color: '#1a1a1a', fontWeight: 500 }}>You sent Alex Johnson money</Typography>}
                    secondary={<Typography sx={{ color: '#666' }}>$150.00 • 2 hours ago</Typography>} 
                  />
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: '#1976d2',
                    boxShadow: '0 0 8px 0 rgba(25, 118, 210, 0.5)'
                  }} />
                </ListItem>
                
                <ListItem 
                  sx={{ 
                    borderBottom: '1px solid #e0e0e0', 
                    py: 2,
                    '&:hover': { background: '#f5f5f5' }
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ backgroundColor: '#1976d2' }}>
                      <AttachMoneyIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary={<Typography sx={{ color: '#1a1a1a', fontWeight: 500 }}>Sarah Miller sent you money</Typography>}
                    secondary={<Typography sx={{ color: '#666' }}>$75.50 • Yesterday</Typography>} 
                  />
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: '#1976d2',
                    boxShadow: '0 0 8px 0 rgba(25, 118, 210, 0.5)'
                  }} />
                </ListItem>
                
                <ListItem 
                  sx={{ 
                    py: 2,
                    '&:hover': { background: '#f5f5f5' }
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ backgroundColor: '#1976d2' }}>
                      <AttachMoneyIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary={<Typography sx={{ color: '#1a1a1a', fontWeight: 500 }}>David Williams requested money</Typography>}
                    secondary={<Typography sx={{ color: '#666' }}>$42.99 • Yesterday</Typography>} 
                  />
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: '#1976d2',
                    boxShadow: '0 0 8px 0 rgba(25, 118, 210, 0.5)'
                  }} />
                </ListItem>
              </List>
            </Box>
          </Box>
        </motion.div>

        {/* Recent Transactions */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 4 }}>
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                mb: 2 
              }}
            >
              <Typography variant="h6" fontWeight="600" sx={{ color: '#1a1a1a' }}>
                Recent Transactions
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ cursor: 'pointer', color: '#1976d2' }}
                onClick={handleHistory}
              >
                View all
              </Typography>
            </Box>
            
            <Box sx={{ 
              p: 0, 
              overflow: 'hidden',
              background: '#ffffff',
              borderRadius: 3,
              border: '1px solid #e0e0e0'
            }}>
              <List sx={{ p: 0 }}>
                <ListItem 
                  sx={{ 
                    borderBottom: '1px solid #e0e0e0', 
                    py: 2,
                    px: 3,
                    '&:hover': { background: '#f5f5f5' }
                  }}
                >
                  <ListItemIcon>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 40, height: 40, borderRadius: '50%', bgcolor: '#e3f2fd' }}>
                      <ArrowUpwardIcon sx={{ color: '#1976d2' }} />
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={<Typography sx={{ fontWeight: 500, color: '#1a1a1a' }}>Withdrawal to Bank ****4582</Typography>} 
                    secondary={<Typography sx={{ color: '#666' }}>May 10, 2023</Typography>}
                  />
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" sx={{ color: '#d32f2f', fontWeight: 600 }}>-$250.00</Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>Completed</Typography>
                  </Box>
                </ListItem>
                
                <ListItem 
                  sx={{ 
                    borderBottom: '1px solid #e0e0e0', 
                    py: 2,
                    px: 3,
                    '&:hover': { background: '#f5f5f5' }
                  }}
                >
                  <ListItemIcon>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 40, height: 40, borderRadius: '50%', bgcolor: '#e3f2fd' }}>
                      <SendIcon sx={{ color: '#1976d2' }} />
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={<Typography sx={{ fontWeight: 500, color: '#1a1a1a' }}>Sent to Alex Johnson</Typography>} 
                    secondary={<Typography sx={{ color: '#666' }}>May 9, 2023</Typography>}
                  />
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" sx={{ color: '#d32f2f', fontWeight: 600 }}>-$150.00</Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>Completed</Typography>
                  </Box>
                </ListItem>
                
                <ListItem 
                  sx={{ 
                    py: 2,
                    px: 3,
                    '&:hover': { background: '#f5f5f5' }
                  }}
                >
                  <ListItemIcon>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 40, height: 40, borderRadius: '50%', bgcolor: '#e3f2fd' }}>
                      <ReceiveIcon sx={{ color: '#1976d2' }} />
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={<Typography sx={{ fontWeight: 500, color: '#1a1a1a' }}>Deposit from Bank ****4582</Typography>} 
                    secondary={<Typography sx={{ color: '#666' }}>May 8, 2023</Typography>}
                  />
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" sx={{ color: '#2e7d32', fontWeight: 600 }}>+$500.00</Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>Completed</Typography>
                  </Box>
                </ListItem>
              </List>
            </Box>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Dashboard; 