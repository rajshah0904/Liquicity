import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Collapse,
  IconButton,
  Stack,
} from '@mui/material';
import { KeyboardArrowDown, KeyboardArrowUp } from '@mui/icons-material';
import { externalAccountsAPI } from '../../utils/api';

/**
 * BankAccounts page – lets a user:
 *  1. View their Bridge-linked external bank accounts
 *  2. Fetch Plaid Auth / Identity / Balance data on-demand
 *  3. Add a new bank account via Plaid Link (US-only) by reusing Deposit page logic
 */
export default function BankAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Store fetched details keyed by account id
  const [details, setDetails] = useState({});

  // Fetch list on mount
  useEffect(() => {
    async function load() {
      try {
        const resp = await externalAccountsAPI.getAccounts();
        setAccounts(resp.data.accounts || []);
      } catch (e) {
        console.error(e);
        setError(e.response?.data?.detail || e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const fetchDetail = async (id, type) => {
    try {
      setDetails((prev) => ({
        ...prev,
        [id]: { ...(prev[id] || {}), loading: { ...(prev[id]?.loading || {}), [type]: true } },
      }));
      let data;
      if (type === 'balance') data = await externalAccountsAPI.getAccountBalance(id);
      else if (type === 'auth') data = await externalAccountsAPI.getAccountAuth(id);
      else if (type === 'identity') data = await externalAccountsAPI.getAccountIdentity(id);

      setDetails((prev) => ({
        ...prev,
        [id]: {
          ...(prev[id] || {}),
          [type]: data.data,
          loading: { ...(prev[id]?.loading || {}), [type]: false },
        },
      }));
    } catch (e) {
      console.error(e);
      setDetails((prev) => ({
        ...prev,
        [id]: {
          ...(prev[id] || {}),
          error: e.response?.data?.detail || e.message,
          loading: { ...(prev[id]?.loading || {}), [type]: false },
        },
      }));
    }
  };

  if (loading) return <Box sx={{ pt: 10, display: 'flex', justifyContent: 'center' }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ mt: 4 }}>{error}</Alert>;

  return (
    <Box sx={{ maxWidth: 960, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Linked Bank Accounts
      </Typography>
      <Box sx={{ mb: 2 }}>
        <Button variant="contained" onClick={() => (window.location.href = '/wallet/link-bank')}>
          Add Bank Account
        </Button>
      </Box>
      {accounts.length === 0 ? (
        <Alert severity="info">No bank accounts linked yet.</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell />
                <TableCell>Bank</TableCell>
                <TableCell>Last 4</TableCell>
                <TableCell>Currency</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {accounts.map((acc) => (
                <Row
                  key={acc.id}
                  account={acc}
                  detail={details[acc.id]}
                  onFetch={fetchDetail}
                />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

function Row({ account, detail = {}, onFetch }) {
  const [open, setOpen] = useState(false);

  const loadingState = detail.loading || {};

  return (
    <>
      <TableRow>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
          </IconButton>
        </TableCell>
        <TableCell>{account.bank_name || '—'}</TableCell>
        <TableCell>{account.last4 || '—'}</TableCell>
        <TableCell>{account.currency?.toUpperCase() || '—'}</TableCell>
        <TableCell>{account.status || '—'}</TableCell>
        <TableCell align="right">
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              size="small"
              disabled={loadingState.balance}
              onClick={() => onFetch(account.id, 'balance')}
            >
              {loadingState.balance ? 'Loading…' : 'Balance'}
            </Button>
            <Button
              variant="outlined"
              size="small"
              disabled={loadingState.auth}
              onClick={() => onFetch(account.id, 'auth')}
            >
              {loadingState.auth ? 'Loading…' : 'Auth'}
            </Button>
            <Button
              variant="outlined"
              size="small"
              disabled={loadingState.identity}
              onClick={() => onFetch(account.id, 'identity')}
            >
              {loadingState.identity ? 'Loading…' : 'Identity'}
            </Button>
          </Stack>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              {detail.error && <Alert severity="error" sx={{ mb: 2 }}>{detail.error}</Alert>}
              {(!detail.balance && !detail.auth && !detail.identity) && (
                <Typography variant="body2" color="text.secondary">No details fetched yet.</Typography>
              )}
              {detail.balance && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight={600}>Balance</Typography>
                  <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(detail.balance, null, 2)}</pre>
                </Box>
              )}
              {detail.auth && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight={600}>Auth</Typography>
                  <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(detail.auth, null, 2)}</pre>
                </Box>
              )}
              {detail.identity && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight={600}>Identity</Typography>
                  <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(detail.identity, null, 2)}</pre>
                </Box>
              )}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
} 