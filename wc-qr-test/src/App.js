import React, { useState, useEffect } from 'react';
import QRCode from 'qrcode.react';
import axios from 'axios';

function App() {
  const [formData, setFormData] = useState({
    backendUrl: 'http://localhost:8000',
    userId: 'test-user-123',
    walletAddress: '',
    chainType: 'evm',
    chainId: 'ethereum'
  });
  
  const [sessionData, setSessionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);

  // Chain options based on your backend
  const chainOptions = {
    evm: [
      { value: 'ethereum', label: 'Ethereum (Chain ID: 1)' },
      { value: 'polygon', label: 'Polygon (Chain ID: 137)' },
      { value: 'base', label: 'Base (Chain ID: 8453)' },
      { value: 'arbitrum', label: 'Arbitrum (Chain ID: 42161)' },
      { value: 'optimism', label: 'Optimism (Chain ID: 10)' }
    ],
    solana: [
      { value: 'solana', label: 'Solana Mainnet' }
    ]
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const createSession = async () => {
    setLoading(true);
    setError(null);
    setSessionData(null);
    setStatus(null);

    try {
      // For testing purposes, we'll need to handle authentication
      // Since your backend requires Auth0 JWT, we'll add a note about this
      const response = await axios.post(
        `${formData.backendUrl}/api/crypto/wallet/connect`,
        {
          user_id: formData.userId,
          wallet_address: formData.walletAddress || '',
          chain_type: formData.chainType,
          chain_id: formData.chainId
        },
        {
          headers: {
            'Content-Type': 'application/json',
            // Note: You'll need to add Auth0 JWT token here for production
            // 'Authorization': `Bearer ${authToken}`
          }
        }
      );

      if (response.data.success) {
        setSessionData(response.data.data);
        setStatus('Session created successfully! Scan the QR code with your wallet.');
        
        // Start polling for session status
        startPolling(response.data.data.session_id);
      } else {
        setError('Failed to create session');
      }
    } catch (err) {
      console.error('Error creating session:', err);
      if (err.response?.status === 401) {
        setError('Authentication required. Please add Auth0 JWT token to test.');
      } else if (err.response?.data?.detail) {
        setError(`Error: ${err.response.data.detail.error || err.response.data.detail}`);
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const startPolling = (sessionId) => {
    // Clear any existing polling
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }

    const interval = setInterval(async () => {
      try {
        const response = await axios.get(
          `${formData.backendUrl}/api/crypto/wallet/session/${sessionId}`
        );
        
        const sessionStatus = response.data;
        setSessionData(prev => ({ ...prev, ...sessionStatus }));
        
        if (sessionStatus.status === 'approved') {
          setStatus('Wallet connected successfully! 🎉');
          clearInterval(interval);
        } else if (sessionStatus.status === 'rejected') {
          setStatus('Connection was rejected by wallet');
          clearInterval(interval);
        } else if (sessionStatus.status === 'expired') {
          setStatus('Session expired');
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Error polling session status:', err);
        // Don't show error to user for polling failures
      }
    }, 2000); // Poll every 2 seconds

    setPollingInterval(interval);
  };

  const disconnectSession = async () => {
    if (!sessionData?.session_id) return;
    
    try {
      await axios.delete(`${formData.backendUrl}/api/crypto/wallet/session/${sessionData.session_id}`);
      setStatus('Session disconnected');
      setSessionData(null);
      
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
    } catch (err) {
      console.error('Error disconnecting session:', err);
      setError('Failed to disconnect session');
    }
  };

  useEffect(() => {
    // Cleanup polling on unmount
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  return (
    <div className="container">
      <div className="header">
        <h1>🔗 WalletConnect QR Test</h1>
        <p>Test your WalletConnect v2 backend integration</p>
      </div>

      <div className="card">
        <h2>Configuration</h2>
        
        <div className="form-group">
          <label>Backend URL:</label>
          <input
            type="text"
            name="backendUrl"
            value={formData.backendUrl}
            onChange={handleInputChange}
            placeholder="http://localhost:8000"
          />
        </div>

        <div className="form-group">
          <label>User ID:</label>
          <input
            type="text"
            name="userId"
            value={formData.userId}
            onChange={handleInputChange}
            placeholder="test-user-123"
          />
        </div>

        <div className="form-group">
          <label>Wallet Address (Optional):</label>
          <input
            type="text"
            name="walletAddress"
            value={formData.walletAddress}
            onChange={handleInputChange}
            placeholder="0x... or Solana address"
          />
        </div>

        <div className="form-group">
          <label>Chain Type:</label>
          <select
            name="chainType"
            value={formData.chainType}
            onChange={handleInputChange}
          >
            <option value="evm">EVM (Ethereum, Polygon, etc.)</option>
            <option value="solana">Solana</option>
          </select>
        </div>

        <div className="form-group">
          <label>Chain ID:</label>
          <select
            name="chainId"
            value={formData.chainId}
            onChange={handleInputChange}
          >
            {chainOptions[formData.chainType].map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <button 
          className="btn" 
          onClick={createSession}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="loading"></span> Creating Session...
            </>
          ) : (
            'Create WalletConnect Session'
          )}
        </button>

        {error && (
          <div className="status error">
            ⚠️ {error}
          </div>
        )}

        {status && (
          <div className="status info">
            ℹ️ {status}
          </div>
        )}
      </div>

      {sessionData && (
        <div className="card">
          <h2>WalletConnect Session</h2>
          
          <div className="qr-container">
            <h3>Scan QR Code</h3>
            <div className="qr-code">
              <QRCode 
                value={sessionData.uri} 
                size={256}
                level="M"
                includeMargin={true}
              />
            </div>
            <p>Use any WalletConnect v2 compatible wallet to scan this QR code</p>
          </div>

          <div className="form-group">
            <label>Session ID:</label>
            <div className="uri-display">{sessionData.session_id}</div>
          </div>

          <div className="form-group">
            <label>WalletConnect URI:</label>
            <div className="uri-display">{sessionData.uri}</div>
          </div>

          <div className="form-group">
            <label>Status:</label>
            <div className={`status ${sessionData.status === 'approved' ? 'success' : 'info'}`}>
              {sessionData.status.toUpperCase()}
            </div>
          </div>

          <div className="form-group">
            <label>Expires At:</label>
            <div>{new Date(sessionData.expires_at).toLocaleString()}</div>
          </div>

          {sessionData.wallet_address && (
            <div className="form-group">
              <label>Connected Wallet:</label>
              <div className="uri-display">{sessionData.wallet_address}</div>
            </div>
          )}

          <button 
            className="btn" 
            onClick={disconnectSession}
            style={{ backgroundColor: '#dc3545' }}
          >
            Disconnect Session
          </button>
        </div>
      )}

      <div className="card">
        <h2>Testing Instructions</h2>
        <ol>
          <li><strong>Backend Setup:</strong> Make sure your FastAPI backend is running on the specified URL</li>
          <li><strong>Authentication:</strong> You'll need to add Auth0 JWT token to the request headers for testing</li>
          <li><strong>Wallet Apps:</strong> Use any WalletConnect v2 compatible wallet (MetaMask, Rainbow, etc.)</li>
          <li><strong>Scan QR:</strong> Open your wallet app and scan the generated QR code</li>
          <li><strong>Approve:</strong> Approve the connection in your wallet</li>
          <li><strong>Monitor:</strong> Watch the status update in real-time</li>
        </ol>
        
        <div className="status info">
          <strong>Note:</strong> This is a test frontend. In production, you'll need to handle Auth0 authentication properly.
        </div>
      </div>
    </div>
  );
}

export default App; 