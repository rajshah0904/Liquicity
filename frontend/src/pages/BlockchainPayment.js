import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, Button, TextField, Grid, Paper, 
  Stepper, Step, StepLabel, CircularProgress, Alert, Divider,
  FormControl, InputLabel, Select, MenuItem, IconButton, Link
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SendIcon from '@mui/icons-material/Send';
import CurrencyBitcoinIcon from '@mui/icons-material/CurrencyBitcoin';
import api from '../utils/api';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(3),
  color: theme.palette.text.primary,
  height: '100%',
}));

const BlockchainPayment = () => {
  const { currentUser, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [wallets, setWallets] = useState([]);
  const [activeStep, setActiveStep] = useState(0);
  const [walletBalances, setWalletBalances] = useState({
    eth: '0.0',
    usdt: '0.0'
  });
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');
  const [selectedToken, setSelectedToken] = useState('USDT');
  const [memo, setMemo] = useState('');
  const [txHash, setTxHash] = useState('');
  const [blockNumber, setBlockNumber] = useState('');
  const [gasUsed, setGasUsed] = useState('');
  const [selectedWallet, setSelectedWallet] = useState(null);
  
  const steps = ['Select Wallet', 'Enter Payment Details', 'Confirm Payment', 'Transaction Result'];

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    fetchWallets();
  }, [navigate, isAuthenticated]);

  const fetchWallets = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/blockchain/wallets/user/${currentUser.id}`);
      
      if (response.status === 200) {
        const data = response.data;
        setWallets(data);
        
        if (data.length === 0) {
          setError('You have no blockchain wallets. Create one to continue.');
        }
      } else {
        setError('Failed to fetch wallets');
      }
    } catch (err) {
      setError('An error occurred while fetching wallets');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createWallet = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.post('/blockchain/wallet/create', {
        user_id: currentUser.id
      });
      
      if (response.status === 200 || response.status === 201) {
        const wallet = response.data;
        setWallets([...wallets, wallet]);
        setSuccess('New wallet created successfully!');
        
        setSelectedWallet(wallet);
        
        fetchWalletBalances(wallet.address);
      } else {
        setError('Failed to create wallet');
      }
    } catch (err) {
      setError('An error occurred while creating wallet');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchWalletBalances = async (address) => {
    try {
      setLoading(true);
      
      const response = await api.get(`/blockchain/wallet/${address}`);
      
      if (response.status === 200) {
        const data = response.data;
        setWalletBalances({
          eth: data.eth_balance || '0.0',
          usdt: data.token_balances?.USDT || '0.0'
        });
      } else {
        console.error('Failed to fetch wallet balances');
      }
    } catch (err) {
      console.error('Error fetching wallet balances:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectWallet = (wallet) => {
    setSelectedWallet(wallet);
    fetchWalletBalances(wallet.address);
  };

  const handleNext = () => {
    if (activeStep === 0 && !selectedWallet) {
      setError('Please select a wallet to continue');
      return;
    }
    
    if (activeStep === 1) {
      if (!validatePaymentDetails()) {
        return;
      }
    }
    
    if (activeStep === 2) {
      processPayment();
      return;
    }
    
    setActiveStep((prevStep) => prevStep + 1);
    setError(null);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
    setError(null);
  };

  const validatePaymentDetails = () => {
    if (!recipient || !/^0x[a-fA-F0-9]{40}$/.test(recipient)) {
      setError('Invalid recipient address');
      return false;
    }
    
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
      setError('Please enter a valid amount');
      return false;
    }
    
    if (selectedToken === 'USDT' && parseFloat(amount) > parseFloat(walletBalances.usdt)) {
      setError('Insufficient USDT balance');
      return false;
    }
    
    if (selectedToken === 'ETH' && parseFloat(amount) > parseFloat(walletBalances.eth)) {
      setError('Insufficient ETH balance');
      return false;
    }
    
    return true;
  };

  const processPayment = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let endpoint, requestBody;
      
      if (selectedToken === 'USDT') {
        endpoint = '/blockchain/token/transfer';
        requestBody = {
          sender_address: selectedWallet.address,
          recipient_address: recipient,
          token_address: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
          amount: parseFloat(amount),
          private_key: selectedWallet.private_key
        };
      } else {
        endpoint = '/blockchain/payment/process';
        requestBody = {
          sender_address: selectedWallet.address,
          recipient_address: recipient,
          amount: parseFloat(amount),
          token_type: 'ETH',
          private_key: selectedWallet.private_key
        };
      }
      
      if (memo) {
        requestBody.memo = memo;
      }
      
      const response = await api.post(endpoint, requestBody);
      
      if (response.status === 200 || response.status === 201) {
        const data = response.data;
        setSuccess('Payment processed successfully!');
        setTxHash(data.transaction_hash);
        setBlockNumber(data.block_number || 'Pending');
        setGasUsed(data.gas_used || 'N/A');
        
        setActiveStep(3);
        
        fetchWalletBalances(selectedWallet.address);
      } else {
        setError('Failed to process payment');
      }
    } catch (err) {
      setError('An error occurred while processing payment');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
  };

  const renderWalletSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Select a Wallet
      </Typography>
      
      {wallets.length === 0 ? (
        <Box sx={{ textAlign: 'center', my: 3 }}>
          <Typography variant="body1" paragraph>
            You don't have any blockchain wallets yet.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={createWallet}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Create New Wallet'}
          </Button>
        </Box>
      ) : (
        <>
          <Grid container spacing={3} sx={{ mt: 2 }}>
            {wallets.map((wallet) => (
              <Grid item xs={12} key={wallet.id}>
                <Paper 
                  sx={{ 
                    p: 2, 
                    cursor: 'pointer',
                    border: selectedWallet?.id === wallet.id ? '2px solid #1976d2' : '1px solid #ddd'
                  }}
                  onClick={() => selectWallet(wallet)}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="subtitle1">
                      Wallet #{wallet.id}
                    </Typography>
                    {selectedWallet?.id === wallet.id && (
                      <Typography variant="caption" color="primary">
                        Selected
                      </Typography>
                    )}
                  </Box>
                  
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                      {wallet.address}
                    </Typography>
                    
                    {selectedWallet?.id === wallet.id && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Balances:
                        </Typography>
                        <Typography variant="body2">
                          ETH: {walletBalances.eth}
                        </Typography>
                        <Typography variant="body2">
                          USDT: {walletBalances.usdt}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
          
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Button
              variant="outlined"
              color="primary"
              onClick={createWallet}
              disabled={loading}
              sx={{ mr: 2 }}
            >
              Create Another Wallet
            </Button>
          </Box>
        </>
      )}
    </Box>
  );
  
  const renderPaymentDetails = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Enter Payment Details
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Recipient Address"
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            placeholder="0x..."
            helperText="Ethereum address of the recipient"
            required
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            type="number"
            required
            InputProps={{ inputProps: { min: 0, step: '0.000001' } }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Token</InputLabel>
            <Select
              value={selectedToken}
              label="Token"
              onChange={(e) => setSelectedToken(e.target.value)}
            >
              <MenuItem value="USDT">USDT (Balance: {walletBalances.usdt})</MenuItem>
              <MenuItem value="ETH">ETH (Balance: {walletBalances.eth})</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Memo (Optional)"
            value={memo}
            onChange={(e) => setMemo(e.target.value)}
            placeholder="Payment for services..."
            multiline
            rows={2}
          />
        </Grid>
      </Grid>
    </Box>
  );
  
  const renderConfirmation = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Confirm Payment
      </Typography>
      
      <Paper sx={{ p: 3, mt: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">From:</Typography>
            <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
              {selectedWallet?.address}
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">To:</Typography>
            <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
              {recipient}
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Amount:</Typography>
            <Typography variant="h6">
              {amount} {selectedToken}
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Network Fee:</Typography>
            <Typography variant="body2">
              ~0.0005 ETH (estimated)
            </Typography>
          </Grid>
          
          {memo && (
            <Grid item xs={12}>
              <Typography variant="subtitle2">Memo:</Typography>
              <Typography variant="body2">
                {memo}
              </Typography>
            </Grid>
          )}
        </Grid>
      </Paper>
      
      <Alert severity="warning" sx={{ mt: 3 }}>
        Please verify all details before confirming. Blockchain transactions cannot be reversed.
      </Alert>
    </Box>
  );
  
  const renderResult = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Transaction Result
      </Typography>
      
      <Paper sx={{ p: 3, mt: 2 }}>
        <Alert severity="success" sx={{ mb: 3 }}>
          Your transaction has been submitted to the blockchain!
        </Alert>
        
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Transaction Hash:</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ wordBreak: 'break-all', mr: 1 }}>
                {txHash}
              </Typography>
              <IconButton size="small" onClick={() => copyToClipboard(txHash)}>
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Block Number:</Typography>
            <Typography variant="body2">
              {blockNumber}
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Gas Used:</Typography>
            <Typography variant="body2">
              {gasUsed}
            </Typography>
          </Grid>
          
          <Grid item xs={12} sx={{ mt: 2 }}>
            <Link 
              href={`https://etherscan.io/tx/${txHash}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              View on Etherscan
            </Link>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );

  return (
    <Container maxWidth="md">
      <Box py={4}>
        <Box mb={4} display="flex" alignItems="center">
          <CurrencyBitcoinIcon color="primary" fontSize="large" sx={{ mr: 1 }} />
          <Typography variant="h4">
            Blockchain Payment
          </Typography>
        </Box>
        
        <Typography variant="body1" paragraph color="textSecondary">
          Send cryptocurrency payments securely through blockchain networks.
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && !error && (
          <Alert severity="success" sx={{ my: 2 }}>
            {success}
          </Alert>
        )}
        
        <Stepper activeStep={activeStep} sx={{ mt: 4, mb: 5 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Item>
          {activeStep === 0 && renderWalletSelection()}
          {activeStep === 1 && renderPaymentDetails()}
          {activeStep === 2 && renderConfirmation()}
          {activeStep === 3 && renderResult()}
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
            {activeStep > 0 && activeStep < 3 && (
              <Button
                variant="outlined"
                onClick={handleBack}
                sx={{ mr: 1 }}
                disabled={loading}
              >
                Back
              </Button>
            )}
            
            {activeStep < 3 && (
              <Button
                variant="contained"
                color="primary"
                onClick={handleNext}
                disabled={loading}
                endIcon={activeStep === 2 ? <SendIcon /> : null}
              >
                {loading ? (
                  <CircularProgress size={24} />
                ) : (
                  activeStep === 2 ? 'Submit Payment' : 'Next'
                )}
              </Button>
            )}
            
            {activeStep === 3 && (
              <Button
                variant="contained"
                color="primary"
                onClick={() => {
                  setActiveStep(0);
                  setRecipient('');
                  setAmount('');
                  setMemo('');
                  setSelectedToken('USDT');
                  setTxHash('');
                  setBlockNumber('');
                  setGasUsed('');
                  setError(null);
                  setSuccess(null);
                }}
              >
                New Payment
              </Button>
            )}
          </Box>
        </Item>
      </Box>
    </Container>
  );
};

export default BlockchainPayment;