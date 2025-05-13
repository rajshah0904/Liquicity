import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Alert, 
  CircularProgress,
  Container,
  Avatar,
  Grid,
  InputAdornment,
  IconButton,
  Chip,
  Divider,
  MenuItem,
  FormControlLabel,
  RadioGroup,
  Radio,
  useTheme,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText
} from '@mui/material';
import { transferAPI, walletAPI, authAPI } from '../../utils/api';
import { motion } from 'framer-motion';
import { Search as SearchIcon, QrCode as QrCodeIcon, Add as AddIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { AnimatedBackground } from '../../components/ui/ModernUIComponents';
import { format } from 'date-fns';
import CountUp from 'react-countup';
import { useAuth0 } from '@auth0/auth0-react';
import { getCurrencySymbol, formatCurrency } from '../../utils/currencyUtils';
import { 
  STANDARD_DEPOSIT_FEE_RATE, 
  STANDARD_SEND_FEE_RATE,
  INSTANT_DEPOSIT_FEE_RATE,
  EXPRESS_ALL_IN_FEE_RATE,
  UI_STANDARD_ALL_IN_FEE,
  UI_EXPRESS_ALL_IN_FEE,
  UI_STANDARD_SEND_FEE,
  UI_INSTANT_DEPOSIT_FEE,
  calculateFee,
  calculateTotalWithFee
} from '../../utils/feeConstants';

// Mock data for recipients and transactions
const mockRecipients = [
  { id: 1, name: 'Sarah', avatar: '/avatars/avatar1.jpg' },
  { id: 2, name: 'Michael', avatar: '/avatars/avatar2.jpg' },
  { id: 3, name: 'Emma', avatar: '/avatars/avatar3.jpg' },
  { id: 4, name: 'Alex', avatar: '/avatars/avatar4.jpg' }
];

const mockTransactions = [
  { 
    id: 1, 
    recipient: { id: 1, name: 'Sarah Johnson', avatar: '/avatars/avatar1.jpg' },
    date: new Date('2025-05-10'),
    amount: -75.00,
    type: 'sent'
  },
  { 
    id: 2, 
    recipient: { id: 2, name: 'Michael Chen', avatar: '/avatars/avatar2.jpg' },
    date: new Date('2025-05-08'),
    amount: 120.00,
    type: 'received'
  },
  { 
    id: 3, 
    recipient: { id: 3, name: 'Emma Wilson', avatar: '/avatars/avatar3.jpg' },
    date: new Date('2025-05-05'),
    amount: -42.50,
    type: 'sent'
  }
];

export default function Send() {
  const theme = useTheme();
  const [step, setStep] = useState('initial'); // initial, confirm, success
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const { user } = useAuth0();
  
  const [balanceData, setBalanceData] = useState({
    total: 0,
    available: 0,
    currency: 'USD'
  });
  
  // Form state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [allUsers, setAllUsers] = useState([]);
  const [recipient, setRecipient] = useState(null);
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  const [speedOption, setSpeedOption] = useState('standard'); // 'standard' or 'express'
  const [bankAccounts, setBankAccounts] = useState([
    { id: 'ext-001', name: 'Chase Bank', accountNumber: '****4582', status: 'verified' },
    { id: 'ext-002', name: 'Bank of America', accountNumber: '****7891', status: 'verified' }
  ]);
  const [selectedBankAccount, setSelectedBankAccount] = useState('');
  
  // Updated fee structure based on new requirements
  // P2P Send fee: 0.50%
  const balanceFee = amount ? calculateFee(parseFloat(amount), STANDARD_SEND_FEE_RATE) : 0;
  const bankFee = amount ? calculateFee(parseFloat(amount), EXPRESS_ALL_IN_FEE_RATE) : 0;
  
  const amountFromBalance = () => {
    if (!amount) return 0;
    const amountNum = parseFloat(amount);
    if (speedOption === 'standard') {
      return amountNum;
    } else if (speedOption === 'express') {
      return Math.min(amountNum, balanceData.available);
    }
    return 0;
  };
  
  const amountFromBank = () => {
    if (!amount) return 0;
    const amountNum = parseFloat(amount);
    if (speedOption === 'express') {
      return amountNum;
    } else if (speedOption === 'standard') {
      return Math.max(0, amountNum - balanceData.available);
    }
    return 0;
  };
  
  const totalFee = () => {
    const balanceAmount = amountFromBalance();
    const bankAmount = amountFromBank();
    return calculateFee(balanceAmount, STANDARD_SEND_FEE_RATE) + calculateFee(bankAmount, EXPRESS_ALL_IN_FEE_RATE);
  };
  
  const totalAmount = () => {
    if (!amount) return 0;
    return parseFloat(amount) + totalFee();
  };
  
  useEffect(() => {
    // Auto-select payment method based on balance vs amount
    if (amount && parseFloat(amount) > 0) {
      if (parseFloat(amount) <= balanceData.available) {
        setSpeedOption('standard');
      } else if (balanceData.available > 0) {
        setSpeedOption('express');
      } else {
        setSpeedOption('express');
      }
    }
  }, [amount, balanceData.available]);
  
  // Fetch wallet data
  const fetchWalletData = async () => {
    try {
      const resp = await walletAPI.getOverview();
      if (resp.data && resp.data.wallets && resp.data.wallets.length > 0) {
        // Get the primary wallet (USD for most users, EUR for Hadeer)
        if (user && user.email === 'hadeermotair@gmail.com') {
          const eurWallet = resp.data.wallets.find(w => w.currency === 'eur') || resp.data.wallets[0];
          setBalanceData({
            total: eurWallet.balance || 0,
            available: eurWallet.balance || 0,
            currency: 'EUR'
          });
        } else {
          // Find USD wallet
          const usdWallet = resp.data.wallets.find(w => w.currency === 'usd') || resp.data.wallets[0];
          
          setBalanceData({
            total: usdWallet.balance || 0,
            available: usdWallet.balance || 0,
            currency: usdWallet.currency?.toUpperCase() || 'USD'
          });
        }
      }
    } catch (err) {
      console.error('Failed to fetch wallet data', err);
    }
  };
  
  useEffect(() => {
    fetchWalletData();
    
    // Fetch all users for the dropdown
    const fetchAllUsers = async () => {
      try {
        const resp = await authAPI.searchUsers('');  // Empty string to get all users
        
        // Ensure Hadeer is in the list
        let users = resp.data.users || [];
        
        // Check if Hadeer is already in the list
        const hadeerExists = users.some(user => user.email === 'hadeermotair@gmail.com');
        
        // Force add Hadeer if not present
        if (!hadeerExists) {
          users = [
            {
              id: 'user-hadeer',
              email: 'hadeermotair@gmail.com',
              name: 'Hadeer Motair',
              has_wallet: true
            },
            ...users
          ];
        }
        
        // Filter out any demo users with @demo.com emails if they exist
        users = users.filter(user => !user.email.includes('@demo.com'));
        
        setAllUsers(users);
      } catch (err) {
        console.error('Failed to fetch users', err);
        
        // Fallback with hardcoded users including Hadeer
        setAllUsers([
          {
            id: 'user-1',
            email: 'hadeermotair@gmail.com',
            name: 'Hadeer Motair',
            has_wallet: true
          },
          {
            id: 'user-2',
            email: 'user@example.com',
            name: 'Example User',
            has_wallet: true
          },
          {
            id: 'user-3',
            email: 'rajshah11@gmail.com',
            name: 'Raj Shah',
            has_wallet: true
          }
        ]);
      }
    };
    
    fetchAllUsers();
    
    // Refresh data every 30 seconds
    const intervalId = setInterval(fetchWalletData, 30000);
    
    return () => clearInterval(intervalId);
  }, [user]);
  
  const handleSearch = async (e) => {
    setSearchQuery(e.target.value);
    setSearching(true);
    try {
      const resp = await authAPI.searchUsers(e.target.value);
      setSearchResults(resp.data.users);
    } catch (err) {
      console.error('Failed to search users', err);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };
  
  const selectRecipient = (person) => {
    console.log('Selecting recipient:', person);
    
    // Make sure person has all required fields
    if (!person) return;
    
    // For Hadeer, ensure user ID is properly formatted
    if (person.email === 'hadeermotair@gmail.com' && person.id !== 'user-1') {
      person.id = 'user-1'; // Normalize ID to match MockDataProvider expectations
    }
    
    // Set recipient state
    setRecipient(person);
    
    // Set the search query to show who was selected
    setSearchQuery(person.name);
    
    // Stay on initial step
    setStep('initial');
    
    // Close the dropdown
    setShowUserDropdown(false);
  };
  
  const handleAmountChange = (e) => {
    // Only allow numeric input with decimal
    const value = e.target.value;
    if (value === '' || /^\d*\.?\d{0,2}$/.test(value)) {
      setAmount(value);
    }
  };
  
  const handleNoteChange = (e) => {
    setNote(e.target.value);
  };
  
  const handleSpeedOptionChange = (e) => {
    setSpeedOption(e.target.value);
  };
  
  const handleBankAccountChange = (e) => {
    setSelectedBankAccount(e.target.value);
  };
  
  const handleSubmit = async () => {
    if (!recipient || !amount || parseFloat(amount) <= 0) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Prepare payload based on payment method
      const payload = {
        recipient_user_id: recipient.id,
        amount: amount,
        memo: note || undefined,
        speed_option: speedOption
      };
      
      // Determine if we need to split the transaction (part from wallet, part from bank)
      const amountNum = parseFloat(amount);
      const hasInsufficientFunds = amountNum > balanceData.available;
      
      // If insufficient funds, add external account info
      if (hasInsufficientFunds) {
        if (selectedBankAccount) {
          payload.external_account_id = selectedBankAccount;
        } else if (bankAccounts.length > 0) {
          payload.external_account_id = bankAccounts[0].id;
        }
        
        // Include how much should come from wallet vs bank
        payload.amount_from_wallet = balanceData.available;
        payload.amount_from_bank = amountNum - balanceData.available;
      }
      
      const resp = await transferAPI.send(payload);
      setSuccess(resp.data);
      
      // Refresh wallet data to get updated balance
      fetchWalletData();
      
      setStep('success');
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err.message || 'Send failed');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCancel = () => {
    if (step === 'confirm') {
      setStep('initial');
    } else {
      // Reset all fields
      setRecipient(null);
      setAmount('');
      setNote('');
      setSpeedOption('standard');
      setSelectedBankAccount('');
      setStep('initial');
    }
  };
  
  const handleContinue = () => {
    if (step === 'initial') {
      setStep('confirm');
    } else if (step === 'confirm') {
      handleSubmit();
    } else {
      // Reset and go back to initial state
      handleCancel();
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

  const renderInitialScreen = () => (
    <>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="600" color="#fff">
          Send Money
        </Typography>
      </Box>
      
      {/* Recipient section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Recipient
        </Typography>
        
        <Box sx={{ position: 'relative' }}>
          <TextField
            fullWidth
            placeholder="Search or enter address"
            value={searchQuery}
            onChange={handleSearch}
            onFocus={() => setShowUserDropdown(true)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  {searching ? (
                    <CircularProgress size={20} />
                  ) : (
                    <Box sx={{ display: 'flex' }}>
                      <IconButton 
                        sx={{ color: 'primary.main' }}
                        onClick={() => setShowUserDropdown(!showUserDropdown)}
                      >
                        <KeyboardArrowDownIcon />
                      </IconButton>
                      <IconButton sx={{ color: 'primary.main' }}>
                        <QrCodeIcon />
                      </IconButton>
                    </Box>
                  )}
                </InputAdornment>
              ),
              sx: {
                borderRadius: '12px',
                bgcolor: 'rgba(17, 25, 40, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#fff',
                '& .MuiOutlinedInput-notchedOutline': {
                  border: 'none'
                }
              }
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  border: 'none'
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  border: 'none'
                }
              }
            }}
          />
          
          {/* User Dropdown */}
          {showUserDropdown && allUsers.length > 0 && (
            <Box sx={{ 
              position: 'absolute', 
              top: '100%', 
              left: 0, 
              right: 0, 
              zIndex: 10, 
              mt: 1, 
              bgcolor: 'rgba(17, 25, 40, 0.95)',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
              maxHeight: '300px',
              overflowY: 'auto'
            }}>
              <List sx={{ p: 1 }}>
                <ListItem sx={{ p: 1.5, justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                  <Typography variant="body2" fontWeight="500" color="text.primary">All Users</Typography>
                  <IconButton size="small" onClick={() => setShowUserDropdown(false)}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </IconButton>
                </ListItem>
                
                {allUsers.map((user) => (
                  <ListItem 
                    key={user.id}
                    button
                    sx={{ 
                      borderRadius: '8px',
                      mb: 0.5,
                      '&:hover': {
                        bgcolor: 'rgba(59, 130, 246, 0.1)'
                      },
                      cursor: 'pointer'
                    }}
                    onClick={() => {
                      console.log("User selected:", user); // Debug log
                      selectRecipient({
                        id: user.id,
                        name: user.name,
                        email: user.email,
                        avatar: null // Use default avatar if none
                      });
                      setSearchQuery(user.name); // Set search query to user name for display
                      setSearchResults([]); // Clear results
                      setShowUserDropdown(false); // Hide dropdown
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.dark' }}>
                        {user.name[0].toUpperCase()}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText 
                      primary={user.name} 
                      secondary={user.email}
                      primaryTypographyProps={{ color: 'text.primary' }}
                      secondaryTypographyProps={{ color: 'text.secondary', fontSize: '0.75rem' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
          
          {/* Search Results Dropdown */}
          {searchQuery && searchResults.length > 0 && (
            <Box sx={{ 
              position: 'absolute', 
              top: '100%', 
              left: 0, 
              right: 0, 
              zIndex: 10, 
              mt: 1, 
              bgcolor: 'rgba(17, 25, 40, 0.95)',
              borderRadius: '12px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
              maxHeight: '300px',
              overflowY: 'auto'
            }}>
              <List sx={{ p: 1 }}>
                {searchResults.map((user) => (
                  <ListItem 
                    key={user.id}
                    button
                    onClick={() => {
                      selectRecipient({
                        id: user.id,
                        name: user.name,
                        email: user.email,
                        avatar: null // Use default avatar if none
                      });
                      setSearchQuery(''); // Clear search when selected
                      setSearchResults([]); // Clear results
                    }}
                    sx={{ 
                      borderRadius: '8px',
                      mb: 0.5,
                      '&:hover': {
                        bgcolor: 'rgba(59, 130, 246, 0.1)'
                      }
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.dark' }}>
                        {user.name[0].toUpperCase()}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText 
                      primary={user.name} 
                      secondary={user.email}
                      primaryTypographyProps={{ color: 'text.primary' }}
                      secondaryTypographyProps={{ color: 'text.secondary', fontSize: '0.75rem' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
        
        {/* Recent Recipients */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Recent Recipients
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {mockRecipients.map((person) => (
              <Box
                key={person.id}
                sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  cursor: 'pointer',
                  opacity: recipient && recipient.id === person.id ? 1 : 0.8,
                  transition: 'all 0.2s',
                  '&:hover': {
                    opacity: 1,
                  }
                }}
                onClick={() => selectRecipient(person)}
              >
                <Avatar 
                  src={person.avatar} 
                  alt={person.name} 
                  sx={{ 
                    width: 60, 
                    height: 60, 
                    mb: 1,
                    border: recipient && recipient.id === person.id 
                      ? '2px solid #3b82f6' 
                      : '2px solid transparent'
                  }}
                />
                <Typography 
                  variant="caption" 
                  color={recipient && recipient.id === person.id ? 'primary' : 'text.secondary'}
                >
                  {person.name}
                </Typography>
              </Box>
            ))}
            <Box
              sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center',
                cursor: 'pointer',
                opacity: 0.8,
                transition: 'all 0.2s',
                '&:hover': {
                  opacity: 1,
                }
              }}
            >
              <Avatar 
                sx={{ 
                  width: 60, 
                  height: 60, 
                  mb: 1, 
                  bgcolor: 'rgba(59, 130, 246, 0.2)'
                }}
              >
                <AddIcon sx={{ color: theme.palette.primary.main }} />
              </Avatar>
              <Typography variant="caption" color="text.secondary">
                New
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>
      
      {/* Amount section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Amount
        </Typography>
        
        <Box sx={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h5" color="text.secondary" sx={{ ml: 1 }}>
            {getCurrencySymbol(balanceData.currency, user)}
          </Typography>
          <TextField
            fullWidth
            placeholder="0.00"
            value={amount}
            onChange={handleAmountChange}
            InputProps={{
              disableUnderline: true,
              sx: {
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: '#fff',
                input: { 
                  padding: '0.5rem 0',
                  '&::placeholder': {
                    color: 'rgba(255, 255, 255, 0.3)',
                    opacity: 1
                  },
                }
              }
            }}
            variant="standard"
            sx={{
              '& .MuiInput-root': {
                borderBottom: 'none',
                '&:before, &:after': {
                  display: 'none'
                }
              }
            }}
          />
          <Box 
            sx={{ 
              border: '1px solid rgba(255, 255, 255, 0.1)',
              px: 1.5,
              py: 0.5,
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer',
              bgcolor: 'rgba(17, 25, 40, 0.7)',
            }}
          >
            <Typography variant="body2" color="text.primary" mr={0.5}>
              {user && user.email === 'hadeermotair@gmail.com' ? 'EUR' : balanceData.currency}
            </Typography>
            <KeyboardArrowDownIcon fontSize="small" sx={{ color: 'text.secondary' }} />
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1, px: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Available: {getCurrencySymbol(balanceData.currency, user)}{balanceData.available.toLocaleString()}
          </Typography>
          <Typography 
            variant="caption" 
            color="primary.main" 
            sx={{ cursor: 'pointer' }}
            onClick={() => setAmount(balanceData.available.toString())}
          >
            Send max
          </Typography>
        </Box>
      </Box>
      
      {/* Note section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Note (optional)
        </Typography>
        
        <TextField
          fullWidth
          placeholder="Add a message..."
          value={note}
          onChange={handleNoteChange}
          multiline
          rows={3}
          InputProps={{
            sx: {
              borderRadius: '12px',
              bgcolor: 'rgba(17, 25, 40, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#fff',
              '&::placeholder': {
                color: 'rgba(255, 255, 255, 0.5)',
                opacity: 1
              }
            }
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                border: 'none'
              },
              '&:hover fieldset': {
                border: 'none'
              },
              '&.Mui-focused fieldset': {
                border: 'none'
              }
            }
          }}
        />
      </Box>
      
      {/* Transaction fee */}
      <Box sx={{ mb: 4, px: 2, py: 3, bgcolor: 'rgba(17, 25, 40, 0.7)', borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Transaction fee
          </Typography>
          <Typography variant="body2" color="text.primary">
            {getCurrencySymbol(balanceData.currency, user)}{amount ? totalFee().toFixed(2) : '0.00'} <IconButton size="small"><QrCodeIcon fontSize="inherit" /></IconButton>
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="body1" fontWeight="bold" color="text.primary">
            Total
          </Typography>
          <Typography variant="body1" fontWeight="bold" color="text.primary">
            {getCurrencySymbol(balanceData.currency, user)}{amount ? totalAmount().toFixed(2) : '0.00'}
          </Typography>
        </Box>
      </Box>
      
      {/* Payment method selection */}
      {parseFloat(amount) > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            Delivery Speed
          </Typography>
          
          <RadioGroup
            value={speedOption}
            onChange={handleSpeedOptionChange}
            sx={{ width: '100%' }}
          >
            {/* Standard option */}
            <FormControlLabel 
              value="standard"
              control={<Radio />}
              label={
                <Box sx={{ ml: 1 }}>
                  <Typography variant="body2" color="text.primary">
                    Standard
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {UI_STANDARD_ALL_IN_FEE} fee ({getCurrencySymbol(balanceData.currency, user)}{calculateFee(parseFloat(amount || '0'), STANDARD_SEND_FEE_RATE).toFixed(2)})
                  </Typography>
                  {parseFloat(amount) > balanceData.available && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                      {getCurrencySymbol(balanceData.currency, user)}{Math.min(parseFloat(amount), balanceData.available).toFixed(2)} sent instantly, {getCurrencySymbol(balanceData.currency, user)}{(parseFloat(amount) - balanceData.available).toFixed(2)} in 1-3 business days
                    </Typography>
                  )}
                </Box>
              }
              sx={{ 
                p: 2, 
                borderRadius: 2,
                bgcolor: 'rgba(17, 25, 40, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                mb: 2,
                width: '100%',
                m: 0
              }}
            />
            
            {/* Express option */}
            <FormControlLabel 
              value="express"
              control={<Radio />}
              label={
                <Box sx={{ ml: 1 }}>
                  <Typography variant="body2" color="text.primary">
                    Express
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {UI_EXPRESS_ALL_IN_FEE} fee ({getCurrencySymbol(balanceData.currency, user)}{calculateFee(parseFloat(amount || '0'), EXPRESS_ALL_IN_FEE_RATE).toFixed(2)})
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                    Funds available instantly (≤15 minutes)
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: '0.7rem', mt: 0.5, opacity: 0.7 }}>
                    *Includes {UI_INSTANT_DEPOSIT_FEE} deposit fee + {UI_STANDARD_SEND_FEE} send fee
                  </Typography>
                </Box>
              }
              sx={{ 
                p: 2, 
                borderRadius: 2,
                bgcolor: 'rgba(17, 25, 40, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                width: '100%',
                m: 0
              }}
            />
          </RadioGroup>
        </Box>
      )}
      
      {/* Bank account selection */}
      {parseFloat(amount) > balanceData.available && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            Bank Account for Additional Funds
          </Typography>
          
          {bankAccounts.length > 0 ? (
            <RadioGroup
              value={selectedBankAccount}
              onChange={handleBankAccountChange}
              sx={{ width: '100%' }}
            >
              {bankAccounts.map((account) => (
                <FormControlLabel
                  key={account.id}
                  value={account.id}
                  control={<Radio />}
                  label={
                    <Box sx={{ ml: 1 }}>
                      <Typography variant="body2" color="text.primary">
                        {account.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {account.accountNumber}
                      </Typography>
                    </Box>
                  }
                  sx={{ 
                    p: 2, 
                    borderRadius: 2,
                    bgcolor: 'rgba(17, 25, 40, 0.7)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    mb: 1,
                    width: '100%',
                    m: 0
                  }}
                />
              ))}
            </RadioGroup>
          ) : (
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              fullWidth
              sx={{ 
                py: 2,
                borderColor: 'rgba(255, 255, 255, 0.1)',
                color: 'text.primary',
                borderStyle: 'dashed'
              }}
            >
              Link Bank Account
            </Button>
          )}
        </Box>
      )}
      
      {/* Action buttons */}
      <Button
        fullWidth
        variant="contained"
        onClick={handleContinue}
        disabled={!recipient || !amount || parseFloat(amount) <= 0}
        sx={{ 
          py: 1.8,
          bgcolor: theme.palette.primary.main,
          color: '#fff',
          '&:hover': {
            bgcolor: theme.palette.primary.dark,
            boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)'
          },
          '&.Mui-disabled': {
            bgcolor: 'rgba(59, 130, 246, 0.2)',
            color: 'rgba(255, 255, 255, 0.3)'
          }
        }}
      >
        Continue
      </Button>
    </>
  );
  
  const renderConfirmScreen = () => {
    // Check if recipient is Hadeer (EUR account)
    const isEurRecipient = recipient.email === 'hadeermotair@gmail.com';
    const showCurrencyConversion = isEurRecipient && user && user.email !== 'hadeermotair@gmail.com';
    
    return (
    <>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h4" component="h1" fontWeight="600" color="#fff">
          Review Payment
        </Typography>
      </Box>
      
      {/* Recipient info */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar 
          src={recipient?.avatar} 
          alt={recipient?.name} 
          sx={{ width: 60, height: 60 }}
        />
        <Box>
          <Typography variant="h6" color="text.primary">
            {recipient?.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Liquicity User
          </Typography>
          {showCurrencyConversion && (
            <Typography variant="caption" sx={{ display: 'block', color: 'primary.main', mt: 0.5 }}>
              EUR Account (Currency conversion applies)
            </Typography>
          )}
        </Box>
      </Box>
      
      {/* Amount and details */}
      <Box sx={{ mb: 4, p: 3, bgcolor: 'rgba(17, 25, 40, 0.7)', borderRadius: 2 }}>
        <Typography variant="h4" color="text.primary" sx={{ mb: 3, textAlign: 'center' }}>
          {getCurrencySymbol(balanceData.currency, user)}{parseFloat(amount).toFixed(2)}
        </Typography>
        
        {note && (
          <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {note}
            </Typography>
          </Box>
        )}
        
        <Divider sx={{ my: 2, bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
        
        {/* Payment details */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Payment Method
          </Typography>
          
          {speedOption === 'standard' && (
            <Typography variant="body1" color="text.primary">
              Standard (1-3 business days)
            </Typography>
          )}
          
          {speedOption === 'express' && (
            <Typography variant="body1" color="text.primary">
              Express (≤15 minutes)
            </Typography>
          )}
        </Box>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Fee
          </Typography>
          <Typography variant="body1" color="text.primary">
            {getCurrencySymbol(balanceData.currency, user)}{totalFee().toFixed(2)} 
            {speedOption === 'standard' 
              ? `(${UI_STANDARD_ALL_IN_FEE} - Standard)` 
              : `(${UI_EXPRESS_ALL_IN_FEE} - Express)`}
          </Typography>
        </Box>

        {showCurrencyConversion && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Currency Conversion
            </Typography>
            <Typography variant="body1" color="text.primary">
              USD to EUR (2% conversion fee)
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Recipient will receive approximately €{((parseFloat(amount) * 0.98 * 0.85)).toFixed(2)}
            </Typography>
          </Box>
        )}
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Delivery
          </Typography>
          <Typography variant="body1" color="text.primary">
            {speedOption === 'standard' && parseFloat(amount) <= balanceData.available && 'Funds available in 1-3 business days'}
            {speedOption === 'standard' && parseFloat(amount) > balanceData.available && (
              `${getCurrencySymbol(balanceData.currency, user)}${Math.min(parseFloat(amount), balanceData.available).toFixed(2)} instantly, 
               ${getCurrencySymbol(balanceData.currency, user)}${(parseFloat(amount) - balanceData.available).toFixed(2)} in 1-3 business days`
            )}
            {speedOption === 'express' && 'All funds available instantly (≤15 minutes)'}
          </Typography>
        </Box>
        
        <Divider sx={{ my: 2, bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="body1" fontWeight="bold" color="text.primary">
            Total
          </Typography>
          <Typography variant="body1" fontWeight="bold" color="text.primary">
            {getCurrencySymbol(balanceData.currency, user)}{totalAmount().toFixed(2)}
          </Typography>
        </Box>
      </Box>
      
      {/* Action buttons */}
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Button
            fullWidth
            variant="outlined"
            onClick={handleCancel}
            sx={{ 
              py: 1.5,
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: '#fff',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.5)',
                bgcolor: 'rgba(255, 255, 255, 0.05)'
              }
            }}
          >
            Cancel
          </Button>
        </Grid>
        <Grid item xs={6}>
          <Button
            fullWidth
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
            sx={{ 
              py: 1.5,
              bgcolor: theme.palette.primary.main,
              color: '#fff',
              '&:hover': {
                bgcolor: theme.palette.primary.dark,
                boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)'
              }
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Send Money'}
          </Button>
        </Grid>
      </Grid>
      
      {error && (
        <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}
    </>
    );
  };
  
  const renderSuccessScreen = () => {
    // Check if recipient is Hadeer (EUR account)
    const isEurRecipient = recipient.email === 'hadeermotair@gmail.com';
    const showCurrencyConversion = isEurRecipient && user && user.email !== 'hadeermotair@gmail.com';
    
    return (
    <>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" fontWeight="600" color="#fff" sx={{ mb: 2 }}>
          Money Sent!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Your transfer to {recipient?.name} was successful.
        </Typography>
      </Box>
      
      <Box sx={{ 
        mb: 4, 
        p: 3, 
        bgcolor: 'rgba(17, 25, 40, 0.7)', 
        borderRadius: 2,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <Avatar 
          src={recipient?.avatar} 
          alt={recipient?.name} 
          sx={{ width: 80, height: 80, mb: 2 }}
        />
        
        <Typography variant="h6" color="text.primary" sx={{ mb: 1 }}>
          {recipient?.name}
        </Typography>
        
        <Typography variant="h3" color="text.primary" sx={{ mb: 3 }}>
          {getCurrencySymbol(balanceData.currency, user)}{parseFloat(amount).toFixed(2)}
        </Typography>
        
        {showCurrencyConversion && (
          <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(59, 130, 246, 0.05)', borderRadius: 1, width: '100%' }}>
            <Typography variant="body2" color="text.primary" fontWeight="medium">
              Currency Conversion:
            </Typography>
            <Typography variant="body2" color="text.secondary">
              USD to EUR with 2% conversion fee
            </Typography>
            <Typography variant="body2" color="text.primary" fontWeight="medium" sx={{ mt: 1 }}>
              Recipient received: €{((parseFloat(amount) * 0.98 * 0.85)).toFixed(2)}
            </Typography>
          </Box>
        )}
        
        {note && (
          <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1, width: '100%' }}>
            <Typography variant="body2" color="text.secondary">
              {note}
            </Typography>
          </Box>
        )}
        
        <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Delivery Speed
          </Typography>
          <Typography variant="body1" color="text.primary">
            {speedOption === 'standard' ? 'Standard (1-3 business days)' : 'Express (≤15 minutes)'}
          </Typography>
          
          {speedOption === 'standard' && parseFloat(amount) > balanceData.available && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
              {getCurrencySymbol(balanceData.currency, user)}{Math.min(parseFloat(amount), balanceData.available).toFixed(2)} sent instantly, 
              {getCurrencySymbol(balanceData.currency, user)}{(parseFloat(amount) - balanceData.available).toFixed(2)} will arrive in 1-3 business days
            </Typography>
          )}
        </Box>
        
        <Typography variant="body2" color="text.secondary">
          Transaction ID: {success?.transfer_id || 'TRX' + Math.floor(Math.random() * 1000000)}
        </Typography>
        
        <Typography variant="body2" color="text.secondary">
          {format(new Date(), 'MMM dd, yyyy • HH:mm')}
        </Typography>
      </Box>
      
      <Button
        fullWidth
        variant="contained"
        onClick={handleCancel}
        sx={{ 
          py: 1.8,
          bgcolor: theme.palette.primary.main,
          color: '#fff',
          '&:hover': {
            bgcolor: theme.palette.primary.dark,
            boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)'
          }
        }}
      >
        Done
      </Button>
    </>
    );
  };
  
  const renderTransactionHistory = () => (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" color="#fff" sx={{ mb: 3 }}>
        Recent Transactions
      </Typography>
      
      {mockTransactions.map((transaction) => (
        <Box 
          key={transaction.id}
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            p: 2,
            mb: 2,
            borderRadius: 2,
            bgcolor: 'rgba(17, 25, 40, 0.5)',
            transition: 'all 0.2s',
            '&:hover': {
              bgcolor: 'rgba(17, 25, 40, 0.7)',
            }
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar 
              src={transaction.recipient.avatar} 
              alt={transaction.recipient.name} 
              sx={{ width: 40, height: 40 }}
            />
            <Box>
              <Typography variant="body2" color="text.primary">
                {transaction.recipient.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {format(transaction.date, 'MMM d, yyyy')}
              </Typography>
            </Box>
          </Box>
          
          <Typography 
            variant="body2" 
            color={transaction.type === 'sent' ? '#ef4444' : '#10b981'}
            fontWeight="500"
          >
            {transaction.type === 'sent' ? '-' : '+'}
            {getCurrencySymbol(balanceData.currency, user)}
            {Math.abs(transaction.amount).toFixed(2)}
            <Typography 
              component="span" 
              variant="caption" 
              color={transaction.type === 'sent' ? 'error.dark' : 'success.dark'}
              sx={{ display: 'block', textAlign: 'right' }}
            >
              {transaction.type === 'sent' ? 'Sent' : 'Received'}
            </Typography>
          </Typography>
        </Box>
      ))}
      
      <Box sx={{ textAlign: 'center', mt: 3 }}>
        <Button
          variant="text"
          sx={{ 
            color: theme.palette.primary.main,
            textTransform: 'none',
            '&:hover': {
              bgcolor: 'rgba(59, 130, 246, 0.1)'
            }
          }}
        >
          View All Transactions
        </Button>
      </Box>
    </Box>
  );

  return (
    <Box
      component={motion.div}
      variants={pageVariants}
      initial="initial"
      animate="animate"
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
              <Box />
              <Typography variant="body2" color="text.secondary">
                Balance: <Typography component="span" fontWeight="600" color="#fff">{getCurrencySymbol(balanceData.currency, user)}{balanceData.total.toLocaleString()}</Typography>
                <IconButton 
                  size="small" 
                  onClick={() => fetchWalletData()}
                  sx={{ ml: 0.5, color: 'primary.main' }}
                  title="Refresh balance"
                >
                  <RefreshIcon fontSize="small" />
                </IconButton>
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
              {step === 'initial' && renderInitialScreen()}
              {step === 'confirm' && renderConfirmScreen()}
              {step === 'success' && renderSuccessScreen()}
            </Paper>
            
            {/* Only show transaction history on initial screen */}
            {step === 'initial' && renderTransactionHistory()}
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
} 