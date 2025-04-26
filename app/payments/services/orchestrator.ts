/**
 * Payment orchestration service for TerraFlow.
 * 
 * This module provides high-level orchestration of payment flows,
 * coordinating between different payment providers and cross-chain bridge operations.
 */

import { getBridgeProvider } from '../providers/factory';
import { receiveFiat, sendFiat } from './payment_service';

interface CrossBorderTransferOptions {
  userId: string;
  amount: number;
  srcCountryCode: string;
  dstCountryCode: string;
  currency: string;
  srcChain?: string | number;
  dstChain?: string | number;
  recipient?: string;
  metadata?: Record<string, any>;
}

interface TransferResult {
  debit: any;
  bridgeOnramp: any;
  bridgeOfframp: any;
  payout: any;
  status: 'pending' | 'completed' | 'failed' | 'refunded' | 'indeterminate_needs_review' | 'offramp_complete_payout_failed';
  errors: string[];
}

/**
 * Execute a cross-border transfer using cross-chain bridges as an intermediary.
 * 
 * This orchestrates a complete flow from source fiat currency to destination fiat currency,
 * using Stargate Protocol as a bridge for the cross-border transfer.
 * 
 * Flow:
 * 1. Pull funds from user's local payment source
 * 2. On-ramp via Stargate (unified liquidity pools across chains)
 * 3. Transfer across chains via Stargate (handled internally)
 * 4. Off-ramp to destination fiat
 * 5. Pay out to the recipient
 * 
 * @param options Transfer options including amount, currencies, and chains
 * @returns A result object with the results of each step
 * @throws Error if any part of the transfer fails
 */
export async function transferCrossBorder(options: CrossBorderTransferOptions): Promise<TransferResult> {
  const {
    userId,
    amount,
    srcCountryCode,
    dstCountryCode,
    currency,
    srcChain = 1,  // Default: Ethereum Mainnet
    dstChain = 137, // Default: Polygon
    recipient,
    metadata
  } = options;
  
  const result: TransferResult = {
    debit: null,
    bridgeOnramp: null,
    bridgeOfframp: null,
    payout: null,
    status: 'pending',
    errors: []
  };
  
  try {
    // Step 1: Pull local fiat from user's payment source
    console.log(`Initiating fiat debit for user ${userId}, amount ${amount} ${currency}`);
    result.debit = await receiveFiat(userId, amount, currency);
    
    // Step 2: On-ramp via Stargate (unified liquidity pools across chains)
    console.log(`Bridging ${amount} ${currency} from chain ${srcChain} to ${dstChain}`);
    const bridge = getBridgeProvider();
    result.bridgeOnramp = await bridge.onramp(
      amount,
      currency,
      srcChain,
      dstChain,
      recipient || userId
    );
    
    // Step 3: Transfer across chains (handled internally by Stargate)
    console.log(`Cross-chain transfer complete with transaction ID: ${result.bridgeOnramp.tx_id}`);
    
    // Step 4: Off-ramp to destination fiat
    console.log(`Off-ramping to fiat in destination country ${dstCountryCode}`);
    const bankAccountId = metadata?.bankAccountId || userId;
    result.bridgeOfframp = await bridge.offramp(
      amount,
      currency,
      dstChain,
      bankAccountId
    );
    
    // Step 5: Pay out to the recipient
    console.log(`Sending fiat payout of ${amount} ${currency}`);
    result.payout = await sendFiat(userId, amount, currency);
    
    result.status = 'completed';
    return result;
    
  } catch (error) {
    console.error(`Error during cross-border transfer: ${error.message}`);
    result.status = 'failed';
    result.errors.push(error.message);
    
    // Attempt fallback and recovery based on where the failure occurred
    try {
      await handleTransferFallback(result, userId, amount, currency);
    } catch (fallbackError) {
      console.error(`Fallback handling failed: ${fallbackError.message}`);
      result.errors.push(`Fallback error: ${fallbackError.message}`);
    }
    
    return result;
  }
}

/**
 * Handle fallback logic for failed transfers.
 * 
 * This attempts to recover from failures at different stages of the transfer process.
 * 
 * @param result The current result object with existing operation results
 * @param userId User ID for the transfer
 * @param amount Amount being transferred
 * @param currency Currency being used
 */
async function handleTransferFallback(
  result: TransferResult,
  userId: string,
  amount: number,
  currency: string
): Promise<void> {
  // Check where the failure occurred and apply appropriate fallback
  if (result.debit && !result.bridgeOnramp) {
    // Failed after debit but before bridge on-ramp - refund the user
    console.log(`Initiating refund for user ${userId} of ${amount} ${currency}`);
    await sendFiat(userId, amount, currency, true); // true = refund
    result.status = 'refunded';
    
  } else if (result.bridgeOnramp && !result.bridgeOfframp) {
    // Failed after on-ramp but before off-ramp
    // This is a complex state requiring manual intervention
    console.error(
      `Transfer in indeterminate state. On-ramped but not off-ramped. ` +
      `Transaction ID: ${result.bridgeOnramp.tx_id}, Amount: ${amount} ${currency}`
    );
    result.status = 'indeterminate_needs_review';
    
  } else if (result.bridgeOfframp && !result.payout) {
    // Failed after off-ramp but before payout
    // Need to retry the payout or notify operations team
    console.error(
      `Funds off-ramped but payout failed. ` +
      `Off-ramp ID: ${result.bridgeOfframp.tx_id}, Amount: ${amount} ${currency}`
    );
    result.status = 'offramp_complete_payout_failed';
  }
  
  // Add additional logic for other failure scenarios if needed
} 