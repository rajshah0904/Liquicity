import axios, { AxiosRequestConfig, Method } from 'axios';
import { v4 as uuidv4 } from 'uuid';

// Backend API configuration
const BACKEND_BASE_URL = __DEV__ 
  ? 'http://localhost:8000'  // Development - your local backend
  : 'https://your-production-backend.com'; // Production - replace with your actual production URL

// Create axios instance for backend API calls
const backendApi = axios.create({
  baseURL: BACKEND_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to make requests to your backend
export async function backendRequest<T = any>(
  method: Method,
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await backendApi.request<T>({
    method,
    url,
    data,
    ...config,
  });
  return response.data;
}

// Auth0 token interceptor - adds Authorization header with JWT token
backendApi.interceptors.request.use(
  async (config) => {
    // You'll need to get the Auth0 token from your auth context
    // For now, this is a placeholder
    // const token = await getAuth0Token();
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
backendApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API endpoints that match your backend routes
export const API_ENDPOINTS = {
  // User management
  USER_CHECK: '/user/check',
  USER_PROFILE: '/user/profile',
  
  // Onboarding
  ONBOARDING: '/onboard',
  REGISTER: '/onboard/register',
  TOS_ACCEPTED: '/onboard/tos/accepted',
  
  // KYC
  KYC_STATUS: '/kyc/status',
  KYC_LINK: '/kyc/link',
  
  // Wallet
  WALLET_INFO: '/wallet/info',
  WALLET_BALANCE: '/wallet/balance',
  WALLET_HISTORY: '/wallet/history',
  
  // External accounts
  EXTERNAL_ACCOUNTS: '/external_accounts',
  
  // Virtual accounts
  VIRTUAL_ACCOUNTS: '/virtual_accounts',
  
  // Transfers
  TRANSFERS: '/transfers',
  
  // Health check
  HEALTH: '/health',
};

export default backendApi; 