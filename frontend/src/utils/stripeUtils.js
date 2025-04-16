/**
 * Utility functions for Stripe integration
 */

import api from './api';
import { API_URL } from './constants';

/**
 * Create a Stripe checkout session for payment or payment method setup
 * @param {number} amount - Amount in cents
 * @param {string} currency - Currency code (e.g., 'usd')
 * @param {object} currentUser - Current user object
 * @param {boolean} isFullPayment - Whether this is a full payment (true) or just payment method setup (false)
 * @returns {Promise<string>} Checkout URL
 */
export const createDepositCheckout = async (amount, currency, currentUser, isFullPayment = true) => {
  try {
    console.log("Creating Stripe checkout session:", { 
      amount, 
      currency, 
      userId: currentUser?.id, 
      isFullPayment 
    });
    
    if (!currentUser || !currentUser.id) {
      console.error("Current user is missing or invalid:", currentUser);
      throw new Error("Missing user information for checkout");
    }
    
    if (isFullPayment && (!amount || isNaN(amount) || amount <= 0)) {
      console.error("Invalid amount for checkout:", amount);
      throw new Error("Invalid amount for checkout");
    }
    
    // Get current URL to return to after Stripe
    const currentUrl = window.location.href;
    
    // Prepare session data
    const checkoutData = {
      amount: amount,
      currency: currency?.toLowerCase() || 'usd',
      // Important: Use 'payment' for actual payments, 'setup' just for payment method setup
      type: isFullPayment ? 'payment' : 'setup',
      metadata: {
        user_id: currentUser.id,
        redirect_url: currentUrl,
        is_payment: isFullPayment ? 'true' : 'false'
      }
    };
    
    console.log("Sending checkout data to API:", checkoutData);
    
    // Create checkout session through API
    const response = await api.post('/stripe/create-checkout', checkoutData);
    console.log("Stripe checkout API response:", response);
    
    if (response?.data?.url) {
      console.log("Successfully got Stripe checkout URL:", response.data.url);
      return response.data.url;
    } else {
      console.error("No URL in Stripe response:", response);
      throw new Error('Failed to create Stripe checkout session - no URL returned');
    }
  } catch (error) {
    console.error('Error creating Stripe checkout:', error);
    if (error.response) {
      console.error('API error details:', error.response.data);
    }
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
 * @param {boolean} depositToWallet - Whether to deposit to wallet or save for later
 * @returns {Promise<object>} Deposit result
 */
export const initiateDirectDeposit = async (amount, currency, bankAccountId, userId, depositToWallet = true) => {
  try {
    const response = await api.post('/stripe/bank-deposit', {
      amount, 
      currency,
      bank_account_id: bankAccountId,
      user_id: userId,
      deposit_to_wallet: depositToWallet
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

/**
 * Process a direct payment for a transaction using a saved payment method
 * @param {object} transactionData - Transaction data
 * @param {string} paymentMethodId - ID of the payment method to use
 * @param {string} paymentSource - Source type ('card', 'bank', 'wallet_partial')
 * @returns {Promise<object>} - Payment result
 */
export const processDirectPayment = async (transactionData, paymentMethodId, paymentSource) => {
  try {
    const response = await api.post('/stripe/direct-payment', {
      transaction: transactionData,
      payment_method_id: paymentMethodId,
      payment_source: paymentSource
    });
    
    return response.data;
  } catch (error) {
    console.error('Error processing direct payment:', error);
    throw error;
  }
};

/**
 * Get saved payment methods for a user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} - Array of payment methods
 */
export const getPaymentMethods = async (userId) => {
  try {
    const response = await api.get(`/stripe/payment-methods/${userId}`);
    return response.data || [];
  } catch (error) {
    console.error('Error fetching payment methods:', error);
    return [];
  }
}; 