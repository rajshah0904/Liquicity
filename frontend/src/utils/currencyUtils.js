import { CURRENCY_SYMBOLS } from './constants';

/**
 * Gets the currency symbol based on currency code with special handling for specific users
 * 
 * @param {string} currencyCode - The currency code (USD, EUR, etc.)
 * @param {Object} user - The current user object, if available
 * @returns {string} The currency symbol
 */
export const getCurrencySymbol = (currencyCode, user = null) => {
  // Special case for Hadeer's account - always use Euro
  if (user && user.email === 'hadeermotair@gmail.com') {
    return '€';
  }
  
  const code = currencyCode?.toUpperCase() || 'USD';
  
  // Use the symbol from constants if available
  if (CURRENCY_SYMBOLS[code]) {
    return CURRENCY_SYMBOLS[code];
  }
  
  // Fallback handling for common currencies
  switch(code) {
    case 'EUR': return '€';
    case 'GBP': return '£';
    case 'MXN': return '₱';
    case 'CAD': return 'C$';
    default: return '$'; // Default to USD symbol
  }
};

/**
 * Formats a currency amount with the appropriate symbol 
 * 
 * @param {number} amount - The amount to format
 * @param {string} currencyCode - The currency code (USD, EUR, etc.)
 * @param {Object} user - The current user object, if available
 * @param {string} locale - The locale to use for formatting
 * @returns {string} The formatted currency amount
 */
export const formatCurrency = (amount, currencyCode = 'USD', user = null, locale = 'en-US') => {
  if (amount === undefined || amount === null) return '—';
  
  // Handle special case for Hadeer
  if (user && user.email === 'hadeermotair@gmail.com') {
    currencyCode = 'EUR';
  }
  
  const formatter = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currencyCode,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  
  return formatter.format(amount);
};

/**
 * Determines which currency code to use for a user
 * 
 * @param {Object} user - The current user object
 * @param {string} defaultCurrency - Default currency if none can be determined
 * @returns {string} The currency code to use
 */
export const getUserCurrency = (user, defaultCurrency = 'USD') => {
  if (!user) return defaultCurrency;
  
  // Special case for Hadeer
  if (user.email === 'hadeermotair@gmail.com') {
    return 'EUR';
  }
  
  // Check country from user profile
  if (user.country === 'EU') {
    return 'EUR';
  } else if (user.country === 'MX') {
    return 'MXN';
  } else if (user.country === 'GB') {
    return 'GBP';
  }
  
  // Default
  return defaultCurrency;
}; 