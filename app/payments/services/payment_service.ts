/**
 * Payment service for TerraFlow.
 * 
 * This module provides basic payment operations for sending and
 * receiving fiat currency through payment providers.
 */

import { getProvider } from '../providers/factory';

/**
 * Receive fiat currency from a user's account
 * 
 * @param userId ID of the user to receive from
 * @param amount Amount to receive
 * @param currency Currency code (e.g., "USD")
 * @returns Transaction result
 */
export async function receiveFiat(userId: string, amount: number, currency: string): Promise<any> {
  // Determine the country code from the user profile or transaction data
  // For simplicity, defaulting to "US" in this implementation
  const countryCode = "US";
  
  // Get the appropriate payment provider for the country
  const provider = getProvider(countryCode);
  
  // Execute the pull operation
  // This would normally use account details from a database
  return await provider.pull(amount, currency, userId);
}

/**
 * Send fiat currency to a user's account
 * 
 * @param userId ID of the user to send to
 * @param amount Amount to send
 * @param currency Currency code (e.g., "USD")
 * @param isRefund Whether this is a refund transaction
 * @returns Transaction result
 */
export async function sendFiat(
  userId: string,
  amount: number,
  currency: string,
  isRefund: boolean = false
): Promise<any> {
  // Determine the country code from the user profile or transaction data
  // For simplicity, defaulting to "US" in this implementation
  const countryCode = "US";
  
  // Get the appropriate payment provider for the country
  const provider = getProvider(countryCode);
  
  // Execute the push operation
  // This would normally use account details from a database
  const metadata = isRefund 
    ? { refund: true, original_user_id: userId } 
    : { user_id: userId };
    
  return await provider.push(amount, currency, userId, metadata);
} 