import { useState, useEffect, useCallback } from 'react';
import { walletAPI } from '../utils/api';

/**
 * Continually fetch the authenticated user's Bridge wallet and expose it.
 *
 * @param {number} pollMs How often to poll in milliseconds (default 10s)
 * @returns {{wallet: object|null, loading: boolean, refetch: Function}}
 */
export default function useBridgeWallet(pollMs = 10000) {
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchWallet = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return; // wait until token is set by auth flow
      setLoading(true);
      const { data } = await walletAPI.getBridgeWallet();
      setWallet(data);
    } catch (err) {
      console.error('useBridgeWallet: failed to fetch wallet', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWallet(); // initial fetch
    const id = setInterval(fetchWallet, pollMs);
    return () => clearInterval(id);
  }, [fetchWallet, pollMs]);

  return { wallet, loading, refetch: fetchWallet };
} 