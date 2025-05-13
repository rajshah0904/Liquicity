import axios from 'axios';

// Create axios instance with a base URL for the proxy
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
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
  register: (userData, options = {}) => api.post('/user/register/', userData, options),
  
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
  getCurrentUser: () => api.get('/user/user/'),
  
  // Update user profile
  updateProfile: (userId, profileData) => api.put(`/user/update-profile/${userId}`, profileData),
  
  // Update user metadata (KYC info)
  updateMetadata: (userId, metadata) => api.post(`/user/${userId}/metadata`, metadata),
  
  // Search users by name or email
  searchUsers: (query) => withMockFallback(
    () => api.get(`/user/search?query=${encodeURIComponent(query)}`),
    'authAPI.searchUsers'
  )(),
};

// Export API endpoints for wallet operations
export const walletAPI = {
  // Get user wallets
  getUserWallets: (userId) => api.get(`/wallet/user/${userId}`),
  
  // Update wallet
  updateWallet: (userId, walletData) => api.put(`/wallet/update/${userId}`, walletData),
  
  // Get wallet transactions
  getTransactions: (walletId) => api.get(`/wallet/${walletId}/transactions`),
  
  // Get all transactions (Bridge aggregated)
  getAllTransactions: (options = {}) => withMockFallback(
    () => api.get('/wallet/transactions', options),
    'walletAPI.getAllTransactions'
  )(),
  
  // Get wallet overview
  getOverview: (options = {}) => withMockFallback(
    () => api.get('/wallet/overview', options),
    'walletAPI.getOverview'
  )()
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

// New Transfer-centric helpers (deposit / withdraw / send)
export const transferAPI = {
  deposit: (payload, options = {}) => api.post('/transfer/deposit', payload, options),
  withdraw: (payload, options = {}) => api.post('/transfer/withdraw', payload, options),
  send: (payload, options = {}) => withMockFallback(
    () => api.post('/transfer/send', payload, options),
    'transferAPI.send'
  )(),
  internal: (payload, options = {}) => api.post('/transfer/internal', payload, options),
};

// New Requests helper
export const requestsAPI = {
  create: (payload, options = {}) => withMockFallback(
    () => api.post('/requests', payload, options),
    'requestsAPI.create'
  )(),
  list: (options = {}) => withMockFallback(
    () => api.get('/requests', options),
    'requestsAPI.list'
  )(),
};

// Export the base API instance as default
export default api; 