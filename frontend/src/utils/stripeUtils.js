/**
 * Utility functions for Stripe integration
 */

import api from './api';

/**
 * Creates a Stripe checkout session for deposit
 * @param {number} amount - Amount to deposit in cents
 * @param {string} currency - Currency code (e.g., 'usd')
 * @param {object} userData - User data for the checkout
 * @returns {Promise<string>} Checkout URL
 */
export const createDepositCheckout = async (amount, currency, userData) => {
  try {
    const response = await api.post('/payment/stripe/create-checkout', {
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
 * Initiates a withdrawal to a bank account
 * @param {number} amount - Amount to withdraw in cents
 * @param {string} currency - Currency code (e.g., 'usd')
 * @param {string} bankAccountId - ID of the saved bank account
 * @param {number} userId - User ID
 * @returns {Promise<object>} Withdrawal result
 */
export const initiateWithdrawal = async (amount, currency, bankAccountId, userId) => {
  try {
    const response = await api.post('/payment/stripe/withdraw', {
      amount,
      currency,
      bank_account_id: bankAccountId,
      user_id: userId
    });

    if (response.status === 200) {
      return response.data;
    } else {
      throw new Error('Failed to initiate withdrawal');
    }
  } catch (error) {
    console.error('Error initiating withdrawal:', error);
    throw error;
  }
};

/**
 * Lists saved bank accounts for a user
 * @param {number} userId - User ID
 * @returns {Promise<Array>} List of bank accounts
 */
export const listBankAccounts = async (userId) => {
  try {
    const response = await api.get(`/payment/stripe/bank-accounts/${userId}`);
    
    if (response.status === 200) {
      return response.data;
    } else {
      throw new Error('Failed to fetch bank accounts');
    }
  } catch (error) {
    console.error('Error fetching bank accounts:', error);
    return [];
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
    const response = await api.post('/payment/stripe/bank-deposit', {
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
 * Links a new bank account
 * @param {number} userId - User ID
 * @returns {Promise<string>} URL to Stripe bank account linking page
 */
export const linkBankAccount = async (userId) => {
  try {
    const response = await api.post('/payment/stripe/link-bank-account', {
      user_id: userId,
      return_url: `${window.location.origin}/wallet?linkStatus=success`,
      cancel_url: `${window.location.origin}/wallet?linkStatus=canceled`
    });

    if (response.status === 200 && response.data.url) {
      return response.data.url;
    } else {
      throw new Error('Failed to create bank account link');
    }
  } catch (error) {
    console.error('Error creating bank account link:', error);
    throw error;
  }
}; 