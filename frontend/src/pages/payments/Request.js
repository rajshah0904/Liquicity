import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Alert, 
  CircularProgress, 
  Container,
  Avatar,
  Grid,
  InputAdornment,
  IconButton,
  Divider,
  useTheme,
  Paper,
  Button,
  List,
  ListItem
} from '@mui/material';
import { requestsAPI, authAPI, walletAPI } from '../../utils/api';
import { motion } from 'framer-motion';
import { Search as SearchIcon, QrCode as QrCodeIcon, Add as AddIcon } from '@mui/icons-material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { AnimatedBackground } from '../../components/ui/ModernUIComponents';
import { format } from 'date-fns';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

// Currency conversion mock rates
const conversionRates = {
  USD: 1,
  EUR: 0.92,
  MXN: 16.85,
  GBP: 0.78,
  CAD: 1.35
};

const mockRequests = [
  { id: 1, requestee: { id: 1, name: 'Demo', avatar: null }, date:new Date(), amount:50, status:'pending', note:'' }
];

// Same hard-coded recent contacts used in Send page
const mockRecipients = [
  { id: 'user-1', name: 'Hadeer Motair', avatar: '/avatars/avatar1.jpg', email: 'hadeermotair@gmail.com' },
  { id: 'user-raj', name: 'Raj Shah', avatar: '/avatars/avatar2.jpg', email: 'rajshah11@gmail.com' }
];

export default function RequestPage() {
  const theme = useTheme();
  const [step, setStep] = useState('initial'); // initial, confirm, success
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown,setShowDropdown]=useState(false);
  const [recipient, setRecipient] = useState(null);
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  const [userData, setUserData] = useState({ currency: 'USD', balance: 0 });
  const [currency, setCurrency] = useState('USD');
  const [requests, setRequests] = useState(mockRequests);
  const [balanceData,setBalanceData]=useState({available:0,currency:'USD'});
  const currentUserEmail = localStorage.getItem('mockCurrentUserEmail') || (typeof window!== 'undefined' && JSON.parse(localStorage.getItem('current_user')||'{}').email) || '';
  const allowedRecipientEmail = currentUserEmail === 'hadeermotair@gmail.com' ? 'rajsshah11@gmail.com' : 'hadeermotair@gmail.com';
  
  // Fetch user data and requests
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // In a real app, this would fetch the user's data including their preferred currency
        // For now, we'll use mock data
        const resp = await requestsAPI.list();
        if (resp.data && resp.data.requests) {
          setRequests(resp.data.requests);
        } else {
          // Use mock data if the API call doesn't return real data
          setRequests(mockRequests);
        }
        const email = localStorage.getItem('mockCurrentUserEmail') || 'rajshah11@gmail.com';
        const newData = {
          currency: email === 'hadeermotair@gmail.com' ? 'EUR' : 'USD',
          balance: 1000.00
        };
        setUserData(newData);
        setCurrency(newData.currency || 'USD');
      } catch (err) {
        console.error('Failed to fetch user data', err);
        // Use mock data as fallback
        setRequests(mockRequests);
      }
    };
    
    fetchUserData();
  }, []);
  
  // fetch wallet balance similar to Send page
  useEffect(() => {
    const fetchBalance = async () => {
      try {
        const walletResp = await walletAPI.getOverview();
        if (walletResp.data && walletResp.data.wallets && walletResp.data.wallets.length > 0) {
          const email = localStorage.getItem('mockCurrentUserEmail');
          if (email === 'hadeermotair@gmail.com') {
            const eurWallet = walletResp.data.wallets.find((w) => w.currency === 'eur') || walletResp.data.wallets[0];
            setBalanceData({ available: eurWallet.balance || 0, currency: 'EUR' });
          } else {
            const usdWallet = walletResp.data.wallets.find((w) => w.currency === 'usd') || walletResp.data.wallets[0];
            setBalanceData({
              available: usdWallet.balance || 0,
              currency: usdWallet.currency?.toUpperCase() || 'USD'
            });
          }
        }
      } catch (e) {
        console.error('wallet fetch', e);
      }
    };

    fetchBalance();
  }, []);
  
  const handleSearch = async (e) => {
    setSearchQuery(e.target.value);
    if(!e.target.value){setShowDropdown(false);return;}
    try{
      const resp = await authAPI.searchUsers(e.target.value);
      const filtered = (resp.data.users || []).filter(u=>u.email===allowedRecipientEmail);
      setSearchResults(filtered);
      setShowDropdown(true);
    }catch(err){console.error(err);setSearchResults([]);}
  };
  
  const selectRecipient = (person) => {
    setRecipient(person);
    setSearchQuery(person.name);
    setShowDropdown(false);
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
  
  const handleCurrencyChange = (newCurrency) => {
    // Currency cannot be changed - locked to user's local currency
    console.log("Currency is locked to user's local currency:", userData.currency);
  };
  
  const getCurrencySymbol = (currencyCode) => {
    switch(currencyCode) {
      case 'EUR': return '€';
      case 'GBP': return '£';
      case 'MXN': return '₱';
      case 'CAD': return 'C$';
      default: return '$';
    }
  };
  
  const getConvertedAmount = () => {
    if (!amount || !recipient) return '';
    
    const amountNum = parseFloat(amount);
    if (isNaN(amountNum)) return '';
    
    // Assuming recipient uses their local currency (not necessarily USD)
    const recipientCurrency = recipient.currency || currency;
    
    if (currency === recipientCurrency) return amountNum.toFixed(2);
    
    // Convert between selected currencies
    const conversionRate = conversionRates[currency] / conversionRates[recipientCurrency];
    return (amountNum / conversionRate).toFixed(2);
  };
  
  const handleSubmit = async () => {
    if (!recipient || !amount || parseFloat(amount) <= 0) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Create request payload
      const payload = {
        requestee_user_id: recipient.id,
        amount: parseFloat(amount),
        currency: currency,
        note: note || undefined
      };
      
      const resp = await requestsAPI.create(payload);
      setSuccess(resp.data);
      setStep('success');
      
      // Refresh requests list
      const requestsResp = await requestsAPI.list();
      if (requestsResp.data && requestsResp.data.requests) {
        setRequests(requestsResp.data.requests);
      }
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err.message || 'Request failed');
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
      setCurrency(userData.currency || 'USD');
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
  
  const handlePay = async(id)=>{
    try{await requestsAPI.pay(id);const r=await requestsAPI.list();setRequests(r.data.requests);}catch(e){console.error(e);}
  };
  const handleDecline = async(id)=>{
    try{await requestsAPI.decline(id);const r=await requestsAPI.list();setRequests(r.data.requests);}catch(e){console.error(e);}
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
  
  const renderInitialScreen = () => (
    <>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="600" color="#fff">
          Request Money
        </Typography>
      </Box>
      
      {/* Recipient section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Request From
        </Typography>
        
        <Box sx={{ position: 'relative' }}>
          <TextField
            fullWidth
            placeholder="Search for someone..."
            value={searchQuery}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton sx={{ color: 'primary.main' }}>
                    <QrCodeIcon />
                  </IconButton>
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
        </Box>
        
        {/* Recent Recipients */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Recent Contacts
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {mockRecipients.filter(p=>p.email===allowedRecipientEmail).map((person) => (
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
            {getCurrencySymbol(currency)}
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
              bgcolor: 'rgba(17, 25, 40, 0.7)',
            }}
          >
            <Typography variant="body2" color="text.primary">
              {currency}
            </Typography>
          </Box>
        </Box>
      </Box>
      
      {/* Note section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Note (optional)
        </Typography>
        
        <TextField
          fullWidth
          placeholder="What's it for?"
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
  
  const renderConfirmScreen = () => (
    <>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h4" component="h1" fontWeight="600" color="#fff">
          Review Request
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
        </Box>
      </Box>
      
      {/* Amount and details */}
      <Box sx={{ mb: 4, p: 3, bgcolor: 'rgba(17, 25, 40, 0.7)', borderRadius: 2 }}>
        <Typography variant="h4" color="text.primary" sx={{ mb: 3, textAlign: 'center' }}>
          {getCurrencySymbol(currency)}
          {parseFloat(amount).toFixed(2)} {currency}
        </Typography>
        
        {note && (
          <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {note}
            </Typography>
          </Box>
        )}
        
        <Divider sx={{ my: 2, bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
        
        <Typography variant="body2" color="text.secondary">
          {recipient?.name} will receive a notification about your request. They can choose to accept and pay it or decline it.
        </Typography>
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
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Send Request'}
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
  
  const renderSuccessScreen = () => (
    <>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" fontWeight="600" color="#fff" sx={{ mb: 2 }}>
          Request Sent!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Your money request has been sent to {recipient?.name}.
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
          {getCurrencySymbol(currency)}
          {parseFloat(amount).toFixed(2)}
        </Typography>
        
        {note && (
          <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1, width: '100%' }}>
            <Typography variant="body2" color="text.secondary">
              {note}
            </Typography>
          </Box>
        )}
        
        <Typography variant="body2" color="text.secondary">
          Request ID: {success?.request_id || 'REQ' + Math.floor(Math.random() * 1000000)}
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
  
  const renderPendingRequests = () => (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" color="#fff" sx={{ mb: 3 }}>
        Your Requests
      </Typography>
      
      {requests.map((request) => (
        <Box 
          key={request.id}
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
              src={'/avatars/default.jpg'} 
              alt={currentUserEmail===request.requester_email?request.recipient_name:request.requester_name}
              sx={{ width: 40, height: 40 }}
            >
              {!request.requestee?.avatar && <AccountCircleIcon />}
            </Avatar>
            <Box>
              <Typography variant="body2" color="text.primary">
                {currentUserEmail===request.requester_email?request.recipient_name:request.requester_name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {request.created_at ? format(new Date(request.created_at), 'MMM d, yyyy') : ''}
              </Typography>
              {request.note && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                  "{request.note}"
                </Typography>
              )}
            </Box>
          </Box>
          
          <Box sx={{ textAlign: 'right' }}>
            <Typography 
              variant="body2" 
              fontWeight="500"
              color="text.primary"
            >
              {getCurrencySymbol(request.currency)}
              {request.amount?.toFixed(2) || '0.00'}
            </Typography>
            <Typography 
              component="span" 
              variant="caption" 
              sx={{ 
                px: 1, 
                py: 0.3, 
                borderRadius: 1, 
                bgcolor: request.status === 'pending' 
                  ? 'rgba(245, 158, 11, 0.2)' 
                  : request.status === 'completed' 
                    ? 'rgba(16, 185, 129, 0.2)' 
                    : 'rgba(239, 68, 68, 0.2)',
                color: request.status === 'pending' 
                  ? '#f59e0b' 
                  : request.status === 'completed' 
                    ? '#10b981' 
                    : '#ef4444',
                display: 'inline-block',
                fontSize: '0.7rem',
                fontWeight: 'medium',
                textTransform: 'capitalize'
              }}
            >
              {request.status || 'unknown'}
            </Typography>
            {currentUserEmail===request.recipient_email && request.status==='pending' && (
              <Box sx={{mt:1,display:'flex',gap:1}}>
                <Button size="small" variant="contained" onClick={()=>handlePay(request.id)}>Pay</Button>
                <Button size="small" color="error" onClick={()=>handleDecline(request.id)}>Decline</Button>
              </Box>
            )}
          </Box>
        </Box>
      ))}
      
      {requests.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
          <Typography variant="body2">
            You don't have any money requests yet.
          </Typography>
        </Box>
      )}
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
                Balance: <Typography component="span" fontWeight="600" color="#fff">{getCurrencySymbol(balanceData.currency)}{Number(balanceData.available||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</Typography>
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
            
            {/* Only show pending requests on initial screen */}
            {step === 'initial' && renderPendingRequests()}
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
} 