import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip,
  InputAdornment,
  Alert,
  CircularProgress,
  Paper,
  Container,
  IconButton,
  Card,
  CardContent,
  Divider,
  Grid
} from '@mui/material';
import {
  Search as SearchIcon,
  ArrowDropDown as ArrowDropDownIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  QrCode as QrCodeIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { styled, useTheme } from '@mui/material/styles';
import { motion } from 'framer-motion';
import api, { transferAPI } from '../../utils/api';
import useBridgeWallet from '../../hooks/useBridgeWallet';
import { calculateLiquicityBalance } from '../../utils/balanceUtils';
import { getCurrencySymbol, formatCurrency } from '../../utils/currency';
import { AnimatedBackground } from '../../components/ui/ModernUIComponents';

export default function Send() {
  const navigate = useNavigate();
  const theme = useTheme();
  const { wallet: bridgeWallet, refetch: refetchWallet } = useBridgeWallet();

  // balance
  const balanceData = useMemo(() => {
    const total = calculateLiquicityBalance(bridgeWallet);
    const currency = bridgeWallet?.fiat_currency?.toUpperCase() || 'USD';
    return { total, currency };
  }, [bridgeWallet]);

  // form state
  const [step, setStep] = useState('initial'); // initial, confirm
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [recipient, setRecipient] = useState(null);
  const [recent, setRecent] = useState([]);
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  const [error, setError] = useState(null);
  const [sending, setSending] = useState(false);
  const [quote, setQuote] = useState(null);

  // search users
  useEffect(() => {
    if (query.length < 2) {
      setResults([]); setShowResults(false); return;
    }
    const id = setTimeout(async () => {
      try {
        setLoading(true); setShowResults(true);
        const { data } = await api.get('/user/search', { params: { q: query } });
        setResults(data.users || []);
      } catch (e) {
        console.error(e); setResults([]);
      } finally { setLoading(false); }
    }, 300);
    return () => clearTimeout(id);
  }, [query]);

  const select = (u) => {
    setRecipient(u);
    setShowResults(false);
    setQuery('');
    // maintain a small recent list (up to 5)
    setRecent(prev => {
      const exists = prev.find(x => x.id === u.id);
      const next = exists ? prev : [u, ...prev];
      return next.slice(0, 5);
    });
  };

  const reset = () => { 
    setRecipient(null); 
    setAmount(''); 
    setNote(''); 
    setStep('initial'); 
    setQuote(null);
    setError(null);
  };

  const toggleResults = () => setShowResults(prev => !prev);

  // computed
  const currencyFrom = balanceData.currency;
  const currencyTo = (recipient?.region?.toUpperCase?.() || 'USD');
  const amountNum = useMemo(() => {
    const n = parseFloat(amount);
    return isNaN(n) ? 0 : Math.max(0, Math.min(n, 99999999));
  }, [amount]);
  
  const isInsufficientFunds = amountNum > balanceData.total;

  const handleAmountChange = (e) => {
    // Only allow numeric input with decimal
    const value = e.target.value;
    if (value === '' || /^\d*\.?\d{0,2}$/.test(value)) {
      setAmount(value);
    }
  };

  const onNext = async () => {
    if (!recipient || !amountNum) return;
    
    setError(null);
    setStep('confirm');
    
    try {
      const { data } = await transferAPI.quote({ recipient_user_id: recipient.id, amount: Number(amountNum.toFixed(2)) });
      setQuote(data);
    } catch (e) {
      setQuote(null);
    }
  };

  const onSend = async () => {
    if (!recipient || !amountNum) return;
    setSending(true); setError(null);
    try {
      await transferAPI.send({ recipient_user_id: recipient.id, amount: Number(amountNum.toFixed(2)), memo: note || undefined });
      await refetchWallet();
      navigate('/dashboard');
    } catch (e) {
      const data = e?.response?.data;
      let msg = e?.message || 'Request failed';
      if (data?.detail) {
        if (Array.isArray(data.detail)) {
          msg = data.detail.map(d => (d.msg || (typeof d === 'string' ? d : JSON.stringify(d)))).join(', ');
        } else if (typeof data.detail === 'string') {
          msg = data.detail;
        } else {
          try { msg = JSON.stringify(data.detail); } catch { msg = 'Request failed'; }
        }
      }
      setError(msg);
    } finally { setSending(false); }
  };

  const handleCancel = () => {
    if (step === 'confirm') {
      setStep('initial');
      setError(null);
    } else {
      reset();
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
            placeholder="Search name or email"
            value={query}
            onChange={e => setQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton size="small" onClick={toggleResults}>
                    <ArrowDropDownIcon sx={{ color: 'text.secondary' }} />
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
          
          {showResults && (
            <Paper sx={{ 
              position:'absolute', 
              top:'100%', 
              left:0, 
              right:0, 
              zIndex:10, 
              maxHeight:300, 
              overflow:'auto', 
              bgcolor:'rgba(17, 25, 40, 0.9)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              mt: 1
            }}>
              {results.length ? (
                <List>
                  {results.map(u => (
                    <ListItem button key={u.id} onClick={() => select(u)} sx={{ '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' } }}>
                      <ListItemAvatar><Avatar>{(u.name||u.email)[0].toUpperCase()}</Avatar></ListItemAvatar>
                      <ListItemText 
                        primary={u.name||u.email} 
                        secondary={u.name?u.email:null}
                        primaryTypographyProps={{ color: 'text.primary' }}
                        secondaryTypographyProps={{ color: 'text.secondary' }}
                      />
                      <Chip 
                        label={u.region?.toUpperCase()||'USD'} 
                        size="small"
                        sx={{ bgcolor: 'rgba(59, 130, 246, 0.2)', color: theme.palette.primary.main }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Box sx={{ p:2 }}>
                  <Typography variant="body2" color="text.secondary">No users found</Typography>
                </Box>
              )}
            </Paper>
          )}
        </Box>
        
        {/* Recent Recipients */}
        {recent.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Recent Recipients
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {recent.map(u => (
                <Box
                  key={u.id}
                  sx={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    alignItems: 'center',
                    cursor: 'pointer',
                    opacity: recipient && recipient.id === u.id ? 1 : 0.8,
                    transition: 'all 0.2s',
                    '&:hover': {
                      opacity: 1,
                    }
                  }}
                  onClick={() => select(u)}
                >
                  <Avatar 
                    sx={{ 
                      width: 60, 
                      height: 60, 
                      mb: 1,
                      border: recipient && recipient.id === u.id 
                        ? '2px solid #3b82f6' 
                        : '2px solid transparent'
                    }}
                  >
                    {(u.name||u.email)[0].toUpperCase()}
                  </Avatar>
                  <Typography 
                    variant="caption" 
                    color={recipient && recipient.id === u.id ? 'primary' : 'text.secondary'}
                  >
                    {u.name || u.email.split('@')[0]}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        )}
      </Box>
      
      {/* Amount section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Amount
        </Typography>
        
        <Box sx={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h5" color={isInsufficientFunds ? '#ef4444' : 'text.secondary'} sx={{ ml: 1 }}>
            {getCurrencySymbol(balanceData.currency)}
          </Typography>
          <TextField
            fullWidth
            placeholder="0.00"
            value={amount}
            onChange={handleAmountChange}
            onBlur={() => { 
              if (amount !== '') { 
                const num = parseFloat(amount); 
                if (!isNaN(num)) setAmount(num.toFixed(2)); 
              } 
            }}
            InputProps={{
              disableUnderline: true,
              sx: {
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: isInsufficientFunds ? '#ef4444' : '#fff',
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
              border: `1px solid ${isInsufficientFunds ? '#ef4444' : 'rgba(255, 255, 255, 0.1)'}`,
              px: 1.5,
              py: 0.5,
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              bgcolor: 'rgba(17, 25, 40, 0.7)',
            }}
          >
            <Typography variant="body2" color={isInsufficientFunds ? '#ef4444' : 'text.primary'}>
              {balanceData.currency}
            </Typography>
          </Box>
        </Box>
        
        {isInsufficientFunds && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="#ef4444">
              Insufficient funds
            </Typography>
            <Typography 
              variant="caption" 
              color="primary.main" 
              sx={{ 
                cursor: 'pointer', 
                textDecoration: 'underline',
                '&:hover': { color: 'primary.light' }
              }}
              onClick={() => navigate('/deposit')}
            >
              Deposit
            </Typography>
          </Box>
        )}
      </Box>
      
      {/* Note section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Note (optional)
        </Typography>
        
        <TextField
          fullWidth
          placeholder="Add a message"
          value={note}
          onChange={e => setNote(e.target.value)}
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
      
      {/* Action button */}
      <Button
        fullWidth
        variant="contained"
        onClick={onNext}
        disabled={!recipient || !amountNum || isInsufficientFunds}
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
      {/* Title with descriptive send to recipient */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h5" component="h1" fontWeight="600" color="#fff" sx={{ mb: 1 }}>
          Send to {recipient?.name || recipient?.email?.split('@')[0] || 'Recipient'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Confirm your transfer details
        </Typography>
      </Box>
      
      {/* Recipient info card */}
      <Box sx={{ 
        mb: 4, 
        p: 3, 
        bgcolor: 'rgba(17, 25, 40, 0.5)', 
        borderRadius: 2,
        display: 'flex', 
        alignItems: 'center', 
        gap: 3,
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <Avatar 
          sx={{ 
            width: 64, 
            height: 64,
            bgcolor: 'rgba(59, 130, 246, 0.2)',
            color: theme.palette.primary.main,
            fontSize: '1.5rem',
            fontWeight: 'bold'
          }}
        >
          {(recipient?.name || recipient?.email)?.[0]?.toUpperCase()}
        </Avatar>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" color="text.primary" sx={{ mb: 0.5 }}>
            {recipient?.name || recipient?.email?.split('@')[0]}
          </Typography>
          {recipient?.name && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
              {recipient.email}
            </Typography>
          )}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: '#10b981'
            }} />
            <Typography variant="body2" color="text.secondary">
              Instant USD Delivery
            </Typography>
          </Box>
          {recipient?.region && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
              {recipient.region.toUpperCase()} recipient
            </Typography>
          )}
        </Box>
      </Box>
      
      {/* Exchange rate info */}
      <Box sx={{ mb: 4, p: 3, bgcolor: 'rgba(17, 25, 40, 0.7)', borderRadius: 2 }}>
        {quote && (
          <>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                USD sent
              </Typography>
              <Typography variant="body2" color="text.primary" fontWeight="600">
                {getCurrencySymbol(quote.sender_currency)}{Number(amountNum).toFixed(2)}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Exchange Rate
              </Typography>
              <Typography variant="body2" color="text.primary">
                {Number(quote.exchange_rate).toFixed(6)}
              </Typography>
            </Box>
            
            <Divider sx={{ my: 2, bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="body2" color="text.secondary" fontWeight="600">
                Recipient gets
              </Typography>
              <Typography variant="body2" color="text.primary" fontWeight="600">
                {getCurrencySymbol(quote.recipient_currency)}{Number(quote.amount_received).toFixed(2)}
              </Typography>
            </Box>
          </>
        )}
        
        {!quote && (
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
            Getting exchange rate...
          </Typography>
        )}
      </Box>
      
      {note && (
        <Box sx={{ mb: 4, p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            "{note}"
          </Typography>
        </Box>
      )}
      
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
            onClick={onSend}
            disabled={sending}
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
            {sending ? <CircularProgress size={24} color="inherit" /> : 'Send Money'}
          </Button>
        </Grid>
      </Grid>
    </>
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
                Balance: <Typography component="span" fontWeight="600" color="#fff">
                  {getCurrencySymbol(balanceData.currency)}{balanceData.total.toFixed(2)}
                </Typography>
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
            </Paper>
            
            {error && !isInsufficientFunds && (
              <Alert severity="error" sx={{ borderRadius: 2, bgcolor: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>
                {error}
              </Alert>
            )}
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
} 