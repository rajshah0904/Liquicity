/**
 * Calculate the total fiat balance from Bridge wallet using fiat_balance_by_rate
 * @param {Object} bridgeWallet - The Bridge wallet object
 * @returns {number} The calculated fiat balance
 */
import { getCurrencySymbol } from './currency';
export const calculateLiquicityBalance = (bridgeWallet) => {
  if (!bridgeWallet) {
    return 0;
  }
  
  // Use the calculated fiat_balance from backend if available (preferred)
  if (typeof bridgeWallet.fiat_balance === 'number') {
    return bridgeWallet.fiat_balance;
  }
  
  // Use fiat_balance_by_rate to calculate balance
  // New format: {"amount": rate} where keys are amounts and values are rates
  if (bridgeWallet.fiat_balance_by_rate && typeof bridgeWallet.fiat_balance_by_rate === 'object') {
    let total = 0;
    
    // Sum all the amount keys (not the rate values)
    for (const [amountKey, rateValue] of Object.entries(bridgeWallet.fiat_balance_by_rate)) {
      const amount = parseFloat(amountKey);
      if (!isNaN(amount)) {
        total += amount;
      }
    }
    
    return total;
  }
  
  // No balance data available
  return 0;
};

/**
 * Format balance for display with currency symbol
 * @param {number} balance - The balance amount
 * @param {string} currency - The currency code (default: 'USD')
 * @returns {string} Formatted balance string
 */
export const formatBalance = (balance, currency = 'USD') => {
  const currencySymbol = getCurrencySymbol(currency);
  return `${currencySymbol}${Number(balance || 0).toLocaleString(undefined, { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })}`;
}; 