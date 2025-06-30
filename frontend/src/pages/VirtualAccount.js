import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, Stack } from '@mui/material';
import api from '../utils/api';
import { useUser } from '../context/UserContext';

// Futuristic UI components
import { GradientText } from '../components/ui/ModernUIComponents';

// Reusable dark-themed container
const VABox = ({ children, sx = {} }) => (
  <Box
    sx={{
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 3,
      background: 'rgba(255,255,255,0.02)',
      px: { xs: 3, md: 6 },
      py: { xs: 4, md: 6 },
      ...sx,
    }}
  >
    {children}
  </Box>
);

function VirtualAccountCard({ acc, primary = false, user }) {
  const details = acc.source_deposit_instructions || acc.account_details || {};

  const displayName = user ? user.full_name || user.name : undefined;
  const routingNum =
    details.routing_number ||
    details.bank_routing_number ||
    acc.routing_number ||
    acc.account_routing_number ||
    acc.source?.routing_number;
  const accountNum =
    details.account_number ||
    details.bank_account_number ||
    acc.account_number ||
    acc.source?.account_number;

  const rows = [
    { label: 'Bank name', value: details.bank_name || details.bank || '—' },
    { label: 'Routing number', value: routingNum || '—' },
    { label: 'Account number', value: accountNum || '—' },
  ].filter((r) => r.value !== undefined && r.value !== null);

  if (!primary) {
    return (
      <VABox sx={{ mb: 3 }}>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Account #{acc.id?.slice(0, 6)}…{acc.id?.slice(-4)}
        </Typography>
        {rows.map((row) => (
          <Typography key={row.label} variant="body2" sx={{ fontFamily: 'monospace' }}>
            {row.label}: {row.value}
          </Typography>
        ))}
      </VABox>
    );
  }

  // Primary styled card
  return (
    <VABox sx={{ mb: 4 }}>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        {displayName || details.recipient || details.owner_name || 'Your Liquidity Account'}
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom sx={{ mb: 3, fontWeight: 500 }}>
        {details.bank_name || 'US Bank'}
      </Typography>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 2, sm: 8 }}>
        <Box>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Account Number
          </Typography>
          <Typography variant="h5" sx={{ fontFamily: 'monospace' }}>
            {accountNum || '—'}
          </Typography>
        </Box>
        <Box>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Routing Number
          </Typography>
          <Typography variant="h5" sx={{ fontFamily: 'monospace' }}>
            {routingNum || '—'}
          </Typography>
        </Box>
      </Stack>
    </VABox>
  );
}

export default function VirtualAccountPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const { user } = useUser();

  useEffect(() => {
    async function fetchAccounts() {
      try {
        const resp = await api.get('/virtual_accounts');
        const data = resp.data?.virtual_accounts || resp.data?.data || resp.data || [];
        setAccounts(data);
      } catch (err) {
        console.error(err);
        setError(err?.response?.data?.detail || err.message || 'Failed to load virtual accounts');
      } finally {
        setLoading(false);
      }
    }
    fetchAccounts();
  }, []);

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      {/* Heading & tagline */}
      <Typography variant="h4" component="h1" fontWeight="600" gutterBottom>
        Virtual Account
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }} color="text.secondary">
        Use this US bank account to receive funds in USD from platforms like Upwork, Shopify, Amazon, and more.
      </Typography>
      <Typography variant="body1" sx={{ mb: 4 }} color="text.secondary">
        Funds sent to this virtual account are automatically credited to your Liquicity wallet balance and can be withdrawn at any time.
      </Typography>

      {/* Error / Loading */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      {loading && <CircularProgress />}

      {/* Primary account */}
      {accounts.length > 0 && (
        <VirtualAccountCard
          acc={{
            ...accounts[0],
            account_details: {
              ...accounts[0].account_details,
              recipient: user?.full_name,
            },
          }}
          primary
          user={user}
        />
      )}

      {/* Benefits */}
      <VABox sx={{ mb: 4 }}>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          More About Virtual Accounts
        </Typography>
        <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
          <li>Transfers are currently USD-only via ACH Push or domestic wire.</li>
          <li>Incoming deposits settle in 1-3 US business days.</li>
          <li>You'll be notified by email once funds are credited.</li>
          <li>Fee on deposits are 1.25% of the deposit amount. First deposit is fee-free.</li>
        </Typography>
      </VABox>
    </Box>
  );
} 