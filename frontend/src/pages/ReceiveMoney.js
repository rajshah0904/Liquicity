import React, { useState, useEffect, useRef } from 'react';
import { 
  Container, Box, Paper, Typography, TextField, Button,
  Grid, Card, CardContent, Select, MenuItem, InputLabel,
  FormControl, Divider, IconButton, Alert,
  CircularProgress, Snackbar, Dialog, DialogTitle,
  DialogContent, DialogActions
} from '@mui/material';
import { 
  QrCode, ContentCopy, Share, ArrowBack, 
  WhatsApp, Email, FileCopy, TextSnippet, Download
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { QRCodeCanvas } from 'qrcode.react';
import { SlideUpBox } from '../components/animations/AnimatedComponents';

const ReceiveMoney = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const qrRef = useRef(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [userWallet, setUserWallet] = useState(null);
  
  // Form states
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [description, setDescription] = useState('');
  const [receiverName, setReceiverName] = useState('');
  const [paymentLinkGenerated, setPaymentLinkGenerated] = useState(false);
  const [paymentLink, setPaymentLink] = useState('');
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  
  useEffect(() => {
    if (currentUser) {
      fetchWallet();
    }
  }, [currentUser]);
  
  const fetchWallet = async () => {
    setLoading(true);
    try {
      // Fetch user's main wallet
      const response = await api.get(`/wallet/${currentUser.id}`);
      if (response.status === 200) {
        setUserWallet(response.data);
        
        // Set the default currency from the user's wallet
        if (response.data?.base_currency) {
          setCurrency(response.data.base_currency);
        }
      }
    } catch (err) {
      console.error('Error fetching wallet:', err);
      setError('Failed to load wallet data');
    } finally {
      setLoading(false);
    }
  };
  
  const generatePaymentLink = () => {
    if (!validateForm()) return;
    
    // Create a payment link based on the form inputs
    const baseUrl = window.location.origin;
    const paymentDetails = {
      amount,
      currency,
      description: description || 'Payment request',
      recipient: currentUser.username || currentUser.email || 'user'
    };
    
    // Convert to base64 to include in URL
    const encodedData = btoa(JSON.stringify(paymentDetails));
    const generatedLink = `${baseUrl}/pay?data=${encodedData}`;
    
    setPaymentLink(generatedLink);
    setPaymentLinkGenerated(true);
  };
  
  const validateForm = () => {
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
      setError('Please enter a valid amount');
      return false;
    }
    
    setError(null);
    return true;
  };
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
  };
  
  const downloadQRCode = () => {
    if (!qrRef.current) return;
    
    const canvas = qrRef.current.querySelector('canvas');
    if (!canvas) return;
    
    const url = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = 'terraflow-payment-qr.png';
    link.href = url;
    link.click();
  };
  
  const sharePaymentLink = () => {
    setShareDialogOpen(true);
  };
  
  const formatCurrency = (amount, currencyCode = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 2
    }).format(amount);
  };
  
  const handleShareOption = (method) => {
    // Close dialog
    setShareDialogOpen(false);
    
    // Format message text
    const message = `Payment request for ${formatCurrency(amount, currency)}${description ? ` - ${description}` : ''}. Pay here: ${paymentLink}`;
    
    // Handle different sharing methods
    switch (method) {
      case 'whatsapp':
        window.open(`https://wa.me/?text=${encodeURIComponent(message)}`);
        break;
      case 'email':
        window.open(`mailto:?subject=Payment Request&body=${encodeURIComponent(message)}`);
        break;
      case 'copy':
        copyToClipboard(message);
        break;
      default:
        if (navigator.share) {
          navigator.share({
            title: 'Payment Request',
            text: message,
            url: paymentLink
          });
        } else {
          copyToClipboard(paymentLink);
        }
    }
  };
  
  const renderRequestForm = () => (
    <Box>
      <Box mb={4}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              type="number"
              inputProps={{ min: 0, step: '0.01' }}
              required
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Currency"
              value={currency}
              disabled
              helperText="Your account currency"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Invoice #123, Lunch payment"
              multiline
              rows={2}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Your Name/Business Name (optional)"
              value={receiverName}
              onChange={(e) => setReceiverName(e.target.value)}
              placeholder="How recipient will see you"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Box display="flex" justifyContent="center" mt={2}>
              <Button
                variant="contained"
                size="large"
                onClick={generatePaymentLink}
                startIcon={<QrCode />}
                disabled={loading}
              >
                Generate Payment Request
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
  
  const renderPaymentLink = () => (
    <SlideUpBox>
      <Card>
        <CardContent>
          <Box textAlign="center" my={2}>
            <Typography variant="h6" gutterBottom>
              Payment Request Generated
            </Typography>
            
            <Typography variant="h4" color="primary" gutterBottom>
              {formatCurrency(amount, currency)}
            </Typography>
            
            {description && (
              <Typography variant="body1" color="text.secondary" paragraph>
                {description}
              </Typography>
            )}
          </Box>
          
          <Divider sx={{ my: 3 }} />
          
          <Box ref={qrRef} display="flex" justifyContent="center" my={3}>
            <QRCodeCanvas 
              value={paymentLink}
              size={200}
              level="H"
              renderAs="canvas"
            />
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Payment Link:
            </Typography>
            <Box display="flex" alignItems="center">
              <TextField
                fullWidth
                value={paymentLink}
                variant="outlined"
                size="small"
                InputProps={{ readOnly: true }}
              />
              <IconButton color="primary" onClick={() => copyToClipboard(paymentLink)}>
                <ContentCopy />
              </IconButton>
            </Box>
          </Box>
          
          <Box display="flex" justifyContent="center" gap={2} mt={3}>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={downloadQRCode}
            >
              Download QR
            </Button>
            <Button
              variant="outlined"
              startIcon={<ContentCopy />}
              onClick={() => copyToClipboard(paymentLink)}
            >
              Copy Link
            </Button>
            <Button
              variant="contained"
              startIcon={<Share />}
              onClick={sharePaymentLink}
            >
              Share
            </Button>
          </Box>
          
          <Box textAlign="center" mt={4}>
            <Button
              startIcon={<ArrowBack />}
              onClick={() => setPaymentLinkGenerated(false)}
            >
              Create Another Request
            </Button>
          </Box>
        </CardContent>
      </Card>
    </SlideUpBox>
  );
  
  return (
    <Container maxWidth="md">
      <Box py={4}>
        <Box mb={4}>
          <Typography variant="h4" display="flex" alignItems="center">
            <QrCode sx={{ mr: 1 }} />
            Receive Money
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Generate payment requests in your currency
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Snackbar
          open={Boolean(success)}
          autoHideDuration={3000}
          onClose={() => setSuccess(null)}
          message={success}
        />
        
        <Paper sx={{ p: 3, mb: 4 }}>
          {loading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              {paymentLinkGenerated ? renderPaymentLink() : renderRequestForm()}
            </>
          )}
        </Paper>
        
        {/* Share Dialog */}
        <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)}>
          <DialogTitle>Share Payment Request</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<WhatsApp />}
                  onClick={() => handleShareOption('whatsapp')}
                >
                  WhatsApp
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Email />}
                  onClick={() => handleShareOption('email')}
                >
                  Email
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<TextSnippet />}
                  onClick={() => handleShareOption('copy')}
                >
                  Copy Text
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<FileCopy />}
                  onClick={() => handleShareOption('link')}
                >
                  Copy Link
                </Button>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShareDialogOpen(false)}>Cancel</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default ReceiveMoney; 