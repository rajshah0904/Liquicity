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
import CreditCardIcon from '@mui/icons-material/CreditCard';
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
import { useAuth0 } from '@auth0/auth0-react';
import NotificationCenter from '../components/NotificationCenter';
import RefreshIcon from '@mui/icons-material/Refresh';

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
  const [wallets, setWallets] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
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

  // Fetch user data
  useEffect(() => {
    setLoading(true);
    setError(null);

    const fetchData = async () => {
      try {
        // Fetch wallet overview
        const walletResp = await walletAPI.getOverview();
        setWallets(walletResp.data.wallets || []);
        // Main balance: sum of local balances
        const totalLocal = (walletResp.data.wallets || []).reduce((acc,w)=>acc + (w.local_balance||0),0);
        setMainBalance(totalLocal);
        setMainCurrency(walletResp.data.wallets[0]?.local_currency?.toUpperCase() || 'USD');

        // Fetch transactions
        const historyResp = await walletAPI.getAllTransactions();
        const txns = historyResp.data.transactions || [];
        setTransactions(txns);
        const sorted = [...txns].sort((a,b)=> new Date(b.date)- new Date(a.date)).slice(0,5);
        setRecentTransactions(sorted);
        const pendingAmount = txns.filter(tx=> tx.state==='pending').reduce((s,tx)=> s+Number(tx.amount||0),0);
        setPending(pendingAmount);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Unable to load your data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

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
  const wallet = wallets.length > 0 ? wallets[0] : null;

  // Dashboard rendering
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
              Dashboard
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
                    end={mainBalance}
                    duration={1.5}
                    separator=","
                    decimals={2}
                    decimal="."
                    prefix={mainCurrency === 'USD' ? '$' : (mainCurrency === 'EUR' ? '€' : '')}
                  />
                </Typography>
              </Box>
            </Box>
          </FloatingCard>
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
              <Typography variant="h6" fontWeight="600">
                Quick Actions
              </Typography>
            </Box>
            
            <Grid container spacing={2}>
              {[
                { 
                  title: 'Deposit', 
                  icon: <AddIcon />, 
                  color: '#3b82f6', 
                  onClick: handleAddFunds,
                  bgColor: 'rgba(59, 130, 246, 0.1)'
                },
                { 
                  title: 'Withdraw', 
                  icon: <ArrowUpwardIcon />, 
                  color: '#10b981', 
                  onClick: handleWithdraw,
                  bgColor: 'rgba(16, 185, 129, 0.1)'
                },
                { 
                  title: 'Send', 
                  icon: <SendIcon />, 
                  color: '#8b5cf6', 
                  onClick: handleSendMoney,
                  bgColor: 'rgba(139, 92, 246, 0.1)'
                },
                { 
                  title: 'Card', 
                  icon: <CreditCardIcon />, 
                  color: '#f59e0b', 
                  onClick: () => navigate('/card'),
                  bgColor: 'rgba(245, 158, 11, 0.1)'
                }
              ].map((action, index) => (
                <Grid item xs={6} sm={3} key={index}>
                  <Box 
                    sx={{ 
                      borderRadius: 2,
                      p: 2,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: 'rgba(17, 24, 39, 0.5)',
                      border: '1px solid rgba(55, 65, 81, 0.5)',
                      transition: 'all 0.3s ease',
                      cursor: 'pointer',
                      height: 100,
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: `0 4px 20px rgba(0, 0, 0, 0.1)`,
                        borderColor: `${action.color}80`,
                        background: 'rgba(17, 24, 39, 0.7)',
                      }
                    }}
                    onClick={action.onClick}
                  >
                    <Box 
                      sx={{ 
                        width: 50, 
                        height: 50, 
                        borderRadius: '50%', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        color: action.color,
                        background: action.bgColor,
                        mb: 1
                      }}
                    >
                      {action.icon}
                    </Box>
                    <Typography variant="body2" fontWeight="600">
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
              <Typography variant="h6" fontWeight="600">
                Notifications
              </Typography>
              <Typography 
                variant="body2" 
                color="primary" 
                sx={{ cursor: 'pointer' }}
                onClick={() => navigate('/notifications')}
              >
                View all
              </Typography>
            </Box>
            
            <FloatingCard sx={{ 
              p: 0, 
              overflow: 'hidden',
              background: 'rgba(17, 24, 39, 0.7)',
              borderColor: 'rgba(59, 130, 246, 0.1)'
            }}>
              <List sx={{ p: 0 }}>
                <ListItem 
                  sx={{ 
                    borderBottom: '1px solid rgba(55, 65, 81, 0.2)', 
                    py: 2,
                    '&:hover': { background: 'rgba(59, 130, 246, 0.05)' }
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ backgroundColor: '#8b5cf6' }}>
                      <AttachMoneyIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary="You sent Alex Johnson money" 
                    secondary={<>$150.00 • 2 hours ago</>} 
                  />
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    boxShadow: '0 0 8px 0 rgba(59, 130, 246, 0.8)'
                  }} />
                </ListItem>
                
                <ListItem 
                  sx={{ 
                    borderBottom: '1px solid rgba(55, 65, 81, 0.2)', 
                    py: 2,
                    '&:hover': { background: 'rgba(59, 130, 246, 0.05)' }
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ backgroundColor: '#10b981' }}>
                      <AttachMoneyIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary="Sarah Miller sent you money" 
                    secondary={<>$75.50 • Yesterday</>} 
                  />
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    boxShadow: '0 0 8px 0 rgba(59, 130, 246, 0.8)'
                  }} />
                </ListItem>
                
                <ListItem 
                  sx={{ 
                    py: 2,
                    '&:hover': { background: 'rgba(59, 130, 246, 0.05)' }
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ backgroundColor: '#f59e0b' }}>
                      <AttachMoneyIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary="David Williams requested money" 
                    secondary={<>$42.99 • Yesterday</>} 
                  />
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    boxShadow: '0 0 8px 0 rgba(59, 130, 246, 0.8)'
                  }} />
                </ListItem>
              </List>
            </FloatingCard>
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
              <Typography variant="h6" fontWeight="600">
                Recent Transactions
              </Typography>
              <Typography 
                variant="body2" 
                color="primary" 
                sx={{ cursor: 'pointer' }}
                onClick={handleHistory}
              >
                View all
              </Typography>
            </Box>
            
            <FloatingCard sx={{ 
              p: 0, 
              overflow: 'hidden',
              background: 'rgba(17, 24, 39, 0.7)',
              borderColor: 'rgba(59, 130, 246, 0.1)'
            }}>
              <List sx={{ p: 0 }}>
                <ListItem 
                  sx={{ 
                    borderBottom: '1px solid rgba(55, 65, 81, 0.2)', 
                    py: 2,
                    '&:hover': { background: 'rgba(59, 130, 246, 0.05)' }
                  }}
                >
                  <ListItemIcon>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 40, height: 40, borderRadius: '50%', bgcolor: 'rgba(59, 130, 246, 0.1)' }}>
                      <ArrowUpwardIcon color="error" />
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={<Box component="span" sx={{ fontWeight: 500 }}>Withdrawal to Bank ****4582</Box>} 
                    secondary={<>May 10, 2023</>}
                  />
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" color="error.main" fontWeight="600">-$250.00</Typography>
                    <Typography variant="caption" color="text.secondary">Completed</Typography>
                  </Box>
                </ListItem>
                
                <ListItem 
                  sx={{ 
                    borderBottom: '1px solid rgba(55, 65, 81, 0.2)', 
                    py: 2,
                    '&:hover': { background: 'rgba(59, 130, 246, 0.05)' }
                  }}
                >
                  <ListItemIcon>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 40, height: 40, borderRadius: '50%', bgcolor: 'rgba(139, 92, 246, 0.1)' }}>
                      <SendIcon color="error" />
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={<Box component="span" sx={{ fontWeight: 500 }}>Sent to Alex Johnson</Box>} 
                    secondary={<>May 9, 2023</>}
                  />
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" color="error.main" fontWeight="600">-$150.00</Typography>
                    <Typography variant="caption" color="text.secondary">Completed</Typography>
                  </Box>
                </ListItem>
                
                <ListItem 
                  sx={{ 
                    py: 2,
                    '&:hover': { background: 'rgba(59, 130, 246, 0.05)' }
                  }}
                >
                  <ListItemIcon>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 40, height: 40, borderRadius: '50%', bgcolor: 'rgba(16, 185, 129, 0.1)' }}>
                      <ReceiveIcon color="success" />
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={<Box component="span" sx={{ fontWeight: 500 }}>Deposit from Bank ****4582</Box>} 
                    secondary={<>May 8, 2023</>}
                  />
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" color="success.main" fontWeight="600">+$500.00</Typography>
                    <Typography variant="caption" color="text.secondary">Completed</Typography>
                  </Box>
                </ListItem>
              </List>
            </FloatingCard>
          </Box>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Dashboard; 