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
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider
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
  ExpandMore as ExpandMoreIcon,
  Check as CheckIcon,
  Close as CloseIcon
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
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [accountDetailOpen, setAccountDetailOpen] = useState(false);
  const [removeDialogOpen, setRemoveDialogOpen] = useState(false);
  const [removingAccount, setRemovingAccount] = useState(false);
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
  
  const handleAccountClick = (account) => {
    setSelectedAccount(account);
    setAccountDetailOpen(true);
  };

  const handleRemoveClick = () => {
    setAccountDetailOpen(false);
    setRemoveDialogOpen(true);
  };

  const handleRemoveAccount = async () => {
    if (!selectedAccount) return;
    
    setRemovingAccount(true);
    try {
      // Delete from external accounts
      await externalAccountsAPI.deleteAccount(selectedAccount.id);
      
      // Refresh the linked accounts list
      const response = await externalAccountsAPI.getAccounts();
      setLinkedAccounts(response.data.accounts || []);
      
      setRemoveDialogOpen(false);
      setSelectedAccount(null);
    } catch (err) {
      console.error('Error removing account:', err);
      setError('Failed to remove account. Please try again.');
    } finally {
      setRemovingAccount(false);
    }
  };

  const handleSetPreferred = async () => {
    if (!selectedAccount) return;
    
    try {
      // Update the payment method to be preferred (unified endpoint)
      await externalAccountsAPI.updatePaymentMethod(selectedAccount.id, { is_preferred: true });
      
      // Refresh the linked accounts list
      const response = await externalAccountsAPI.getAccounts();
      setLinkedAccounts(response.data.accounts || []);
      
      // Update the selected account
      const updatedAccount = response.data.accounts.find(acc => acc.id === selectedAccount.id);
      if (updatedAccount) {
        setSelectedAccount(updatedAccount);
      }
    } catch (err) {
      console.error('Error setting preferred payment method:', err);
      setError('Failed to set preferred payment method. Please try again.');
    }
  };

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
        background: '#ffffff',
        pb: 8
      }}
    >
      <Container maxWidth="lg" sx={{ pt: 3 }}>
        {/* Balance Summary */}
        <SlideRightBox variants={itemVariants}>
          <Box sx={{ 
            p: 4, 
            mb: 5,
            background: '#f5f5f5',
            borderRadius: 3,
            border: 'none',
          }}>
            <Typography variant="body2" sx={{ color: '#666', fontWeight: 400, mb: 2, fontSize: '1rem' }}>
              Total Balance
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Typography variant="h2" component="div" fontWeight={700} sx={{ color: '#1a1a1a', fontSize: '3.5rem' }}>
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
            <Typography 
              variant="body2" 
              sx={{ 
                color: '#1976d2', 
                fontWeight: 500,
                display: 'flex',
                alignItems: 'center',
                gap: 0.5
              }}
            >
              Daily Rewards (~4.0% APY)
            </Typography>
          </Box>
        </SlideRightBox>

        {/* Wallet Actions */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <motion.div variants={itemVariants}>
              <Box sx={{ 
                p: 4,
                background: '#f5f5f5',
                borderRadius: 3,
                border: 'none',
              }}>
                <Typography variant="h6" fontWeight="600" sx={{ mb: 3, color: '#1a1a1a' }}>
                  Wallet Actions
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Button
                      variant="contained"
                      fullWidth
                      startIcon={<ArrowDownwardIcon />}
                      onClick={handleDeposit}
                      sx={{ 
                        py: 2, 
                        backgroundColor: '#1976d2',
                        color: '#ffffff',
                        boxShadow: 'none',
                        '&:hover': {
                          backgroundColor: '#1565c0',
                          boxShadow: 'none'
                        }
                      }}
                    >
                      Deposit
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<ArrowUpwardIcon />}
                      onClick={handleWithdraw}
                      sx={{ 
                        py: 2,
                        borderColor: '#1976d2',
                        color: '#1976d2',
                        backgroundColor: '#ffffff',
                        '&:hover': {
                          borderColor: '#1565c0',
                          backgroundColor: '#f5f5f5'
                        }
                      }}
                    >
                      Withdraw
                    </Button>
                  </Grid>
                </Grid>
              </Box>
            </motion.div>
          </Grid>
        </Grid>

        {/* Linked Accounts */}
        <motion.div variants={itemVariants}>
          <Box sx={{ 
            p: 4,
            mb: 4,
            background: '#ffffff',
            borderRadius: 3,
            border: '1px solid #e0e0e0'
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" fontWeight="600" sx={{ color: '#1a1a1a' }}>
                Linked Payment Methods
              </Typography>
              <Button
                size="small"
                startIcon={<AddIcon />}
                variant="text"
                onClick={handleAddAccount}
                sx={{ color: '#1976d2', textTransform: 'none' }}
              >
                Add
              </Button>
            </Box>
            
            <List sx={{ p: 0 }}>
              {linkedAccounts.map((account, index) => (
                <ListItem 
                  key={account.id}
                  onClick={() => handleAccountClick(account)}
                  sx={{ 
                    p: 3, 
                    mb: index < linkedAccounts.length - 1 ? 2 : 0, 
                    borderRadius: 2,
                    background: '#f5f5f5',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                      background: '#e8e8e8',
                    }
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 56, mr: 2 }}>
                    <Box sx={{ 
                      borderRadius: '50%', 
                      width: 48, 
                      height: 48, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      backgroundColor: '#e3f2fd'
                    }}>
                      <AccountBalanceIcon sx={{ color: '#1976d2', fontSize: 28 }} />
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                        <Typography variant="subtitle1" fontWeight={600} sx={{ color: '#1a1a1a' }}>
                          {account.bank_name}
                        </Typography>
                        {account.active && (
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            ml: 1.5,
                            color: '#2e7d32',
                            fontSize: '0.75rem'
                          }}>
                            <VerifiedIcon fontSize="inherit" sx={{ mr: 0.5 }} />
                            <Typography variant="caption" sx={{ color: '#2e7d32', fontWeight: 500 }}>Active</Typography>
                          </Box>
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" sx={{ color: '#666' }}>
                          ****{account.last4}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#999', mt: 0.5, display: 'block' }}>
                          {account.currency?.toUpperCase() || 'USD'}
                        </Typography>
                      </Box>
                    }
                  />
                  {account.is_preferred && (
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center',
                      ml: 2,
                      backgroundColor: '#2e7d32',
                      borderRadius: '20px',
                      px: 1.5,
                      py: 0.75,
                      gap: 0.5
                    }}>
                      <CheckIcon sx={{ color: '#ffffff', fontSize: 16 }} />
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          color: '#ffffff', 
                          fontWeight: 600,
                          letterSpacing: '0.5px',
                          fontSize: '0.7rem'
                        }}
                      >
                        PREFERRED
                      </Typography>
                    </Box>
                  )}
                </ListItem>
              ))}
            </List>
            <LinkPaymentDialog open={linkDialogOpen} onClose={()=>setLinkDialogOpen(false)} />
          </Box>
        </motion.div>

        {/* Account Detail Dialog */}
        <Dialog 
          open={accountDetailOpen} 
          onClose={() => setAccountDetailOpen(false)}
          maxWidth="sm"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: 3,
            }
          }}
        >
          {selectedAccount && (
            <>
              <DialogTitle sx={{ pb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ 
                      borderRadius: '50%', 
                      width: 56, 
                      height: 56, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      backgroundColor: '#e3f2fd',
                      mr: 2
                    }}>
                      <AccountBalanceIcon sx={{ color: '#1976d2', fontSize: 32 }} />
                    </Box>
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        {selectedAccount.bank_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        ****{selectedAccount.last4}
                      </Typography>
                    </Box>
                  </Box>
                  <IconButton 
                    onClick={() => setAccountDetailOpen(false)}
                    sx={{ 
                      color: '#666',
                      '&:hover': {
                        backgroundColor: '#f5f5f5'
                      }
                    }}
                  >
                    <CloseIcon />
                  </IconButton>
                </Box>
              </DialogTitle>
              <Divider />
              <DialogContent sx={{ py: 3 }}>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    Status
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {selectedAccount.active ? (
                      <>
                        <VerifiedIcon sx={{ color: '#2e7d32', fontSize: 20, mr: 1 }} />
                        <Typography variant="body1" fontWeight={500} sx={{ color: '#2e7d32' }}>
                          Active
                        </Typography>
                      </>
                    ) : (
                      <Typography variant="body1" fontWeight={500} color="text.secondary">
                        Inactive
                      </Typography>
                    )}
                  </Box>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    Currency
                  </Typography>
                  <Typography variant="body1" fontWeight={500}>
                    {selectedAccount.currency?.toUpperCase() || 'USD'}
                  </Typography>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    Account Type
                  </Typography>
                  <Typography variant="body1" fontWeight={500}>
                    {selectedAccount.account_type || 'Checking'}
                  </Typography>
                </Box>

                <Box>
                  {selectedAccount.is_preferred ? (
                    <>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <VerifiedIcon sx={{ color: '#2e7d32', fontSize: 20, mr: 1 }} />
                        <Typography variant="body1" fontWeight={500} sx={{ color: '#1a1a1a' }}>
                          Preferred when paying online
                        </Typography>
                      </Box>
                      <Button
                        onClick={handleSetPreferred}
                        sx={{ 
                          color: '#1976d2',
                          textTransform: 'none',
                          fontWeight: 500,
                          pl: 0,
                          '&:hover': {
                            backgroundColor: 'transparent',
                            textDecoration: 'underline'
                          }
                        }}
                      >
                        Change
                      </Button>
                    </>
                  ) : (
                    <>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Set as preferred to use this account by default.
                      </Typography>
                      <Button
                        variant="contained"
                        onClick={handleSetPreferred}
                        sx={{ 
                          backgroundColor: '#1976d2',
                          color: '#ffffff',
                          textTransform: 'none',
                          fontWeight: 500,
                          boxShadow: 'none',
                          '&:hover': {
                            backgroundColor: '#1565c0',
                            boxShadow: 'none'
                          }
                        }}
                      >
                        Set as preferred
                      </Button>
                    </>
                  )}
                </Box>
              </DialogContent>
              <Divider />
              <DialogActions sx={{ p: 3, justifyContent: 'center' }}>
                <Button 
                  onClick={handleRemoveClick}
                  sx={{ 
                    color: '#1976d2',
                    textTransform: 'none',
                    fontWeight: 500
                  }}
                >
                  Remove bank
                </Button>
              </DialogActions>
            </>
          )}
        </Dialog>

        {/* Remove Confirmation Dialog */}
        <Dialog
          open={removeDialogOpen}
          onClose={() => !removingAccount && setRemoveDialogOpen(false)}
          maxWidth="xs"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: 3,
            }
          }}
        >
          <DialogTitle sx={{ pb: 2 }}>
            Remove Bank Account?
          </DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary">
              Are you sure you want to remove {selectedAccount?.bank_name} ending in {selectedAccount?.last4}? 
              This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions sx={{ p: 3 }}>
            <Button 
              onClick={() => setRemoveDialogOpen(false)}
              disabled={removingAccount}
              sx={{ textTransform: 'none' }}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleRemoveAccount}
              disabled={removingAccount}
              variant="contained"
              sx={{ 
                textTransform: 'none',
                backgroundColor: '#d32f2f',
                '&:hover': {
                  backgroundColor: '#c62828'
                }
              }}
            >
              {removingAccount ? 'Removing...' : 'Remove'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
} 