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
  IconButton
} from '@mui/material';
import { Search as SearchIcon, ArrowBack as ArrowBackIcon, Send as SendIcon, Edit as EditIcon, ArrowDropDown as ArrowDropDownIcon } from '@mui/icons-material';
import api, { transferAPI } from '../../utils/api';
import useBridgeWallet from '../../hooks/useBridgeWallet';
import { calculateLiquicityBalance } from '../../utils/balanceUtils';

export default function Send() {
  const navigate = useNavigate();
  const { wallet: bridgeWallet, refetch: refetchWallet } = useBridgeWallet();

  // balance
  const balanceData = useMemo(() => {
    const total = calculateLiquicityBalance(bridgeWallet);
    const currency = bridgeWallet?.fiat_currency?.toUpperCase() || 'USD';
    return { total, currency };
  }, [bridgeWallet]);

  // form state
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [recipient, setRecipient] = useState(null);
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  const [error, setError] = useState(null);
  const [sending, setSending] = useState(false);

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

  const select = (u) => { setRecipient(u); setShowResults(false); setQuery(''); };

  const reset = () => { setRecipient(null); setAmount(''); setNote(''); };

  const toggleResults=()=> setShowResults((prev)=>!prev);

  const onSend = async () => {
    if (!recipient || !amount) return;
    if (parseFloat(amount) > balanceData.total) { setError('Insufficient balance'); return; }
    setSending(true); setError(null);
    try {
      await transferAPI.send({ recipient_user_id: recipient.id, amount: parseFloat(amount), memo: note || undefined });
      await refetchWallet();
      navigate('/dashboard');
    } catch (e) {
      setError(e?.response?.data?.detail || e.message);
    } finally { setSending(false); }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>Send Money</Typography>

      <Typography variant="body2" color="text.secondary">Balance: {balanceData.currency==='USD'? '$':''}{balanceData.total.toFixed(2)} {balanceData.currency}</Typography>

      {error && <Alert severity="error" sx={{ my:2 }}>{error}</Alert>}

      {/* Recipient */}
      <Box sx={{ my:3 }}>
        <Typography variant="subtitle2" gutterBottom>Recipient</Typography>
        {recipient ? (
          <Box sx={{ display:'flex',alignItems:'center',gap:2, border:1, borderColor:'divider', borderRadius:2, p:1 }}>
            <Avatar>{(recipient.name||recipient.email)[0].toUpperCase()}</Avatar>
            <Box sx={{ flex:1 }}>
              {recipient.name && <Typography>{recipient.name}</Typography>}
              <Typography variant="body2" color="text.secondary">{recipient.email}</Typography>
            </Box>
            <Chip label={recipient.region?.toUpperCase()||'USD'} size="small"/>
            <IconButton onClick={()=>setRecipient(null)}><EditIcon/></IconButton>
          </Box>
        ) : (
          <Box sx={{ position:'relative' }}>
            <TextField fullWidth placeholder="Search name or email" value={query} onChange={e=>setQuery(e.target.value)} InputProps={{ startAdornment:(<InputAdornment position="start"><SearchIcon/></InputAdornment>), endAdornment:(<InputAdornment position="end">{loading? <CircularProgress size={20}/>:<IconButton size="small" onClick={toggleResults}><ArrowDropDownIcon/></IconButton>}</InputAdornment>) }} /> 
            {showResults && (
              <Paper sx={{ position:'absolute', top:'100%', left:0, right:0, zIndex:10, maxHeight:300, overflow:'auto' }}>
                {results.length? <List>
                  {results.map(u=> (
                    <ListItem button key={u.id} onClick={()=>select(u)}>
                      <ListItemAvatar><Avatar>{(u.name||u.email)[0].toUpperCase()}</Avatar></ListItemAvatar>
                      <ListItemText primary={u.name||u.email} secondary={u.name?u.email:null}/>
                      <Chip label={u.region?.toUpperCase()||'USD'} size="small"/>
                    </ListItem>
                  ))}
                </List> : <Box sx={{ p:2 }}><Typography variant="body2" color="text.secondary">No users found</Typography></Box>}
              </Paper>) }
          </Box>) }
      </Box>
      
      {/* Amount */}
      <Box sx={{ my:3 }}>
        <Typography variant="subtitle2" gutterBottom>Amount</Typography>
        <TextField fullWidth placeholder="0.00" value={amount} onChange={e=>{/^\d*\.?\d{0,2}$/.test(e.target.value)&&setAmount(e.target.value)}} InputProps={{ startAdornment:(<InputAdornment position="start">{balanceData.currency==='USD'? '$':balanceData.currency}</InputAdornment>)}} />
      </Box>
      
      {/* Note */}
      <Box sx={{ my:3 }}>
        <Typography variant="subtitle2" gutterBottom>Note (optional)</Typography>
        <TextField fullWidth multiline rows={2} value={note} onChange={e=>setNote(e.target.value)} />
      </Box>
      
      <Box sx={{ display:'flex', gap:2 }}>
        <Button variant="outlined" fullWidth onClick={reset}>Cancel</Button>
        <Button variant="contained" fullWidth startIcon={sending?<CircularProgress size={20}/> : <SendIcon/>} disabled={sending||!recipient||!amount} onClick={onSend}>Send</Button>
      </Box>
      </Container>
  );
} 