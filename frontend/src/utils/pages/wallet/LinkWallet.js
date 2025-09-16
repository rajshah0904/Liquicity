import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, CircularProgress, TextField, Alert, useMediaQuery, useTheme } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { cryptoAPI } from '../../utils/api';
import { useAuth0 } from '@auth0/auth0-react';

export default function LinkWallet() {
  const { user } = useAuth0();
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [qr, setQr] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // detect mobile viewport – on mobile we prefer deep-link over QR
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // optional network selection inputs (future)
  const [chainType] = useState('evm');
  const [chainId] = useState('ethereum');

  // start WalletConnect session on mount
  useEffect(() => {
    let poll;
    async function begin() {
      try {
        setLoading(true);
        const resp = await cryptoAPI.connectWallet({
          user_id: user?.sub || 'me',
          wallet_address: '',
          chain_type: chainType,
          chain_id: chainId,
        });
        const data = resp.data.data;
        setSession(data);
        // persist session id for later transfer creation
        try { localStorage.setItem('wc_session_id', data.session_id); } catch {}
        setQr(data.qr_code_url);
        setStatus(data.status);

        // poll status every 3s
        poll = setInterval(async () => {
          try {
            const s = await cryptoAPI.getSessionStatus(data.session_id);
            setStatus(s.data.status);
            if (s.data.status === 'approved') {
              clearInterval(poll);
              // also persist wallet address if available
              try { if (s.data.wallet_address) localStorage.setItem('wc_wallet_address', s.data.wallet_address); } catch {}
              navigate('/wallet');
            }
          } catch (e) {
            console.error(e);
          }
        }, 3000);
      } catch (e) {
        console.error(e);
        setError(e.response?.data?.error || e.message);
      } finally {
        setLoading(false);
      }
    }
    begin();
    return () => poll && clearInterval(poll);
  }, [user, chainType, chainId, navigate]);

  if (loading) return <Box sx={{ display:'flex',justifyContent:'center',pt:10 }}><CircularProgress/></Box>;

  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box sx={{ maxWidth: 480, mx:'auto', textAlign:'center', mt:4 }}>
      <Typography variant="h4" fontWeight={600} sx={{ mb:2 }}>Link Crypto Wallet</Typography>
      {/* Show QR only on non-mobile devices for convenient cross-device pairing */}
      {!isMobile && qr && (
        <img src={qr} alt="walletconnect qr" style={{ width: 260, height: 260 }} />
      )}

      {/* On mobile, provide a deep-link button that opens the URI directly in the wallet app */}
      {session && isMobile && (
        <Button
          variant="contained"
          color="primary"
          onClick={() => (window.location.href = session.uri)}
          sx={{ mt: 2 }}
        >
          Open in Wallet
        </Button>
      )}
      {session && (
        <>
          <Typography variant="body2" sx={{ mt:2 }} color="text.secondary">Scan the QR code with your wallet or click URI below:</Typography>
          <TextField
            fullWidth
            value={session?.uri || ''}
            sx={{ my:2 }}
            InputProps={{ readOnly:true }}
            onFocus={(e)=>e.target.select()}
          />
        </>
      )}
      <Typography variant="subtitle2" sx={{ mt:1 }}>Status: {status}</Typography>
      <Button onClick={()=>navigate(-1)} sx={{ mt:3 }}>Back</Button>
    </Box>
  );
} 