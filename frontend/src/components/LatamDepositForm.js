import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    IconButton,
    InputAdornment,
    Paper,
    Stack,
    Step,
    StepLabel,
    Stepper,
    TextField,
    Typography,
    useMediaQuery,
    useTheme
} from '@mui/material';
import { motion } from 'framer-motion';
import React, { useState } from 'react';
import { velafiAPI } from '../utils/api';

const RAIL_INSTRUCTIONS = {
  'BRL': {
    name: 'Pix',
    fields: ['key'],
    instructions: [
      'Open your bank app',
      'Select "Pix Transfer"',
      'Paste the Pix key below',
      'Enter the exact amount shown',
      'Confirm the transfer'
    ]
  },
  'MXN': {
    name: 'SPEI',
    fields: ['clabe'],
    instructions: [
      'Open your bank app',
      'Select "SPEI Transfer"',
      'Enter the CLABE number below',
      'Enter the exact amount shown',
      'Include the reference number in the description',
      'Confirm the transfer'
    ]
  },
  'ARS': {
    name: 'CBU',
    fields: ['cbu', 'alias'],
    instructions: [
      'Open your bank app',
      'Select "Transfer"',
      'Enter the CBU or alias below',
      'Enter the exact amount shown',
      'Confirm the transfer'
    ]
  }
};

export default function LatamDepositForm({
  userRegion,
  onBack,
  onSuccess
}) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    amount: '',
    currency: userRegion.currency.toUpperCase()
  });
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

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

  // Get rail info based on currency
  const railInfo = RAIL_INSTRUCTIONS[form.currency];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // First get a quote
      const quote = await velafiAPI.getQuote({
        fiat_amount: form.amount,
        fiat_currency: form.currency,
        direction: 'BUY',
        country_code: userRegion.country_code
      });

      // Create the order
      const order = await velafiAPI.createOrder({
        direction: 'BUY',
        fiat_amount: form.amount,
        fiat_currency: form.currency,
        country_code: userRegion.country_code
      });

      setOrder(order);
      setStep(1);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err.message || 'Failed to create deposit order');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const steps = ['Enter Amount', 'Bank Transfer', 'Confirmation'];

  return (
    <Box
      component={motion.div}
      variants={pageVariants}
      initial="initial"
      animate="animate"
      sx={{ width: '100%', maxWidth: 600, mx: 'auto' }}
    >
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={2} mb={4}>
        <IconButton onClick={onBack} sx={{ color: 'text.secondary' }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h5" component="h1">
          Deposit {railInfo.name}
        </Typography>
      </Stack>

      {/* Stepper */}
      <Stepper activeStep={step} alternativeLabel sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Step 0: Amount Form */}
      {step === 0 && (
        <motion.div variants={itemVariants}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              borderRadius: 2,
              bgcolor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider'
            }}
          >
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Amount"
                type="number"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      {form.currency}
                    </InputAdornment>
                  )
                }}
                sx={{ mb: 3 }}
              />
              <Button
                fullWidth
                variant="contained"
                type="submit"
                disabled={loading || !form.amount}
                sx={{ mt: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Continue'}
              </Button>
            </form>
          </Paper>
        </motion.div>
      )}

      {/* Step 1: Bank Transfer Instructions */}
      {step === 1 && order && (
        <motion.div variants={itemVariants}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              borderRadius: 2,
              bgcolor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider'
            }}
          >
            <Typography variant="h6" gutterBottom>
              Transfer Instructions
            </Typography>

            {/* Amount to Send */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Amount to Send
              </Typography>
              <Typography variant="h4">
                {form.currency} {form.amount}
              </Typography>
            </Box>

            {/* Rail Details */}
            {railInfo.fields.map((field) => (
              <Box key={field} sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  {field.toUpperCase()}
                </Typography>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                    {order.rail[field]}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(order.rail[field])}
                    color={copied ? 'success' : 'inherit'}
                  >
                    <ContentCopyIcon fontSize="small" />
                  </IconButton>
                </Stack>
              </Box>
            ))}

            {/* Instructions */}
            <Box sx={{ mt: 4 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Steps
              </Typography>
              <ol>
                {railInfo.instructions.map((instruction, i) => (
                  <Typography
                    key={i}
                    component="li"
                    variant="body2"
                    sx={{ mb: 1 }}
                  >
                    {instruction}
                  </Typography>
                ))}
              </ol>
            </Box>

            {/* Important Notes */}
            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2">
                • Send the exact amount shown above
                <br />
                • Transfer must be completed within 30 minutes
                <br />
                • Funds will appear in your account within minutes after transfer
              </Typography>
            </Alert>

            {/* Order ID */}
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                Order ID: {order.order_id}
              </Typography>
            </Box>
          </Paper>
        </motion.div>
      )}
    </Box>
  );
}