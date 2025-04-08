/**
 * Authentication utilities for TerraFlow frontend
 */

// Get authentication token from localStorage
export const getToken = () => {
  return localStorage.getItem('auth_token');
};

// Check if user is logged in
export const isLoggedIn = () => {
  return !!getToken();
};

// Set authentication token in localStorage
export const setToken = (token) => {
  localStorage.setItem('auth_token', token);
};

// Remove authentication token from localStorage
export const logout = () => {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('current_user');
};

// Get current user data from localStorage
export const getCurrentUser = () => {
  const userString = localStorage.getItem('current_user');
  return userString ? JSON.parse(userString) : null;
};

// Set current user data in localStorage
export const setCurrentUser = (user) => {
  localStorage.setItem('current_user', JSON.stringify(user));
};

// Get authentication headers for API requests
export const getAuthHeaders = () => {
  const token = getToken();
  return token ? { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  } : {
    'Content-Type': 'application/json'
  };
};

// Parse JWT token to get expiration time
export const getTokenExpiration = () => {
  const token = getToken();
  if (!token) return null;
  
  try {
    // JWT token consists of three parts separated by dots
    const payload = token.split('.')[1];
    // Base64 decode the payload
    const decoded = atob(payload);
    // Parse the JSON
    const parsed = JSON.parse(decoded);
    
    // Return the expiration timestamp
    return parsed.exp * 1000; // Convert to milliseconds
  } catch (e) {
    console.error('Error parsing token:', e);
    return null;
  }
};

// Check if token is expired
export const isTokenExpired = () => {
  const expiration = getTokenExpiration();
  return expiration ? expiration < Date.now() : true;
}; 