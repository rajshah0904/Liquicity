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
  updateMetadata: (userId, metadata) => api.post(`/user/${userId}/metadata`, metadata)
};

// Export API endpoints for wallet operations
export const walletAPI = {
  // Get user wallets
  getUserWallets: (userId) => api.get(`/wallet/user/${userId}`),
  
  // Update wallet
  updateWallet: (userId, walletData) => api.put(`/wallet/update/${userId}`, walletData),
  
  // Get wallet transactions
  getTransactions: (walletId) => api.get(`/wallet/${walletId}/transactions`)
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

// Export the base API instance as default
export default api; 