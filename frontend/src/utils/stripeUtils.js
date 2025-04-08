/**
 * Utility functions for Stripe integration
 */

import api from './api';
import { API_URL } from './constants';

/**
 * Creates a Stripe checkout session for deposit
 * @param {number} amount - Amount to deposit in cents
 * @param {string} currency - Currency code (e.g., 'usd')
 * @param {object} userData - User data for the checkout
 * @returns {Promise<string>} Checkout URL
 */
export const createDepositCheckout = async (amount, currency, userData) => {
  try {
    const response = await api.post('/stripe/create-checkout', {
      amount,
      currency,
      type: 'deposit',
      metadata: {
        user_id: userData.id,
        email: userData.email
      }
    });

    if (response.status === 200 && response.data.url) {
      return response.data.url;
    } else {
      throw new Error('Failed to create checkout session');
    }
  } catch (error) {
    console.error('Error creating Stripe checkout session:', error);
    throw error;
  }
};

/**
 * Initiate a withdrawal from the user's wallet to their bank account
 * @param {number} amount - Amount to withdraw in cents
 * @param {string} currency - Currency code (e.g., 'usd')
 * @param {string} accountId - Bank account ID to withdraw to
 * @param {string} userId - User ID
 * @returns {Promise<Object>} - Result of withdrawal request
 */
export const initiateWithdrawal = async (amount, currency, accountId, userId) => {
  try {
    const response = await api.post('/stripe/withdraw', {
      amount,
      currency,
      bank_account_id: accountId,
      user_id: userId
    });
    
    return { 
      success: true, 
      data: response.data 
    };
  } catch (error) {
    console.error('Withdrawal error:', error);
    return {
      success: false,
      error: error.response?.data?.message || 'Failed to process withdrawal'
    };
  }
};

/**
 * Fetch a list of user's connected bank accounts
 * @param {string} userId - User ID
 * @returns {Promise<Array>} - Array of bank accounts
 */
export const listBankAccounts = async (userId) => {
  try {
    const response = await api.get(`/stripe/bank-accounts/${userId}`);
    return response.data || [];
  } catch (error) {
    console.error('Error fetching bank accounts:', error);
    throw error;
  }
};

/**
 * Initiates a direct deposit from a bank account
 * @param {number} amount - Amount to deposit in cents
 * @param {string} currency - Currency code (e.g., 'usd')
 * @param {string} bankAccountId - ID of the bank account
 * @param {number} userId - User ID
 * @returns {Promise<object>} Deposit result
 */
export const initiateDirectDeposit = async (amount, currency, bankAccountId, userId) => {
  try {
    const response = await api.post('/stripe/bank-deposit', {
      amount, 
      currency,
      bank_account_id: bankAccountId,
      user_id: userId
    });
    
    if (response.status === 200) {
      return response.data;
    } else {
      throw new Error('Failed to initiate bank transfer');
    }
  } catch (error) {
    console.error('Error initiating bank deposit:', error);
    throw error;
  }
};

/**
 * Create a link token to connect a bank account
 * @param {string} userId - User ID
 * @returns {Promise<string>} - URL to redirect to for bank account linking
 */
export const linkBankAccount = async (userId) => {
  try {
    const response = await api.post('/stripe/link-bank-account', {
      user_id: userId,
      return_url: `${window.location.origin}/withdraw?linkStatus=success`,
      cancel_url: `${window.location.origin}/withdraw?linkStatus=canceled`
    });
    
    return response.data.url;
  } catch (error) {
    console.error('Error creating bank link:', error);
    throw error;
  }
};

/**
 * Create a Stripe checkout session for adding funds
 * @param {number} amount - Amount to add in cents
 * @param {string} currency - Currency code
 * @param {string} userId - User ID
 * @returns {Promise<string>} - Checkout URL
 */
export const createCheckoutSession = async (amount, currency, userId) => {
  try {
    const response = await api.post('/stripe/create-checkout', {
      amount,
      currency,
      user_id: userId,
      type: 'deposit',
      metadata: {
        user_id: userId
      }
    });
    
    return response.data.url;
  } catch (error) {
    console.error('Error creating checkout session:', error);
    throw error;
  }
}; 