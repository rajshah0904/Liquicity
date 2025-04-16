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
  Tooltip,
  RadioGroup,
  Radio,
  Autocomplete
} from '@mui/material';
import { 
  Send, 
  AccountBalanceWallet, 
  Check, 
  Person,
  ArrowForward, 
  ArrowForwardIos,
  Info,
  Currency,
  CreditCard,
  AccountBalance
} from '@mui/icons-material';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { SlideUpBox } from '../components/animations/AnimatedComponents';
import { 
  createDepositCheckout, 
  getPaymentMethods,
  processDirectPayment
} from '../utils/stripeUtils';

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
    recipientType: 'any', // 'any' instead of specific types - we'll search across all
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
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(null);
  const [paymentSource, setPaymentSource] = useState('wallet'); // 'wallet', 'card', 'bank'
  const [showPaymentOptions, setShowPaymentOptions] = useState(false);
  const [userSearchResults, setUserSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

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

  useEffect(() => {
    // Only show payment options when wallet balance is insufficient
    if (formData.sourceWalletId && formData.amount) {
      const amount = parseFloat(formData.amount) || 0;
      const fee = amount * 0.01; // 1% fee
      const totalAmount = amount + fee;
      
      const selectedWallet = wallets.find(wallet => wallet.id === formData.sourceWalletId);
      if (selectedWallet && totalAmount > selectedWallet.fiat_balance) {
        // Balance is insufficient, show payment options
        setShowPaymentOptions(true);
        // Clear any error related to insufficient balance
        setError(null);
      } else {
        // Balance is sufficient, don't show external payment options
        setShowPaymentOptions(false);
      }
    }
  }, [formData.sourceWalletId, formData.amount, wallets]);

  useEffect(() => {
    // Check for a saved pending transaction when returning from payment
    const pendingTransaction = localStorage.getItem('pendingTransaction');
    const paymentSuccess = new URLSearchParams(location.search).get('payment_success');
    const paymentCanceled = new URLSearchParams(location.search).get('payment_canceled');
    
    // Only process if we have a pending transaction and a payment status
    if (pendingTransaction && (paymentSuccess || paymentCanceled)) {
      try {
        // Restore the transaction data
        const savedTransaction = JSON.parse(pendingTransaction);
        setFormData(savedTransaction.formData || savedTransaction);
        
        // Also restore recipient info if available
        if (savedTransaction.recipientInfo) {
          setRecipientInfo(savedTransaction.recipientInfo);
        }
        
        // Check if this was a payment from step 2
        const wasFullPayment = savedTransaction.activeStep === 2 && 
                            (savedTransaction.paymentSource === 'card' || 
                             savedTransaction.paymentSource === 'bank' ||
                             savedTransaction.paymentSource === 'wallet_partial');
        
        // First, clean up the pending transaction to prevent issues
        localStorage.removeItem('pendingTransaction');
        
        // Set appropriate message and state based on result
        if (paymentSuccess === 'true') {
          if (wasFullPayment) {
            // This was a full payment that succeeded - complete the transaction
            setSendingFunds(true);
            
            // Get correct form data (could be nested inside formData property)
            const formDataToUse = savedTransaction.formData || savedTransaction;
            
            // Validate that we have recipientInfo
            if (!savedTransaction.recipientInfo || !savedTransaction.recipientInfo.id) {
              setError('Missing recipient information. Please try again or contact support.');
              setActiveStep(1); // Go back to recipient selection step
              setSendingFunds(false);
              return;
            }
            
            // Prevent sending money to yourself with Stripe
            if (currentUser.id === savedTransaction.recipientInfo.id) {
              setError('Cannot send money to yourself using a card payment. The payment was processed but no transfer was made. Please contact support for a refund.');
              setSendingFunds(false);
              return;
            }
            
            // Process the actual transfer to the recipient
            api.post('/payment/transfer', {
              sender_id: currentUser.id,
              recipient_id: savedTransaction.recipientInfo.id,
              amount: parseFloat(formDataToUse.amount),
              source_currency: formDataToUse.currency,
              target_currency: formDataToUse.currency,
              stripe_payment: true,
              payment_source: savedTransaction.paymentSource || 'card',
              transaction_type: savedTransaction.paymentSource ? 
                `${savedTransaction.paymentSource.toUpperCase()}_PAYMENT` : 'CARD_PAYMENT',
              skip_sender_deduction: true, // This prevents double deduction since Stripe already took the money
              use_stablecoin: formDataToUse.useStablecoinBridge || false,
              description: formDataToUse.description || "Payment via Stripe"
            })
            .then(response => {
              // Show success screen
              setSuccess(true);
              setTransactionId(response.data.transaction_id || 'stripe-' + Date.now());
              setSendingFunds(false);
            })
            .catch(err => {
              console.error('Error completing transaction:', err);
              // Enhanced error handling with more detailed information
              let errorMessage = 'Payment was successful, but there was an error completing the transfer.';
              
              // Check for specific error response
              if (err.response && err.response.data) {
                if (err.response.data.detail) {
                  errorMessage += ` Error: ${err.response.data.detail}`;
                } else if (err.response.data.message) {
                  errorMessage += ` Error: ${err.response.data.message}`;
                }
                
                // Log detailed error data for debugging
                console.error('Transfer API error details:', err.response.data);
              }
              
              // Add transaction reference for support
              const transactionRef = Date.now().toString(36);
              errorMessage += ` Please contact support with reference #${transactionRef}.`;
              
              setError(errorMessage);
              setActiveStep(2); // Return to confirmation step
              setSendingFunds(false);
            });
          } else {
            // This was just a payment method setup
            setSuccess('Payment method added successfully. Please continue with your transaction.');
            setActiveStep(savedTransaction.activeStep || 0);
            
            // Refresh payment methods
            fetchPaymentMethods();
          }
        } else if (paymentCanceled === 'true') {
          setError('Payment was canceled. You can try again or use a different payment method.');
          // Return to the confirmation step
          setActiveStep(2);
        } else {
          // No specific status, return to confirmation
          setActiveStep(2);
        }
      } catch (err) {
        console.error('Error restoring transaction:', err);
        setError('Something went wrong processing your payment. Please try again or contact support.');
        setActiveStep(0);
      }
    }
  }, [location.search]);

  useEffect(() => {
    fetchPaymentMethods();
  }, [currentUser]);

  const fetchPaymentMethods = async () => {
    try {
      if (!currentUser?.id) return;
      
      // Fetch the user's payment methods
      const methods = await getPaymentMethods(currentUser.id);
      
      if (methods && methods.length > 0) {
        setPaymentMethods(methods);
        // Set default payment method to the first one
        setSelectedPaymentMethod(methods[0].id);
      } else {
        // Empty array - user has no payment methods
        setPaymentMethods([]);
        setSelectedPaymentMethod(null);
      }
    } catch (err) {
      console.error('Error fetching payment methods:', err);
      setPaymentMethods([]);
      setSelectedPaymentMethod(null);
    }
  };

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
    
    // If same currency, no conversion needed - always use direct path
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
    
    // Only use stablecoin bridge for different currencies
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
        
        // Always select the first wallet
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

  const searchUsers = async (searchTerm) => {
    if (!searchTerm || searchTerm.length < 2) {
      setUserSearchResults([]);
      return;
    }
    
    setIsSearching(true);
    
    try {
      // Unified search endpoint that searches across email, username and ID
      const endpoint = `/user/search?query=${encodeURIComponent(searchTerm)}`;
      
      const response = await api.get(endpoint);
      
      if (response.data && Array.isArray(response.data)) {
        // Filter out current user from results
        const filteredResults = response.data.filter(user => user.id !== currentUser.id);
        setUserSearchResults(filteredResults);
      } else {
        setUserSearchResults([]);
      }
    } catch (error) {
      console.error('Error searching users:', error);
      setUserSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleRecipientInputChange = (e) => {
    const { value } = e.target;
    
    // Update the form data
    setFormData(prev => ({
      ...prev,
      recipientAddress: value
    }));
    
    // Clear any previous errors
    if (formErrors.recipientAddress) {
    setFormErrors(prev => ({
      ...prev,
      recipientAddress: ''
    }));
    }
    
    // Clear recipient info when input changes
    setRecipientInfo(null);
    
    // Search if there's at least 2 characters
    if (value.length >= 2) {
      searchUsers(value);
    }
  };

  const handleUserSelect = (event, selectedUser) => {
    if (!selectedUser) return;
    
    // For display purposes, we'll use whichever identifier is most recognizable
    // but we'll store the user's actual ID for the transaction
    let displayValue = '';
    
    if (selectedUser.username) {
      displayValue = selectedUser.username;
    } else if (selectedUser.email) {
      displayValue = selectedUser.email;
    } else if (selectedUser.id) {
      displayValue = `User #${selectedUser.id}`;
    }
    
    setFormData(prev => ({
      ...prev,
      recipientAddress: displayValue
    }));
    
    // Set recipient info directly
    setRecipientInfo(selectedUser);
        
        // Also fetch recipient's wallet to get their currency
    if (selectedUser.id) {
      fetchRecipientWallet(selectedUser.id);
    }
  };

  const fetchRecipientWallet = async (recipientId) => {
    try {
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
    } catch (error) {
      console.error('Error fetching recipient wallet:', error);
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
    
    // Check for recipient info, which indicates a valid registered user
    if (!recipientInfo || !recipientInfo.id) {
      errors.recipientAddress = 'Please select a valid registered TerraFlow user';
    } else if (recipientInfo.id === currentUser.id) {
      errors.recipientAddress = 'You cannot send money to yourself';
    }
    
    if (!formData.amount || isNaN(formData.amount) || parseFloat(formData.amount) <= 0) {
      errors.amount = 'Please enter a valid amount';
    } else if (paymentSource === 'wallet') {
      // Only check balance if using wallet as payment source
      const selectedWallet = wallets.find(wallet => wallet.id === formData.sourceWalletId);
      if (selectedWallet && selectedWallet.fiat_balance < parseFloat(formData.amount)) {
        errors.amount = 'Insufficient balance. Consider using a card or bank account instead.';
      }
    }
    
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

  const handlePaymentSourceChange = (event) => {
    setPaymentSource(event.target.value);
  };

  const handlePaymentMethodChange = (event) => {
    setSelectedPaymentMethod(event.target.value);
  };

  const handleSubmitPayment = async () => {
    setSendingFunds(true);
    setError(null);

    try {
      // Make sure we have recipient info
      if (!recipientInfo || !recipientInfo.id) {
        throw new Error('Invalid recipient. Please select a valid registered user.');
      }
      
      // Get the selected wallet
      const selectedWallet = wallets.find(wallet => wallet.id === formData.sourceWalletId);
      
      // If user is paying entirely from wallet (has sufficient balance)
      if (paymentSource === 'wallet') {
        // Use existing transfer logic for wallet-to-wallet transfers
        await handleSubmit();
      } 
      // If user is using a combination of wallet + payment method
      else if (paymentSource === 'wallet_partial' && selectedWallet) {
        // Use the wallet balance for partial payment and charge the rest to the payment method
        const walletAmount = selectedWallet.fiat_balance;
        const remainingAmount = parseFloat(formData.amount) - walletAmount;
        
        // Process the transaction using the direct payment utility
        const response = await processDirectPayment({
          ...formData,
          recipient_id: recipientInfo.id, // Add recipient ID
          use_wallet_amount: walletAmount,
          remaining_amount: remainingAmount,
        }, selectedPaymentMethod, paymentSource);
        
        if (response.success) {
          setSuccess(true);
          setTransactionId(response.transaction_id);
      } else {
          throw new Error(response.message || 'Payment failed');
        }
      }
      // If user is paying directly with card or bank without using wallet
      else {
        // Process the direct payment
        const response = await processDirectPayment({
          ...formData,
          recipient_id: recipientInfo.id, // Add recipient ID
          use_wallet_amount: 0,
        }, selectedPaymentMethod, paymentSource);
        
        if (response.success) {
          setSuccess(true);
          setTransactionId(response.transaction_id);
        } else {
          throw new Error(response.message || 'Payment failed');
        }
      }
    } catch (err) {
      console.error('Payment error:', err);
      setError(err.message || 'Failed to process payment');
    } finally {
      setSendingFunds(false);
    }
  };

  const handleSubmit = async () => {
    setSendingFunds(true);
    try {
      const selectedWallet = wallets.find(wallet => wallet.id === formData.sourceWalletId);
      
      // Calculate total amount including fee
      const totalAmount = parseFloat(formData.amount) + estimatedFee;
      
      if (paymentSource === 'wallet') {
        // Directly process wallet payment
      const response = await api.post('/payment/transfer', {
          sender_id: currentUser.id,
          recipient_id: recipientInfo.id,
          amount: totalAmount, // Include fees in the amount
          source_currency: selectedWallet.base_currency || selectedWallet.currency,
          target_currency: formData.currency,
          use_stablecoin: formData.useStablecoinBridge && 
                         (selectedWallet.base_currency || selectedWallet.currency) !== formData.currency,
          stripe_payment: false,
          payment_source: paymentSource,
          skip_sender_deduction: false
      });

      if (response.status === 200) {
        setSuccess(true);
          setTransactionId(response.data.transaction_id);
        }
      } else if (paymentSource === 'card' || paymentSource === 'bank') {
        // Store pending transaction before redirecting to Stripe
        const transactionData = {
          formData: {
            ...formData,
            useStablecoinBridge: formData.useStablecoinBridge || false
          },
          activeStep,
          paymentSource,
          recipientInfo: recipientInfo,
          stripe_payment: true
        };
        
        // Debug log to verify data
        console.log('Saving pending transaction data:', transactionData);
        
        // Ensure all required data is present
        if (!recipientInfo || !recipientInfo.id) {
          throw new Error('Missing recipient information. Please select a valid recipient before proceeding.');
        }
        
        // Don't allow sending money to yourself with a card payment
        if (currentUser.id === recipientInfo.id) {
          throw new Error('Cannot send money to yourself using a card payment. Please select a different recipient.');
        }
        
        localStorage.setItem('pendingTransaction', JSON.stringify(transactionData));
        
        createDepositCheckout(
          Math.round(totalAmount * 100),
          formData.currency.toLowerCase(),
          currentUser,
          true, // Set to true for a payment
          {
            is_payment: true,
            recipient_id: recipientInfo.id,
            stripe_payment: true,
            payment_source: paymentSource,
            transfer_type: 'direct_payment',
            skip_sender_deduction: true // Ensure no wallet deduction
          }
        )
        .then(checkoutUrl => {
          if (checkoutUrl) {
            window.location.href = checkoutUrl;
      } else {
            throw new Error("No checkout URL returned");
          }
        })
        .catch(error => {
          console.error("Failed to create Stripe session:", error);
          setError(`Payment error: ${error.message}`);
          setSendingFunds(false);
          // Void pending transaction if Stripe session fails
          localStorage.removeItem('pendingTransaction');
        });
      }
    } catch (err) {
      console.error('Error during transfer:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(`Failed to process transfer: ${err.response.data.detail}`);
      } else {
        setError('Network error. Please try again later.');
      }
    } finally {
      setSendingFunds(false);
    }
  };

  const handleNext = () => {
    console.log(`handleNext called, activeStep: ${activeStep}, paymentSource: ${paymentSource}`);
    
    if (activeStep === 0) {
      // Move to recipient details step
      setActiveStep(1);
      return;
    } 
    
    if (activeStep === 1) {
      if (!validateForm()) {
        return;
      }
      calculateFee();
      // Move to confirmation step
      setActiveStep(2);
    }
  };

  const handleSend = () => {
    if (activeStep === 2) {
      handleSubmit();
    }
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
    
    // Special message for same currency transfers
    if (sourceCurrency === targetCurrency) {
      return (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="subtitle2">Direct Transfer</Typography>
          <Typography variant="body2">
            Since you're sending in the same currency, no currency conversion is needed.
          </Typography>
        </Alert>
      );
    }
    
    if (conversionPath === 'direct') {
      return (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="subtitle2">Direct Conversion</Typography>
          <Typography variant="body2">
            Your funds will be converted directly from {sourceCurrency} to {targetCurrency}
            without using a stablecoin intermediary.
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
          
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 2 }}>
            <Box textAlign="center">
              <Typography variant="body2" color="text.secondary">Source</Typography>
              <Typography variant="body1" fontWeight="medium">
                {formatCurrency(sourceAmount, sourceCurrency)}
              </Typography>
            </Box>
            
            <ArrowForward color="action" />
            
            <Box textAlign="center">
              <Typography variant="body2" color="text.secondary">Via Stablecoin</Typography>
              <Typography variant="body1" fontWeight="medium">
                {stablecoinAmount.toFixed(2)} USDT
              </Typography>
            </Box>
            
            <ArrowForward color="action" />
            
            <Box textAlign="center">
              <Typography variant="body2" color="text.secondary">Destination</Typography>
              <Typography variant="body1" fontWeight="medium">
                {formatCurrency(targetAmount, targetCurrency)}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption" color="text.secondary">
                Rate: 1 {sourceCurrency} = {(1/stablecoinRates[sourceCurrency]).toFixed(4)} USDT
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Rate: 1 USDT = {stablecoinRates[targetCurrency].toFixed(4)} {targetCurrency}
              </Typography>
            </Box>
          </Box>
      </SlideUpBox>
    );
  };

  const lookupRecipient = async (recipientValue) => {
    if (!recipientValue) recipientValue = formData.recipientAddress;
    
    if (!recipientValue || recipientValue.length < 2) {
      return;
    }
    
    setIsSearching(true);
    
    try {
      // Reset recipient info
      setRecipientInfo(null);
      
      // Try to determine what type of identifier it is
      let endpoint;
      
      // If it's a number, try ID lookup
      if (!isNaN(recipientValue) && parseInt(recipientValue) > 0) {
        endpoint = `/user/profile/${recipientValue}`;
      }
      // Otherwise, use the universal search endpoint
      else {
        endpoint = `/user/search?query=${encodeURIComponent(recipientValue)}&exact=true`;
      }
      
      const response = await api.get(endpoint);
      
      if (response.data) {
        let user;
        
        // If it's an array (from search), take the first exact match
        if (Array.isArray(response.data) && response.data.length > 0) {
          // Find the exact match
          user = response.data.find(u => 
            u.username === recipientValue || 
            u.email === recipientValue
          );
          
          // If no exact match, take first result
          if (!user && response.data.length > 0) {
            user = response.data[0];
          }
        } else {
          // Direct profile response
          user = response.data;
        }
        
        if (user) {
          // Check if user is sending to themselves
          if (user.id === currentUser.id) {
            setFormErrors(prev => ({
              ...prev,
              recipientAddress: 'You cannot send money to yourself'
            }));
            return;
          }
          
          setRecipientInfo(user);
          
          // Also fetch recipient's wallet to get their currency
          fetchRecipientWallet(user.id);
        }
      }
    } catch (error) {
      console.error('Error looking up recipient:', error);
      // Set error for invalid recipient
      setFormErrors(prev => ({
        ...prev,
        recipientAddress: 'Recipient not found'
      }));
    } finally {
      setIsSearching(false);
    }
  };

  const getRecipientOptionLabel = (option) => {
    // If it's just a string (user input), return it
    if (typeof option === 'string') return option;
    
    // If it's a user object, show the most user-friendly format
    return option.email || option.username || `User #${option.id}`;
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
                // Reset success state
                setSuccess(false);
                setActiveStep(0);
                
                // Reset form data to initial state
                setFormData({
                  sourceWalletId: wallets.length > 0 ? wallets[0].id : '',
                  recipientAddress: '',
                  recipientType: 'any',
                  amount: '',
                  currency: wallets.length > 0 ? (wallets[0].base_currency || wallets[0].currency) : 'USD',
                  description: '',
                  isCryptoTransaction: false,
                  cryptoCurrency: 'USDT',
                  useStablecoinBridge: true
                });
                
                // Clear recipient info
                setRecipientInfo(null);
                
                // Clear any errors
                setError(null);
                
                // Reset transaction breakdown
                setTransactionBreakdown(null);
                
                // Reset payment source to wallet
                setPaymentSource('wallet');
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
                  <Autocomplete
            fullWidth
                    options={userSearchResults}
                    loading={isSearching}
                    getOptionLabel={getRecipientOptionLabel}
                    onChange={handleUserSelect}
                    freeSolo
                    renderOption={(props, option) => (
                      <li {...props}>
                        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                          <Typography variant="body1">
                            {option.username || option.email || `User #${option.id}`}
                          </Typography>
                          {option.username && option.email && (
                            <Typography variant="caption" color="text.secondary">
                              {option.email}
                            </Typography>
                          )}
                        </Box>
                      </li>
                    )}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Recipient"
                    error={!!formErrors.recipientAddress}
                        helperText={formErrors.recipientAddress || "Enter username or email of any registered TerraFlow user"}
                        onChange={handleRecipientInputChange}
                        onBlur={() => {
                          // If user manually typed something but didn't select from dropdown
                          if (formData.recipientAddress && !recipientInfo) {
                            lookupRecipient(formData.recipientAddress);
                          }
                        }}
                        placeholder="Enter username or email"
                        InputProps={{
                          ...params.InputProps,
                          endAdornment: (
                            <>
                              {isSearching ? <CircularProgress color="inherit" size={20} /> : null}
                              {params.InputProps.endAdornment}
                            </>
                          ),
                        }}
                      />
                    )}
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
                    <strong>Currency handling:</strong> Money will be sent from your account in {getSelectedWallet()?.base_currency || 'your currency'} {' '}
                    and will be received by the recipient in {formData.currency || 'their base currency'}. {' '}
                    The system will automatically handle the currency conversion using the current exchange rates.
                  </Typography>
                </Alert>
              )}

              {/* Add payment source selection when balance is insufficient */}
              {showPaymentOptions && (
                <>
                  <Grid item xs={12} sx={{ mt: 3 }}>
                    <Divider sx={{ my: 1 }} />
                    
                    {/* Only show insufficient balance warning when balance is actually insufficient */}
                    {getSelectedWallet() && 
                     parseFloat(formData.amount) + estimatedFee > getSelectedWallet().fiat_balance && (
                      <Alert severity="warning" sx={{ mb: 2 }}>
                        Your wallet balance is insufficient for this transaction. Please select a payment method.
                      </Alert>
                    )}
                    
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Payment Method
                    </Typography>
                    
                    <RadioGroup
                      value={paymentSource}
                      onChange={handlePaymentSourceChange}
                      name="payment-source-group"
                    >
                      <FormControlLabel 
                        value="wallet_partial" 
                        control={<Radio />}
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <AccountBalanceWallet sx={{ mr: 1, fontSize: 20 }} />
                            <Typography variant="body2">
                              Use wallet balance + additional payment method
                            </Typography>
                          </Box>
                        }
                        disabled={getSelectedWallet() && parseFloat(formData.amount) <= getSelectedWallet().fiat_balance}
                      />
                      
                      <FormControlLabel 
                        value="card" 
                        control={<Radio />}
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <CreditCard sx={{ mr: 1, fontSize: 20 }} />
                            <Typography variant="body2">
                              Pay directly with credit/debit card
                            </Typography>
                          </Box>
                        }
                      />
                      
                      <FormControlLabel 
                        value="bank" 
                        control={<Radio />}
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <AccountBalance sx={{ mr: 1, fontSize: 20 }} />
                            <Typography variant="body2">
                              Pay directly from bank account
                            </Typography>
                          </Box>
                        }
                      />
                    </RadioGroup>
                    
                    {(paymentSource === 'card' || paymentSource === 'bank' || paymentSource === 'wallet_partial') && (
                      <Box sx={{ mt: 2 }}>
                        {paymentSource === 'wallet_partial' && (
                          <Alert severity="info" sx={{ mt: 2 }}>
                            We'll use your available wallet balance of {formatCurrency(getSelectedWallet()?.fiat_balance, getSelectedWallet()?.currency)} {' '}
                            and charge the remaining {formatCurrency(Math.max(0, parseFloat(formData.amount) - (getSelectedWallet()?.fiat_balance || 0)), formData.currency)} {' '}
                            to your selected payment method.
                          </Alert>
                        )}
                      </Box>
                    )}
                  </Grid>
                </>
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
                onClick={activeStep === steps.length - 1 ? handleSend : handleNext}
                endIcon={activeStep === steps.length - 1 ? <Send /> : null}
                disabled={wallets.length === 0 || sendingFunds}
            >
                {sendingFunds ? "Processing..." : "Send Money"}
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
            <>
              <Typography variant="h6" gutterBottom>
                Your Wallet
              </Typography>
              <Box>
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
                    <Grid item xs={12}>
                        <Card 
                          sx={{ 
                          border: '1px solid',
                            borderColor: 'primary.main',
                          backgroundColor: 'action.selected',
                            transition: 'all 0.3s'
                          }}
                        >
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                            {formatWalletDisplay(wallets[0])}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                </Grid>
              )}
              </Box>
            </>
          )}

          {/* Add payment method selection */}
          <Box sx={{ mt: 4 }}>
            <Divider sx={{ mb: 3 }} />
            
            <Typography variant="h6" gutterBottom>
              Select Payment Method
            </Typography>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Choose how you want to pay for this transaction
            </Typography>
            
            <RadioGroup
              value={paymentSource}
              onChange={handlePaymentSourceChange}
              name="payment-source-group"
            >
              <FormControlLabel 
                value="wallet" 
                control={<Radio />}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AccountBalanceWallet sx={{ mr: 1, fontSize: 20 }} />
                    <Typography variant="body2">
                      Use wallet balance 
                      {getSelectedWallet() && 
                        ` (Available: ${formatCurrency(getSelectedWallet().fiat_balance, getSelectedWallet().currency)})`}
                    </Typography>
                  </Box>
                }
              />
              
              <FormControlLabel 
                value="card" 
                control={<Radio />}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CreditCard sx={{ mr: 1, fontSize: 20 }} />
                    <Typography variant="body2">
                      Pay directly with credit/debit card
                    </Typography>
                  </Box>
                }
              />
              
              <FormControlLabel 
                value="bank" 
                control={<Radio />}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AccountBalance sx={{ mr: 1, fontSize: 20 }} />
                    <Typography variant="body2">
                      Pay directly from bank account
                    </Typography>
                  </Box>
                }
              />
            </RadioGroup>
            
            {(paymentSource === 'card' || paymentSource === 'bank') && (
              <Box sx={{ mt: 2 }}>
                {/* Box for any alerts */}
            </Box>
          )}
          </Box>
          
          {/* Now restore the navigation buttons at the end of the component */}
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
              onClick={activeStep === steps.length - 1 ? handleSend : handleNext}
              endIcon={activeStep === steps.length - 1 ? <Send /> : null}
              disabled={
                wallets.length === 0 || 
                sendingFunds
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