/**
 * Fee structure constants for Liquicity application.
 * 
 * This file centralizes all fee-related constants to ensure consistency across the application.
 */

// Two-Tier Fee Structure

// Standard Tier (1-3 business days)
// Free deposit + 0.75% send; all-in ≤ Wise/Remitly fast rails
export const STANDARD_DEPOSIT_FEE_RATE = 0.0;  // No fee for standard deposits
export const STANDARD_SEND_FEE_RATE = 0.005;  // 0.5% for P2P wallet transfers

// Express Tier (Instant ≤ 15 min)
// Covers instant deposit (1.5076%) + balance-send (0.5%) rails
// Display as 1.5% in UI, but calculate with exact rate
export const INSTANT_DEPOSIT_FEE_RATE = 0.015076;  // 1.5076% for instant deposits
// All-in express fee is 2.0% (math: 1 - (1 - 0.015076) × (1 - 0.005) ≈ 0.02)

// P2P Wallet-Only (for users who have already deposited)
// Best-in-class pure P2P, 0.5% fee
export const P2P_WALLET_FEE_RATE = 0.005;  // 0.5% for wallet-to-wallet transfers

// Withdraw (no fee)
export const WITHDRAW_FEE_RATE = 0.0;  // Free withdrawal to bank

// Card Spend (no fee)
export const CARD_SPEND_FEE_RATE = 0.0;  // Free card spending

// Bank transfer fee (when using bank account directly for sending money)
export const BANK_TRANSFER_FEE_RATE = 0.029;  // 2.9% fee for bank-funded transfers

// For UI display (rounded to nearest tenth)
export const UI_INSTANT_DEPOSIT_FEE = '1.5%';  // Display as 1.5% in UI
export const UI_STANDARD_SEND_FEE = '0.5%';  // Display as 0.5% in UI
export const UI_BANK_TRANSFER_FEE = '2.9%';  // Display as 2.9% in UI

/**
 * Calculate fee for a transaction
 * @param {number} amount - The transaction amount
 * @param {number} feeRate - The fee rate to apply
 * @returns {number} The calculated fee amount
 */
export const calculateFee = (amount, feeRate) => {
  return parseFloat((amount * feeRate).toFixed(2));
};

/**
 * Calculate total amount including fee
 * @param {number} amount - The base transaction amount
 * @param {number} feeRate - The fee rate to apply
 * @returns {number} The total amount including fee
 */
export const calculateTotalWithFee = (amount, feeRate) => {
  return parseFloat((amount + calculateFee(amount, feeRate)).toFixed(2));
}; 