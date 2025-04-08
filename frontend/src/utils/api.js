import axios from 'axios';
import { API_URL } from './constants';

// Create a base axios instance with default configuration
const api = axios.create({
  baseURL: API_URL, // Backend API URL from constants
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Add this line to ensure cookies and auth headers are properly sent
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('auth_token');
    
    // If token exists, add it to the request headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    // Return successful responses directly
    return response;
  },
  (error) => {
    // Handle error responses
    if (error.response) {
      // Server responded with an error status code
      console.error('API Error:', {
        url: error.config.url,
        status: error.response.status,
      });
      
      // Handle authentication errors (401)
      if (error.response.status === 401) {
        // Clear local storage if token is invalid or expired
        localStorage.removeItem('auth_token');
        localStorage.removeItem('current_user');
        
        // Redirect to login page if not already there
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('API Request Error (No Response):', error.request);
    } else {
      // Error setting up the request
      console.error('API Setup Error:', error.message);
    }
    
    // Return the rejected promise
    return Promise.reject(error);
  }
);

export default api; 