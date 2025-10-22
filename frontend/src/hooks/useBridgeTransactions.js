import { useState, useEffect, useCallback } from 'react';
import { walletAPI } from '../utils/api';

export default function useBridgeTransactions() {
  const [txns, setTxns] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTxns = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return; // wait for token before hitting API
      setLoading(true);
      const { data } = await walletAPI.getAllTransactions();
      setTxns(data.data || []);
    } catch (e) {
      console.error('Failed to fetch transactions', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTxns(); // initial fetch only, no polling
  }, [fetchTxns]);

  return { txns, loading, refetch: fetchTxns };
} 