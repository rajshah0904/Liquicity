import axios from 'axios';

// Determine API base URL, ensure it targets backend (not the frontend dev server)
const rawBase = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const baseURL = /:3000(\/|$)/.test(rawBase) ? 'http://localhost:8000' : rawBase;

// Create axios instance with a base URL for the proxy
const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add authentication token if it exists
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Log outgoing requests
  console.log(`🌐 API Request: ${config.method.toUpperCase()} ${config.url}`, config);
  
  return config;
}, error => {
  console.error('📡 API Request Error:', error);
  return Promise.reject(error);
});

// Add response interceptor for handling common errors
api.interceptors.response.use(
  response => {
    console.log(`✅ API Response: ${response.status} from ${response.config.url}`, response.data);
    return response;
  },
  error => {
    console.error('❌ API Response Error:', error.response?.status || 'Network Error', 
      error.response?.data || error.message, 
      error.config?.url);
    
    // Handle 401 unauthorized errors by redirecting to login
    if (error.response && error.response.status === 401) {
      // Clear local storage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('current_user');
      
      // Redirect to login page if not already there
      if (!window.location.pathname.includes('/login') && 
          !window.location.pathname.includes('/register') &&
          !window.location.pathname.includes('/verify-email')) {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Helper to use mock data when backend is unavailable
const withMockFallback = (apiCall, mockFunction) => async (...args) => {
  try {
    return await apiCall(...args);
  } catch (error) {
    console.log('💫 Using mock data fallback');
    // Check if we have a mock implementation
    if (window.mockOverrides && mockFunction) {
      const parts = mockFunction.split('.');
      let mockImpl = window.mockOverrides;
      
      // Navigate through the object path
      for (const part of parts) {
        mockImpl = mockImpl[part];
        if (!mockImpl) break;
      }
      
      // If we found a matching mock function, use it
      if (typeof mockImpl === 'function') {
        return mockImpl(...args);
      }
    }
    
    // Re-throw the error if we don't have a mock implementation
    throw error;
  }
};

// Export API endpoints for authentication
export const authAPI = {
  // Register new user with email
  register: (userData, options = {}) => api.post('/onboard/register', userData, options),
  
  // Login with email and password
  login: (email, password) => api.post('/user/login/', { email, password }),
  
  // Google OAuth login
  googleLogin: (token) => api.post('/user/google-login/', { token }),
  
  // Request email verification link
  sendVerificationEmail: (email) => api.post('/user/send-verification-email/', { email }),
  
  // Verify email with token
  verifyEmail: (token) => api.post('/user/verify-email/', { token }),
  
  // Request passwordless login link
  sendLoginLink: (email) => api.post('/user/send-login-link/', { email }),
  
  // Verify login link
  verifyLoginLink: (token) => api.post('/user/verify-login-link/', { token }),
  
  // Logout user
  logout: () => api.post('/user/logout/'),
  
  // Get current user profile
  getCurrentUser: () => api.get('/user'),
  
  // Update user profile
  updateProfile: (userId, profileData) => api.put(`/user/update-profile/${userId}`, profileData),
  
  // Update user metadata (KYC info)
  updateMetadata: (userId, metadata) => api.post(`/user/${userId}/metadata`, metadata)
};

// Export API endpoints for wallet operations
export const walletAPI = {
  // Get user wallets
  getUserWallets: (userId) => api.get(`/wallet/user/${userId}`),
  
  // Bridge wallet live data
  getBridgeWallet: (options = {}) => api.get('/wallet', options),
  
  // Update wallet
  updateWallet: (userId, walletData) => api.put(`/wallet/update/${userId}`, walletData),
  
  // Get wallet transactions (live from Bridge)
  getTransactions: () => api.get('/wallet/history'),
  
  // Get all transactions (Bridge aggregated)
  getAllTransactions: (options = {}) => api.get('/wallet/history', options),
  
  // Get wallet overview
  getOverview: (options = {}) => api.get('/wallet/overview', options)
};

// Export API endpoints for payment operations
export const paymentAPI = {
  // Create payment
  createPayment: (paymentData) => api.post('/payment/create', paymentData),
  
  // Get payment status
  getPaymentStatus: (paymentId) => api.get(`/payment/${paymentId}/status`),
  
  // Process deposit
  processDeposit: (depositData) => api.post('/payment/deposit', depositData),
  
  // Process withdrawal
  processWithdrawal: (withdrawalData) => api.post('/payment/withdraw', withdrawalData)
};

// Export API endpoints for KYC operations
export const kycAPI = {
  // Submit KYC data
  submitKycData: (userId, kycData) => api.post(`/user/kyc/submit`, kycData),
  
  // Get KYC status
  getKycStatus: (userId) => api.get(`/user/kyc/${userId}/status`),
  
  // Upload identity documents
  uploadDocument: (userId, documentType, file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('documentType', documentType);
    
    return api.post(`/user/kyc/${userId}/upload-document`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};

// === Bridge-centric helpers (new) ===

/**
 * Bridge API client
 * 
 * This API client interfaces with the Liquicity backend which in turn connects to Bridge API.
 * Our backend implements these endpoints to match the Bridge API structure.
 * 
 * Bridge API Reference documentation: https://docs.bridge.xyz/reference/
 * 
 * The Bridge API is organized into the following main sections:
 * - Customers (account management)
 * - External Accounts (bank accounts linked to Bridge)
 * - Virtual Accounts (US accounts & EU IBANs for receiving funds)
 * - Bridge Wallets (crypto/stablecoin wallets managed by Bridge)
 * - Transfers (moving money between accounts)
 * - Plaid (US bank account linking via Plaid)
 * - Cards (virtual card issuance and management)
 * - Webhooks (notification system for account changes)
 * 
 * For a complete reference of all endpoints, see:
 * app/services/bridge_api_reference.py in the backend codebase
 */
export const bridgeAPI = {
  // Ensure customer exists & return record
  getOrCreateCustomer: (options = {}) => api.get('/bridge/customers', options),

  // Link external bank / IBAN / CLABE
  createExternalAccount: (payload, options = {}) => api.post('/bridge/external_account', payload, options),

  // Card issuance / management (virtual for now)
  createCard: (payload = { type: 'virtual', currency: 'usd' }, options = {}) =>
    api.post('/bridge/cards', payload, options),

  // Plaid flows (US bank linking)
  getPlaidLinkToken: (options = {}) => api.get('/bridge/plaid/link_request', options),
  exchangePlaidPublicToken: (requestId, options = {}) =>
    api.post(`/bridge/plaid/exchange/${requestId}`, {}, options),
};

// Export API endpoints for external accounts
export const externalAccountsAPI = {
  // Get all external accounts for the current user
  getAccounts: () => api.get('/external_accounts/accounts'),
  
  // Get a specific external account
  getAccount: (id) => api.get(`/external_accounts/accounts/${id}`),
  
  // Create a new external account (manual entry)
  createAccount: (accountData) => api.post('/external_accounts/accounts', accountData),
  
  // Delete an external account
  deleteAccount: (id) => api.delete(`/external_accounts/accounts/${id}`),
  
  // Get region info to determine flow
  getRegionInfo: () => api.get('/external_accounts/region'),
  
  // Plaid linking (US only)
  getPlaidLinkToken: () => api.get('/external_accounts/plaid/link_token'),
  exchangePlaidToken: (requestId, publicToken, institutionData = {}) => 
    api.post(`/external_accounts/plaid/exchange/${requestId}`, { 
      public_token: publicToken,
      ...institutionData
    }),

  // Plaid passthrough APIs for linked accounts
  /**
   * Fetch real-time balance information for the specified external account.
   * Backend wrapper around Plaid /accounts/balance/get
   * @param {string} accountId Bridge external_account id
   */
  getAccountBalance: (accountId) =>
    api.get(`/external_accounts/accounts/${accountId}/balance`),

  /**
   * Fetch account/routing numbers (ACH) via Plaid Auth
   * Backend wrapper around Plaid /auth/get
   * @param {string} accountId Bridge external_account id
   */
  getAccountAuth: (accountId) =>
    api.get(`/external_accounts/accounts/${accountId}/auth`),

  /**
   * Fetch owner name / address via Plaid Identity
   * Backend wrapper around Plaid /identity/get
   * @param {string} accountId Bridge external_account id
   */
  getAccountIdentity: (accountId) =>
    api.get(`/external_accounts/accounts/${accountId}/identity`),
  
  // Sync accounts/balances
  syncAccounts: () => api.post('/external_accounts/sync'),
};

// Export API endpoints for deposits and transfers
export const transferAPI = {
  // Deposit funds from external account to Bridge wallet
  deposit: (data) => api.post('/deposits', data),
  
  // Withdraw funds
  withdraw: (data) => api.post('/transfers/withdraw', data),
  
  // Internal transfer
  transfer: (data) => api.post('/transfers', data),
  
  // Send money to another user
  send: (data) => api.post('/transfers/send', data),
  
  // Quote a transfer (no execution)
  quote: (data) => api.post('/transfers/quote', data),
  
  // List transfers
  getTransfers: (params) => api.get('/transfers', { params }),
};

// Requests (P2P payment requests)
export const requestsAPI = {
  create: (payload, options = {}) => api.post('/requests', payload, options),
  list: (options = {}) => api.get('/requests', options),
};

// === Crypto wallet endpoints (WalletConnect & USDC) ===
export const cryptoAPI = {
  // Start WalletConnect session
  connectWallet: (payload) => api.post('/api/crypto/wallet/connect', payload),
  // Get WC session status
  getSessionStatus: (sessionId) => api.get(`/api/crypto/wallet/session/${sessionId}`),
  // Create USDC transfer (awaiting signature)
  createUsdcTransfer: (payload) => api.post('/api/crypto/payments/usdc/transfer', payload),
  // Submit signed transaction
  signUsdcTransaction: (payload) => api.post('/api/crypto/payments/usdc/sign', payload),
  // Bridge transfer after deposit
  createBridgeTransfer: (payload) => api.post('/api/crypto/bridge/transfer', payload),
};

// Export base axios instance for modules that imported default
export default api;