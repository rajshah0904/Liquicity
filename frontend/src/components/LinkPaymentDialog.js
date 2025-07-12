import React from 'react';
import { Dialog, DialogTitle, DialogContent, Button, Stack } from '@mui/material';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import { useNavigate } from 'react-router-dom';

export default function LinkPaymentDialog({ open, onClose }) {
  const navigate = useNavigate();

  const handleSelect = (type) => {
    if (onClose) onClose();
    if (type === 'bank') {
      navigate('/wallet/link-bank');
    } else if (type === 'wallet') {
      // Placeholder route – implement wallet linking flow separately
      navigate('/wallet/link-wallet');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs">
      <DialogTitle>Select payment method to link</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Button
            variant="outlined"
            startIcon={<AccountBalanceIcon />}
            fullWidth
            onClick={() => handleSelect('bank')}
          >
            Bank account
          </Button>
          <Button
            variant="outlined"
            startIcon={<AccountBalanceWalletIcon />}
            fullWidth
            onClick={() => handleSelect('wallet')}
          >
            Crypto wallet
          </Button>
        </Stack>
      </DialogContent>
    </Dialog>
  );
} 