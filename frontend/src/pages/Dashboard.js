import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Paper,
  CircularProgress,
  Alert,
  Button, 
  Card, 
  CardContent, 
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
import api from '../utils/api';
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

// Import our custom UI components
import {
  FloatingCard as GlassCard,
  NeonButton as GradientButton,
  NeonButton as SecondaryGradientButton,
  GradientBorder as BorderGradientCard,
  GradientDivider,
  GradientChip,
  GlassIconButton,
  GradientText,
  AnimatedBackground as GradientBackground,
  FuturisticAvatar as GradientBorderAvatar,
  GlassContainer as FrostedGlassContainer,
  Box as DashboardContainer
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
        const userId = user?.id || localStorage.getItem('userId') || 1;
        console.log("Dashboard: Fetching data for user ID:", userId);
        
        // Fetch wallet data
        const walletResponse = await api.get(`/wallet/${userId}`);
        if (walletResponse.status === 200) {
          setWallets([walletResponse.data]);
          
          // Set main balance and currency from wallet data
          const walletData = walletResponse.data;
          setMainBalance(walletData?.fiat_balance || 0);
          setMainCurrency(walletData?.base_currency || 'USD');
          setStablecoinBalance(walletData?.stablecoin_balance || 0);
        }

        // Fetch transaction history
        const historyResponse = await api.get(`/transaction/user/${userId}`);
        if (historyResponse.status === 200) {
          setTransactions(historyResponse.data);
          
          // Set recent transactions (latest 5)
          const sortedTransactions = historyResponse.data
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, 5);
          setRecentTransactions(sortedTransactions);
          
          // Calculate pending amount
          const pendingAmount = historyResponse.data
            .filter(tx => tx.status === 'pending')
            .reduce((sum, tx) => {
              // If user is recipient, add to pending
              if (tx.recipient_id === userId) {
                return sum + (tx.target_amount || 0);
              }
              return sum;
            }, 0);
          setPending(pendingAmount);
        }
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
  const handleSendMoney = () => navigate('/send');
  const handleReceiveMoney = () => navigate('/receive');
  const handleAddFunds = () => navigate('/deposit');
  const handleWithdraw = () => navigate('/withdraw');
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="70vh">
        <ScaleUpBox>
          <CircularProgress color="primary" size={60} thickness={4} />
        </ScaleUpBox>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ px: { xs: 2, md: 3 } }}>
      {error && (
        <SlideUpBox>
          <Alert severity="error" sx={{ 
            mb: 2, 
            borderRadius: 2,
            backgroundColor: `rgba(${theme.palette.error.main}, 0.1)`,
            backdropFilter: 'blur(10px)'
          }}>
            {error}
          </Alert>
        </SlideUpBox>
      )}
      
      {/* Welcome Section - reduced vertical spacing */}
      <SlideUpBox>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom fontWeight="700">
            Welcome back, <GradientText>{user?.profile?.first_name || user?.username || 'User'}</GradientText>
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Here's an overview of your finances
          </Typography>
        </Box>
      </SlideUpBox>
      
      {/* Main Balance and Quick Actions - reduced spacing */}
      <Grid 
        container 
        spacing={2} 
        sx={{ mb: 3 }}
      >
        {/* Balance Card */}
        <Grid item xs={12} md={6}>
          <Box sx={{ 
            p: { xs: 2, md: 3 },
            background: (theme) => theme.palette.background.paper,
            borderRadius: 2,
            border: (theme) => `1px solid ${theme.palette.divider}`,
            boxShadow: 'none',
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
              <Typography variant="h6" component="div" fontWeight="600" sx={{ color: 'text.primary' }}>
                Your Balance
              </Typography>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="h3" component="div" sx={{ fontWeight: 'bold', my: 1, color: 'text.primary' }}>
                <CountUp 
                  end={parseFloat(mainBalance)} 
                  prefix={mainCurrency === 'USD' ? '$' : ''} 
                  suffix={mainCurrency !== 'USD' ? ` ${mainCurrency}` : ''}
                  decimals={2}
                  duration={1}
                  separator=","
                />
              </Typography>
              
              {pending > 0 && (
                <Box sx={{ 
                  display: 'inline-block', 
                  px: 1.5, 
                  py: 0.5, 
                  borderRadius: 0, 
                  background: (theme) => alpha(theme.palette.warning.main, 0.1), 
                  border: (theme) => `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
                  mt: 1
                }}>
                  <Typography variant="caption" sx={{ color: 'text.primary', fontWeight: 500 }}>
                    {formatCurrency(pending, mainCurrency)} pending
                  </Typography>
                </Box>
              )}
            </Box>
            
            <Box sx={{ 
              height: '1px', 
              width: '100%', 
              background: (theme) => theme.palette.divider,
              my: 2
            }} />
            
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button 
                variant="contained"
                onClick={handleSendMoney}
                sx={{ 
                  flex: 1, 
                  py: 1.5, 
                  color: (theme) => theme.palette.mode === 'dark' ? '#000000' : '#FFFFFF',
                  fontWeight: 'bold',
                  background: (theme) => theme.palette.primary.main,
                  borderRadius: 0,
                  '&:hover': {
                    background: (theme) => theme.palette.primary.dark,
                  }
                }}
              >
                <Typography fontSize="1.2rem" sx={{ mr: 1, color: 'inherit' }}>→</Typography>
                Send
              </Button>
              <Button 
                variant="outlined" 
                onClick={handleReceiveMoney}
                sx={{ 
                  flex: 1, 
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
                <Typography fontSize="1.2rem" sx={{ mr: 1, color: 'inherit' }}>←</Typography>
                Receive
              </Button>
            </Box>
          </Box>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Box sx={{ 
            p: { xs: 2, md: 3 },
            background: (theme) => theme.palette.background.paper,
            borderRadius: 2,
            border: (theme) => `1px solid ${theme.palette.divider}`,
            boxShadow: 'none',
            height: '100%',
          }}>
            <Typography variant="h6" component="div" sx={{ color: 'text.primary' }} fontWeight="600" gutterBottom>
              Quick Actions
            </Typography>
            
            <Grid container spacing={2} sx={{ mt: 0 }}>
              <Grid item xs={6}>
                <Box sx={{ 
                  p: 2, 
                  height: '100%', 
                  cursor: 'pointer',
                  bgcolor: 'background.paper',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease-in-out',
                  borderRadius: 0,
                  border: (theme) => `1px solid ${theme.palette.divider}`,
                  '&:hover': {
                    borderColor: 'primary.main',
                    background: (theme) => alpha(theme.palette.primary.main, 0.03),
                  }
                }}
                  onClick={handleAddFunds}
                >
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography sx={{ 
                      fontSize: '2rem', 
                      mb: 1,
                      color: 'primary.main'
                    }}>
                      +
                    </Typography>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'text.primary' }}>
                      Add Funds
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      Deposit to wallet
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ 
                  p: 2, 
                  height: '100%', 
                  cursor: 'pointer',
                  bgcolor: 'background.paper',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease-in-out',
                  borderRadius: 0,
                  border: (theme) => `1px solid ${theme.palette.divider}`,
                  '&:hover': {
                    borderColor: 'primary.main',
                    background: (theme) => alpha(theme.palette.primary.main, 0.03),
                  }
                }}
                  onClick={handleWithdraw}
                >
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography sx={{ 
                      fontSize: '2rem', 
                      mb: 1,
                      color: 'primary.main'
                    }}>
                      ↓
                    </Typography>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'text.primary' }}>
                      Withdraw Funds
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      Withdraw to bank
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ 
                  p: 2, 
                  height: '100%', 
                  cursor: 'pointer',
                  bgcolor: 'background.paper',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease-in-out',
                  borderRadius: 0,
                  border: (theme) => `1px solid ${theme.palette.divider}`,
                  '&:hover': {
                    borderColor: 'primary.main',
                    background: (theme) => alpha(theme.palette.primary.main, 0.03),
                  }
                }}
                  onClick={() => navigate('/receive')}
                >
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography sx={{ 
                      fontSize: '2rem', 
                      mb: 1,
                      color: 'primary.main'
                    }}>
                      ←
                    </Typography>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'text.primary' }}>
                      Request
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      Request payment
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ 
                  p: 2, 
                  height: '100%', 
                  cursor: 'pointer',
                  bgcolor: 'background.paper',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease-in-out',
                  borderRadius: 0,
                  border: (theme) => `1px solid ${theme.palette.divider}`,
                  '&:hover': {
                    borderColor: 'primary.main',
                    background: (theme) => alpha(theme.palette.primary.main, 0.03),
                  }
                }}
                  onClick={() => navigate('/transactions')}
                >
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography sx={{ 
                      fontSize: '2rem', 
                      mb: 1,
                      color: 'primary.main'
                    }}>
                      🔍
                    </Typography>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'text.primary' }}>
                      Transactions
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      View all activity
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </Grid>
        </Grid>

      {/* Recent Transactions Section - reduced spacing */}
      <Grid 
        container 
        spacing={2}
      >
        <Grid item xs={12}>
          <Box sx={{ 
            p: { xs: 2, md: 3 },
            borderRadius: 2,
            background: (theme) => theme.palette.background.paper,
            boxShadow: 'none',
            border: (theme) => `1px solid ${theme.palette.divider}`,
          }}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h5" component="h2" gutterBottom fontWeight="600" sx={{ color: 'text.primary' }}>
                Recent Activity
              </Typography>
            </Box>
            
            {recentTransactions.length > 0 ? (
              <List sx={{ p: 0 }}>
                {recentTransactions.map((transaction, index) => {
                  // Determine transaction type and direction for display
                  const isIncoming = transaction.recipient_id === user?.id;
                  const transactionType = transaction.transaction_type || 
                    (isIncoming ? 'RECEIVE' : 'SEND');
                  
                  return (
                    <ListItem
                      key={transaction.id || index}
                      sx={{
                        borderBottom: (theme) => index < recentTransactions.length - 1 ? `1px solid ${theme.palette.divider}` : 'none',
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
                            color={(theme) => isIncoming ? theme.palette.success.main : theme.palette.error.main}
                          >
                            {isIncoming ? '+' : '-'}
                            {formatCurrency(
                              isIncoming ? transaction.target_amount : transaction.source_amount, 
                              isIncoming ? transaction.target_currency : transaction.source_currency || mainCurrency
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
                          <Typography fontSize="1.2rem" sx={{ color: (theme) => isIncoming ? theme.palette.success.main : theme.palette.error.main }}>
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
            
            {recentTransactions.length > 0 && (
              <Box sx={{ p: 1, textAlign: 'center' }}>
                <Button 
                  endIcon={<KeyboardArrowRightIcon />}
                  onClick={() => navigate('/transactions')}
                  sx={{ 
                    borderRadius: 0,
                    textTransform: 'none',
                    fontWeight: 'bold',
                    color: 'primary.main',
                    borderColor: 'primary.main',
                    border: '1px solid',
                    '&:hover': {
                      borderColor: 'primary.dark',
                      background: (theme) => alpha(theme.palette.primary.main, 0.05)
                    }
                  }}
                >
                  View All Transactions
                </Button>
              </Box>
            )}
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 