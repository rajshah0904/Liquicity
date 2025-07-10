import axios, { AxiosRequestConfig, Method } from 'axios';
import { v4 as uuidv4 } from 'uuid';

// Backend API configuration
const BACKEND_BASE_URL = __DEV__ 
  ? 'http://192.168.86.31:8000'  // Development - use your computer's IP address
  : 'https://api.liquicity.com'; // Production - replace with your actual production URL

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
  console.log('[API] Request:', method, url, { data, config });
  try {
    const response = await backendApi.request<T>({
      method,
      url,
      data,
      ...config,
    });
    console.log('[API] Response:', method, url, response.status, response.data);
    return response.data;
  } catch (error: any) {
    console.error('[API] Error:', method, url, error?.message, error?.response);
    console.error('[API] Error Details:', {
      message: error?.message,
      status: error?.response?.status,
      statusText: error?.response?.statusText,
      data: error?.response?.data,
      config: error?.config,
      code: error?.code,
      isAxiosError: error?.isAxiosError,
      timeout: error?.code === 'ECONNABORTED' ? 'Request timed out' : 'No timeout'
    });
    throw error;
  }
}

// Auth0 token interceptor - adds Authorization header with JWT token
backendApi.interceptors.request.use(
  async (config) => {
    const method = config.method?.toUpperCase() || 'UNKNOWN';
    const baseURL = config.baseURL || '';
    const url = config.url || '';
    console.log('[API] Axios Request:', method, baseURL + url, config.headers);
    if (config.headers && config.headers.Authorization) {
      console.log('Authorization header being sent:', config.headers.Authorization);
    } else {
      console.log('No Authorization header set on this request');
    }
    return config;
  },
  (error) => {
    console.error('[API] Request interceptor error:', error);
    return Promise.reject(error);
  }
);

backendApi.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toUpperCase() || 'UNKNOWN';
    const baseURL = response.config.baseURL || '';
    const url = response.config.url || '';
    console.log('[API] Axios Response:', method, baseURL + url, response.status, response.data);
    return response;
  },
  (error) => {
    const method = error.config?.method?.toUpperCase() || 'UNKNOWN';
    const baseURL = error.config?.baseURL || '';
    const url = error.config?.url || '';
    console.error('[API] Axios Error:', method, baseURL + url, error?.message, error?.response);
    console.error('[API] Axios Error Details:', {
      message: error?.message,
      status: error?.response?.status,
      statusText: error?.response?.statusText,
      data: error?.response?.data,
      code: error?.code,
      isAxiosError: error?.isAxiosError,
      timeout: error?.code === 'ECONNABORTED' ? 'Request timed out' : 'No timeout'
    });
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