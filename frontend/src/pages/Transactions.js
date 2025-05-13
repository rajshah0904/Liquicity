import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, Table, TableBody, TableCell, TableHead, TableRow, Paper } from '@mui/material';
import { walletAPI } from '../utils/api';
import { useAuth0 } from '@auth0/auth0-react';
import { getCurrencySymbol, formatCurrency } from '../utils/currencyUtils';

export default function Transactions() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const { user } = useAuth0();

  useEffect(() => {
    async function fetchTx() {
      setLoading(true);
      setError(null);
      try {
        const resp = await walletAPI.getAllTransactions();
        setTransactions(resp.data.transactions || []);
      } catch (err) {
        console.error(err);
        setError(err?.response?.data?.detail || err.message || 'Failed to load transactions');
      } finally {
        setLoading(false);
      }
    }
    fetchTx();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Transactions
      </Typography>
      {transactions.length === 0 ? (
        <Typography>No transactions yet.</Typography>
      ) : (
        <Paper sx={{ width: '100%', overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Currency</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((t) => {
                // For Hadeer's account, show EUR
                const displayCurrency = user?.email === 'hadeermotair@gmail.com' ? 'EUR' : t.currency.toUpperCase();
                
                return (
                  <TableRow key={t.transaction_id}>
                    <TableCell>{new Date(t.date).toLocaleString()}</TableCell>
                    <TableCell>{t.description || t.transaction_id}</TableCell>
                    <TableCell>
                      {getCurrencySymbol(displayCurrency, user)}{Number(t.amount).toLocaleString()}
                    </TableCell>
                    <TableCell>{displayCurrency}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Paper>
      )}
    </Box>
  );
} 