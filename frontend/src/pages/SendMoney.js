import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Grid, 
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Divider,
  FormControlLabel,
  Switch,
  LinearProgress,
  Tooltip
} from '@mui/material';
import { 
  Send, 
  AccountBalanceWallet, 
  Check, 
  Person,
  ArrowForward, 
  ArrowForwardIos,
  Info,
  Currency
} from '@mui/icons-material';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { SlideUpBox } from '../components/animations/AnimatedComponents';

const SendMoney = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentUser, isAuthenticated } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sendingFunds, setSendingFunds] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [transactionId, setTransactionId] = useState(null);
  const [formData, setFormData] = useState({
    sourceWalletId: '',
    recipientAddress: '',
    amount: '',
    currency: 'USD',
    description: '',
    isCryptoTransaction: false,
    cryptoCurrency: 'USDT',
    useStablecoinBridge: true // Default to using stablecoin as intermediary
  });
  const [formErrors, setFormErrors] = useState({});
  const [conversionRate, setConversionRate] = useState(null);
  const [stablecoinRates, setStablecoinRates] = useState({
    USD: 1.0,
    EUR: 0.93,
    GBP: 0.79,
    JPY: 0.0067
  });
  const [estimatedFee, setEstimatedFee] = useState(0);
  const [recipientInfo, setRecipientInfo] = useState(null);
  const [transactionBreakdown, setTransactionBreakdown] = useState(null);

  const steps = ['Select wallet', 'Enter recipient', 'Confirm transfer'];

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: '/send' } });
      return;
    }
    
    // Check if we should pre-select crypto transaction option
    if (location.state?.cryptoPreSelected) {
      setFormData(prev => ({
        ...prev,
        isCryptoTransaction: true,
        cryptoCurrency: 'BTC' // Default to Bitcoin
      }));
    }
    
    fetchWallets();
  }, [isAuthenticated, navigate, location]);

  useEffect(() => {
    if (formData.sourceWalletId && formData.currency) {
      const selectedWallet = wallets.find(wallet => wallet.id === formData.sourceWalletId);
      if (selectedWallet && selectedWallet.base_currency !== formData.currency) {
        fetchConversionRate(selectedWallet.base_currency || selectedWallet.currency, formData.currency);
      } else {
        setConversionRate(null);
      }
      
      // Calculate transaction breakdown when values change
      calculateTransactionBreakdown();
    }
  }, [formData.sourceWalletId, formData.currency, formData.amount, formData.useStablecoinBridge, wallets]);

  const calculateTransactionBreakdown = () => {
    if (!formData.amount || isNaN(formData.amount) || parseFloat(formData.amount) <= 0) {
      setTransactionBreakdown(null);
      return;
    }
    
    const selectedWallet = wallets.find(wallet => wallet.id === formData.sourceWalletId);
    if (!selectedWallet) {
      setTransactionBreakdown(null);
      return;
    }
    
    const sourceAmount = parseFloat(formData.amount);
    const sourceCurrency = selectedWallet.base_currency || selectedWallet.currency || 'USD';
    const targetCurrency = formData.currency;
    
    // If same currency, no conversion needed
    if (sourceCurrency === targetCurrency) {
      setTransactionBreakdown({
        sourceAmount,
        sourceCurrency,
        targetAmount: sourceAmount,
        targetCurrency,
        conversionPath: 'direct',
        fee: sourceAmount * 0.005, // 0.5% fee
        total: sourceAmount * 1.005
      });
      return;
    }
    
    if (formData.useStablecoinBridge) {
      // Fiat → Stablecoin → Fiat conversion
      // Calculate using stablecoin as intermediary
      const sourceToStablecoin = sourceAmount / stablecoinRates[sourceCurrency];
      const stablecoinToTarget = sourceToStablecoin * stablecoinRates[targetCurrency];
      
      const fee = stablecoinToTarget * 0.01; // 1% fee for cross-currency
      
      setTransactionBreakdown({
        sourceAmount,
        sourceCurrency,
        stablecoinAmount: sourceToStablecoin,
        targetAmount: stablecoinToTarget,
        targetCurrency,
        conversionPath: 'stablecoin',
        fee,
        total: stablecoinToTarget + fee
      });
    } else {
      // Direct conversion without stablecoin
      const directRate = conversionRate || 1;
      const targetAmount = sourceAmount * directRate;
      const fee = targetAmount * 0.02; // 2% fee for direct conversion (higher)
      
      setTransactionBreakdown({
        sourceAmount,
        sourceCurrency,
        targetAmount,
        targetCurrency,
        conversionPath: 'direct',
        fee,
        total: targetAmount + fee
      });
    }
  };

  const fetchWallets = async () => {
    setLoading(true);
    try {
      if (!currentUser || !currentUser.id) {
        console.error('Cannot fetch wallets: no current user ID');
        setError('User authentication error. Please log in again.');
        setWallets([]);
        setLoading(false);
        return;
      }
      
      console.log('Fetching wallets for user:', currentUser.id);
      
      const response = await api.get(`/wallet/${currentUser.id}`);
      
      if (response.data) {
        const walletsData = Array.isArray(response.data) ? response.data : [response.data];
        
        const validWallets = walletsData.filter(wallet => {
          if (!wallet) return false;
          if (wallet.id == null) return false;
          
          return wallet.user_id === currentUser.id;
        });
        
        console.log(`Found ${validWallets.length} valid wallets for user ${currentUser.id}`);
        
        setWallets(validWallets);
        
        if (validWallets.length > 0) {
          setFormData(prev => ({
            ...prev,
            sourceWalletId: validWallets[0].id,
            currency: validWallets[0].base_currency || validWallets[0].currency
          }));
        }
      } else {
        console.warn('No wallet data returned from API');
        setWallets([]);
      }
    } catch (err) {
      console.error('Error fetching wallets:', err);
      setError('Failed to load wallets. Please try again.');
      setWallets([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchConversionRate = async (fromCurrency, toCurrency) => {
    if (fromCurrency === toCurrency) {
      setConversionRate(1);
      return;
    }
    
    try {
      const response = await api.get(`/currency/rate/${fromCurrency}/${toCurrency}/`);
      setConversionRate(response.data.rate);
    } catch (err) {
      console.error('Error fetching conversion rate:', err);
      setConversionRate(null);
    }
  };

  const handleRecipientChange = (e) => {
    const value = e.target.value;
    setFormData(prevState => ({
      ...prevState,
      recipientAddress: value
    }));
    
    setRecipientInfo(null);
    
    // Reset any errors
    setFormErrors(prev => ({
      ...prev,
      recipientAddress: ''
    }));
    
    // Look up recipient when a valid ID is entered
    if (value && !isNaN(value) && parseInt(value) > 0) {
      lookupRecipient(value);
    }
  };
  
  const lookupRecipient = async (recipientId) => {
    if (!recipientId) recipientId = formData.recipientAddress;
    
    try {
      // Reset recipient info
      setRecipientInfo(null);
      
      if (!recipientId || isNaN(recipientId)) {
        return;
      }
      
      const response = await api.get(`/user/profile/${recipientId}`);
      if (response.data) {
        setRecipientInfo(response.data);
        
        // Also fetch recipient's wallet to get their currency
        const walletResponse = await api.get(`/wallet/${recipientId}`);
        if (walletResponse.data) {
          const recipientWallet = walletResponse.data;
          const recipientCurrency = recipientWallet.base_currency || recipientWallet.currency || 'USD';
          
          // Set transaction target currency to match recipient's currency
          setFormData(prevState => ({
            ...prevState,
            currency: recipientCurrency
          }));
        }
      }
    } catch (error) {
      console.error('Error looking up recipient:', error);
      // Not setting error here, as recipient might not exist yet
    }
  };

  const calculateFee = () => {
    const amount = parseFloat(formData.amount) || 0;
    const feeRate = 0.01;
    const calculatedFee = amount * feeRate;
    
    setEstimatedFee(calculatedFee);
    return calculatedFee;
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.sourceWalletId) {
      errors.sourceWalletId = 'Please select a source wallet';
    }
    
    if (!formData.recipientAddress) {
      errors.recipientAddress = 'Please enter a recipient address or ID';
    } else if (isNaN(formData.recipientAddress)) {
      errors.recipientAddress = 'Recipient must be a valid user ID';
    }
    
    if (!formData.amount || isNaN(formData.amount) || parseFloat(formData.amount) <= 0) {
      errors.amount = 'Please enter a valid amount';
    } else {
      const selectedWallet = wallets.find(wallet => wallet.id === formData.sourceWalletId);
      if (selectedWallet && selectedWallet.fiat_balance < parseFloat(formData.amount)) {
        errors.amount = 'Insufficient balance';
      }
    }
    
    // Currency validation is no longer needed since we use recipient's currency
    
    if (formData.isCryptoTransaction && !formData.cryptoCurrency) {
      errors.cryptoCurrency = 'Please select a cryptocurrency';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: null
      });
    }
  };

  const handleSubmit = async () => {
    setSendingFunds(true);
    setError(null);
    
    try {
      if (!isAuthenticated || !currentUser || !currentUser.id) {
        throw new Error('You must be logged in to send funds');
      }
      
      const selectedWallet = wallets.find(wallet => wallet.id === formData.sourceWalletId);
      if (!selectedWallet || selectedWallet.user_id !== currentUser.id) {
        throw new Error('Invalid source wallet selected');
      }

      // Handle different transaction types
      let response;
      
      if (formData.isCryptoTransaction) {
        // For crypto transactions, use the crypto endpoint
        response = await api.post('/transaction/crypto/', {
          sender_id: currentUser.id,
          recipient_id: parseInt(formData.recipientAddress), // Assuming this is a user ID
          amount: parseFloat(formData.amount),
          crypto_currency: formData.cryptoCurrency,
          description: formData.description || 'Crypto transfer'
        });
      } else {
        // For regular transactions, use the standard endpoint with automatic stablecoin conversion
        // Always use the sender's and recipient's base currencies
        response = await api.post('/payment/transfer', {
          sender_id: currentUser.id,
          recipient_id: parseInt(formData.recipientAddress), // Assuming this is a user ID
          amount: parseFloat(formData.amount),
          source_currency: selectedWallet.base_currency || selectedWallet.currency,
          target_currency: formData.currency, // This is set to recipient's currency by lookupRecipient()
          description: formData.description || 'Standard transfer',
          use_stablecoin: formData.useStablecoinBridge // Pass the stablecoin bridge option
        });
      }
      
      setSuccess(true);
      setTransactionId(response.data.transaction_id);
      
      setFormData({
        sourceWalletId: '',
        recipientAddress: '',
        amount: '',
        currency: 'USD',
        description: '',
        isCryptoTransaction: false,
        cryptoCurrency: 'USDT',
        useStablecoinBridge: true
      });
    } catch (err) {
      console.error('Error sending funds:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to send funds. Please try again.');
    } finally {
      setSendingFunds(false);
    }
  };

  const handleNext = () => {
    if (activeStep === 0) {
      if (!formData.sourceWalletId) {
        setFormErrors(prev => ({ ...prev, sourceWalletId: 'Please select a source wallet' }));
        return;
      }
    } else if (activeStep === 1) {
      if (!validateForm()) {
        return;
      }
      calculateFee();
      lookupRecipient();
    } else if (activeStep === 2) {
      handleSubmit();
      return;
    }
    
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const formatCurrency = (amount, currency = 'USD') => {
    if (amount == null) return 'N/A';
    
    try {
      // Handle cryptocurrencies which aren't valid ISO 4217 currency codes
      if (['USDT', 'BTC', 'ETH', 'USDC'].includes(currency)) {
        return `${parseFloat(amount || 0).toFixed(2)} ${currency}`;
      }
      
      // Use Intl.NumberFormat for standard currencies
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency
      }).format(amount || 0);
    } catch (error) {
      console.error("Error formatting currency:", error);
      return `${parseFloat(amount || 0).toFixed(2)} ${currency}`;
    }
  };

  const getSelectedWallet = () => {
    return wallets.find(wallet => wallet.id === formData.sourceWalletId);
  };

  const calculateTotal = () => {
    const amount = parseFloat(formData.amount) || 0;
    return amount + estimatedFee;
  };

  const formatWalletDisplay = (wallet) => {
    if (!wallet) return 'Unknown Wallet';
    
    return (
      <Box>
        <Typography variant="body1" component="span" fontWeight="medium">
          {currentUser.username}'s Wallet
        </Typography>
        <Typography variant="body2" component="div" color="text.secondary">
          {formatCurrency(wallet.fiat_balance, wallet.base_currency || wallet.currency)} • {wallet.base_currency || wallet.currency}
          {wallet.stablecoin_balance > 0 && ` • ${formatCurrency(wallet.stablecoin_balance, 'USDT')} USDT`}
        </Typography>
      </Box>
    );
  };

  const getRecipientDisplayName = (recipient) => {
    if (!recipient) return '';
    
    try {
      const name = recipient.name || recipient.username || '';
      const address = recipient.wallet_address || recipient.address || '';
      
      if (name) {
        return `${name} (${address ? address.substring(0, 8) + '...' : 'No address'})`;
      }
      
      return address ? address.substring(0, 12) + '...' : 'Unknown recipient';
    } catch (error) {
      console.error('Error getting recipient display name:', error);
      return 'Unknown recipient';
    }
  };

  const renderWalletOptions = () => {
    if (!wallets || wallets.length === 0) {
      return [
        <MenuItem key="no-wallets" value="" disabled>
          No wallets available
        </MenuItem>
      ];
    }
    
    return wallets.map(wallet => {
      try {
        if (!wallet) return null;
        
        const id = wallet.id != null ? wallet.id : '';
        if (id === '') return null;
        
        const balance = wallet.fiat_balance || wallet.balance || 0;
        const currency = wallet.base_currency || wallet.currency || 'USD'; 
        const walletAddress = wallet.blockchain_address || wallet.wallet_address || wallet.address || '';
        const displayAddress = walletAddress && typeof walletAddress === 'string' && walletAddress.length >= 6 
          ? `${walletAddress.substring(0, 6)}...` 
          : id.toString().substring(0, 6);
        
        return (
          <MenuItem key={id} value={id}>
            {`${displayAddress} (${balance} ${currency})`}
          </MenuItem>
        );
      } catch (error) {
        console.error('Error rendering wallet option:', error, wallet);
        return null;
      }
    }).filter(Boolean);
  };

  const renderConversionProcess = () => {
    if (!transactionBreakdown || formData.isCryptoTransaction) return null;
    
    const { sourceAmount, sourceCurrency, stablecoinAmount, targetAmount, targetCurrency, conversionPath } = transactionBreakdown;
    
    if (conversionPath === 'direct' || sourceCurrency === targetCurrency) {
      return (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="subtitle2">Direct Transfer</Typography>
          <Typography variant="body2">
            Since you're sending in the same currency or using direct conversion, 
            no stablecoin intermediary is needed.
          </Typography>
        </Alert>
      );
    }
    
    return (
      <SlideUpBox>
        <Box sx={{ mt: 3, mb: 4, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
          <Typography variant="subtitle1" gutterBottom>
            Cross-Currency Transfer Process
            <Tooltip title="We use stablecoins as an intermediary to provide better exchange rates and transparent conversions">
              <Info fontSize="small" color="primary" sx={{ ml: 1, verticalAlign: 'middle' }} />
            </Tooltip>
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', my: 3 }}>
            <Box sx={{ textAlign: 'center', minWidth: '100px' }}>
              <Typography variant="subtitle2">
                {formatCurrency(sourceAmount, sourceCurrency)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Source
              </Typography>
            </Box>
            
            <ArrowForward color="primary" />
            
            <Box sx={{ textAlign: 'center', minWidth: '100px' }}>
              <Typography variant="subtitle2">
                {stablecoinAmount.toFixed(2)} USDT
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Stablecoin
              </Typography>
            </Box>
            
            <ArrowForward color="primary" />
            
            <Box sx={{ textAlign: 'center', minWidth: '100px' }}>
              <Typography variant="subtitle2">
                {formatCurrency(targetAmount, targetCurrency)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Destination
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2">
              Your money will be converted from {sourceCurrency} to USDT, then from USDT to {targetCurrency}.
              This provides better rates and transparency compared to direct conversion.
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Rate: 1 {sourceCurrency} = {(1/stablecoinRates[sourceCurrency]).toFixed(4)} USDT
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Rate: 1 USDT = {stablecoinRates[targetCurrency].toFixed(4)} {targetCurrency}
              </Typography>
            </Box>
          </Box>
          
          <FormControlLabel
            control={
              <Switch
                checked={formData.useStablecoinBridge}
                onChange={(e) => setFormData({
                  ...formData,
                  useStablecoinBridge: e.target.checked
                })}
              />
            }
            label="Use stablecoin bridge (recommended for better rates)"
            sx={{ mt: 2 }}
          />
        </Box>
      </SlideUpBox>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (success) {
    return (
      <Container maxWidth="md">
        <Paper sx={{ p: 4, mt: 4, textAlign: 'center' }}>
          <Check sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Transfer Successful!
          </Typography>
          <Typography variant="body1" paragraph>
            Your transfer has been successfully initiated. Transaction ID: {transactionId}
          </Typography>
          <Box mt={4}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={() => navigate('/dashboard')}
            >
              Back to Dashboard
            </Button>
            <Button 
              variant="outlined" 
              sx={{ ml: 2 }}
              onClick={() => {
                setSuccess(false);
                setActiveStep(0);
              }}
            >
              Send Another Payment
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md">
        <Paper sx={{ p: 4, mt: 4, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            Authentication Required
          </Typography>
          <Typography variant="body1" paragraph>
            You must be logged in to send money.
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => navigate('/login', { state: { from: '/send' } })}
          >
            Login
          </Button>
        </Paper>
      </Container>
    );
  }

  if (activeStep === 1) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Send Money
            </Typography>
            
            <Stepper activeStep={activeStep} sx={{ mb: 4, mt: 3 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}
            
            <Box>
              <Typography variant="h6" gutterBottom>
                Enter Recipient Details
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Recipient Address"
                    name="recipientAddress"
                    value={formData.recipientAddress}
                    onChange={handleRecipientChange}
                    error={!!formErrors.recipientAddress}
                    helperText={formErrors.recipientAddress}
                    onBlur={lookupRecipient}
                  />
                </Grid>
                
                {recipientInfo && (
                  <Grid item xs={12}>
                    <Alert severity="info" icon={<Person />}>
                      Recipient: {getRecipientDisplayName(recipientInfo)}
                    </Alert>
                  </Grid>
                )}
                
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.isCryptoTransaction}
                          onChange={(e) => setFormData({
                            ...formData,
                            isCryptoTransaction: e.target.checked
                          })}
                          name="isCryptoTransaction"
                        />
                      }
                      label="Send as cryptocurrency"
                    />
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Amount"
                    name="amount"
                    type="number"
                    value={formData.amount}
                    onChange={handleInputChange}
                    error={!!formErrors.amount}
                    helperText={formErrors.amount}
                    InputProps={{
                      inputProps: { min: 0, step: "0.01" }
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  {formData.isCryptoTransaction ? (
                    <FormControl fullWidth error={!!formErrors.cryptoCurrency}>
                      <InputLabel id="crypto-currency-select-label">Cryptocurrency</InputLabel>
                      <Select
                        labelId="crypto-currency-select-label"
                        id="crypto-currency-select"
                        name="cryptoCurrency"
                        value={formData.cryptoCurrency}
                        onChange={handleInputChange}
                        label="Cryptocurrency"
                      >
                        <MenuItem value="USDT">USDT (Tether)</MenuItem>
                        <MenuItem value="BTC">BTC (Bitcoin)</MenuItem>
                        <MenuItem value="ETH">ETH (Ethereum)</MenuItem>
                        <MenuItem value="USDC">USDC (USD Coin)</MenuItem>
                      </Select>
                      {formErrors.cryptoCurrency && (
                        <FormHelperText>{formErrors.cryptoCurrency}</FormHelperText>
                      )}
                    </FormControl>
                  ) : (
                    <TextField
                      fullWidth
                      label="Currency"
                      value={formData.currency || "Will use recipient's currency"}
                      disabled
                      helperText="Transfers are processed in the recipient's currency"
                    />
                  )}
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description (Optional)"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    multiline
                    rows={2}
                  />
                </Grid>
              </Grid>
              
              {renderConversionProcess()}
              
              {!formData.isCryptoTransaction && conversionRate && formData.amount && (
                <Alert severity="info" sx={{ mt: 3 }}>
                  You're sending {formatCurrency(formData.amount, formData.currency)}. 
                  This will convert to approximately {formatCurrency(
                    parseFloat(formData.amount) / conversionRate, 
                    getSelectedWallet()?.currency
                  )} from your wallet.
                </Alert>
              )}
              
              {formData.isCryptoTransaction && formData.amount && (
                <Alert severity="info" sx={{ mt: 3 }}>
                  You're sending {formatCurrency(formData.amount, formData.cryptoCurrency)} directly as cryptocurrency.
                  This transaction will use the blockchain network and may take longer to process than regular transfers.
                </Alert>
              )}
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
              <Button
                disabled={activeStep === 0}
                onClick={handleBack}
                variant="outlined"
              >
                Back
              </Button>
              <Button
                variant="contained"
                onClick={handleNext}
                endIcon={activeStep === steps.length - 1 ? <Send /> : null}
                disabled={
                  wallets.length === 0 || 
                  sendingFunds || 
                  (activeStep === 0 && !formData.sourceWalletId)
                }
              >
                {sendingFunds ? (
                  <>
                    <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                    Processing...
                  </>
                ) : activeStep === steps.length - 1 ? (
                  'Send Money'
                ) : (
                  'Next'
                )}
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    );
  }
  
  if (activeStep === 2) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Send Money
            </Typography>
            
            <Stepper activeStep={activeStep} sx={{ mb: 4, mt: 3 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}
            
            <Box>
              <Typography variant="h6" gutterBottom>
                Review and Confirm
              </Typography>
              
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        From
                      </Typography>
                      <Typography variant="body1">
                        {formatWalletDisplay(getSelectedWallet())}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        To
                      </Typography>
                      <Typography variant="body1">
                        {getRecipientDisplayName(recipientInfo)}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12}>
                      <Divider sx={{ my: 1 }} />
                    </Grid>
                    
                    {transactionBreakdown && !formData.isCryptoTransaction && 
                      transactionBreakdown.conversionPath === 'stablecoin' && (
                      <>
                        <Grid item xs={12}>
                          <Typography variant="subtitle2" color="text.secondary">
                            Conversion Flow
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {formatCurrency(transactionBreakdown.sourceAmount, transactionBreakdown.sourceCurrency)}
                              </Typography>
                            </Box>
                            <ArrowForwardIos sx={{ mx: 1, fontSize: 12, color: 'text.secondary' }} />
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {transactionBreakdown.stablecoinAmount.toFixed(2)} USDT
                              </Typography>
                            </Box>
                            <ArrowForwardIos sx={{ mx: 1, fontSize: 12, color: 'text.secondary' }} />
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {formatCurrency(transactionBreakdown.targetAmount, transactionBreakdown.targetCurrency)}
                              </Typography>
                            </Box>
                          </Box>
                        </Grid>
                        <Grid item xs={12}>
                          <Divider sx={{ my: 1 }} />
                        </Grid>
                      </>
                    )}
                    
                    <Grid item xs={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Amount
                      </Typography>
                      <Typography variant="h6">
                        {formatCurrency(formData.amount, formData.currency)}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Fee
                      </Typography>
                      <Typography variant="body1">
                        {formatCurrency(estimatedFee, formData.currency)}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12}>
                      <Divider sx={{ my: 1 }} />
                    </Grid>
                    
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Total
                      </Typography>
                      <Typography variant="h5">
                        {formatCurrency(calculateTotal(), formData.currency)}
                      </Typography>
                    </Grid>
                    
                    {formData.description && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Description
                        </Typography>
                        <Typography variant="body1">
                          {formData.description}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
              
              <Alert severity="warning" sx={{ mb: 3 }}>
                Please review the transaction details carefully. All transactions are final and cannot be reversed.
              </Alert>

              {/* Add currency conversion info */}
              {!formData.isCryptoTransaction && (
                <Alert severity="info" sx={{ mt: 2, mb: 3 }}>
                  <Typography variant="body2">
                    <strong>Currency handling:</strong> Money will be sent from your account in {getSelectedWallet()?.base_currency || 'your currency'} 
                    and will be received by the recipient in {formData.currency || 'their base currency'}. 
                    The system will automatically handle the currency conversion using the current exchange rates.
                  </Typography>
                </Alert>
              )}
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
              <Button
                disabled={activeStep === 0}
                onClick={handleBack}
                variant="outlined"
              >
                Back
              </Button>
              <Button
                variant="contained"
                onClick={handleNext}
                endIcon={activeStep === steps.length - 1 ? <Send /> : null}
                disabled={
                  wallets.length === 0 || 
                  sendingFunds || 
                  (activeStep === 0 && !formData.sourceWalletId)
                }
              >
                {sendingFunds ? (
                  <>
                    <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                    Processing...
                  </>
                ) : activeStep === steps.length - 1 ? (
                  'Send Money'
                ) : (
                  'Next'
                )}
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Send Money
          </Typography>
          
          <Stepper activeStep={activeStep} sx={{ mb: 4, mt: 3 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          {activeStep === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Select Source Wallet
              </Typography>
              
              {wallets.length === 0 ? (
                <Box textAlign="center" py={3}>
                  <AccountBalanceWallet sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No Wallets Found
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    You need to create a wallet before you can send funds.
                  </Typography>
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/wallet')}
                  >
                    Go to Wallet
                  </Button>
                </Box>
              ) : (
                <Grid container spacing={3}>
                  {wallets.map((wallet) => {
                    if (!wallet || wallet.id == null) return null;
                    
                    if (wallet.user_id !== currentUser.id) return null;
                    
                    return (
                      <Grid item xs={12} sm={6} key={wallet.id}>
                        <Card 
                          sx={{ 
                            cursor: 'pointer',
                            border: formData.sourceWalletId === wallet.id ? 2 : 0,
                            borderColor: 'primary.main',
                            transition: 'all 0.3s'
                          }}
                          onClick={() => setFormData(prev => ({ 
                            ...prev, 
                            sourceWalletId: wallet.id,
                            currency: wallet.currency
                          }))}
                        >
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              {formatWalletDisplay(wallet)}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    );
                  })}
                </Grid>
              )}
              
              {formErrors.sourceWalletId && (
                <FormHelperText error>{formErrors.sourceWalletId}</FormHelperText>
              )}
            </Box>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
              variant="outlined"
            >
              Back
            </Button>
            <Button
              variant="contained"
              onClick={handleNext}
              endIcon={activeStep === steps.length - 1 ? <Send /> : null}
              disabled={
                wallets.length === 0 || 
                sendingFunds || 
                (activeStep === 0 && !formData.sourceWalletId)
              }
            >
              {sendingFunds ? (
                <>
                  <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                  Processing...
                </>
              ) : activeStep === steps.length - 1 ? (
                'Send Money'
              ) : (
                'Next'
              )}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default SendMoney; 