"use strict";
/**
 * Payment orchestration service for Liquicity.
 *
 * This module provides high-level orchestration of payment flows,
 * coordinating between different payment providers and cross-chain bridge operations.
 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.transferCrossBorder = transferCrossBorder;
const factory_1 = require("../providers/factory");
const payment_service_1 = require("./payment_service");
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
function transferCrossBorder(options) {
    return __awaiter(this, void 0, void 0, function* () {
        const { userId, amount, srcCountryCode, dstCountryCode, currency, srcChain = 1, // Default: Ethereum Mainnet
        dstChain = 137, // Default: Polygon
        recipient, metadata } = options;
        const result = {
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
            result.debit = yield (0, payment_service_1.receiveFiat)(userId, amount, currency);
            // Step 2: On-ramp via Stargate (unified liquidity pools across chains)
            console.log(`Bridging ${amount} ${currency} from chain ${srcChain} to ${dstChain}`);
            const bridge = (0, factory_1.getBridgeProvider)();
            result.bridgeOnramp = yield bridge.onramp(amount, currency, srcChain, dstChain, recipient || userId);
            // Step 3: Transfer across chains (handled internally by Stargate)
            console.log(`Cross-chain transfer complete with transaction ID: ${result.bridgeOnramp.tx_id}`);
            // Step 4: Off-ramp to destination fiat
            console.log(`Off-ramping to fiat in destination country ${dstCountryCode}`);
            const bankAccountId = (metadata === null || metadata === void 0 ? void 0 : metadata.bankAccountId) || userId;
            result.bridgeOfframp = yield bridge.offramp(amount, currency, dstChain, bankAccountId);
            // Step 5: Pay out to the recipient
            console.log(`Sending fiat payout of ${amount} ${currency}`);
            result.payout = yield (0, payment_service_1.sendFiat)(userId, amount, currency);
            result.status = 'completed';
            return result;
        }
        catch (error) {
            console.error(`Error during cross-border transfer: ${error.message}`);
            result.status = 'failed';
            result.errors.push(error.message);
            // Attempt fallback and recovery based on where the failure occurred
            try {
                yield handleTransferFallback(result, userId, amount, currency);
            }
            catch (fallbackError) {
                console.error(`Fallback handling failed: ${fallbackError.message}`);
                result.errors.push(`Fallback error: ${fallbackError.message}`);
            }
            return result;
        }
    });
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
function handleTransferFallback(result, userId, amount, currency) {
    return __awaiter(this, void 0, void 0, function* () {
        // Check where the failure occurred and apply appropriate fallback
        if (result.debit && !result.bridgeOnramp) {
            // Failed after debit but before bridge on-ramp - refund the user
            console.log(`Initiating refund for user ${userId} of ${amount} ${currency}`);
            yield (0, payment_service_1.sendFiat)(userId, amount, currency, true); // true = refund
            result.status = 'refunded';
        }
        else if (result.bridgeOnramp && !result.bridgeOfframp) {
            // Failed after on-ramp but before off-ramp
            // This is a complex state requiring manual intervention
            console.error(`Transfer in indeterminate state. On-ramped but not off-ramped. ` +
                `Transaction ID: ${result.bridgeOnramp.tx_id}, Amount: ${amount} ${currency}`);
            result.status = 'indeterminate_needs_review';
        }
        else if (result.bridgeOfframp && !result.payout) {
            // Failed after off-ramp but before payout
            // Need to retry the payout or notify operations team
            console.error(`Funds off-ramped but payout failed. ` +
                `Off-ramp ID: ${result.bridgeOfframp.tx_id}, Amount: ${amount} ${currency}`);
            result.status = 'offramp_complete_payout_failed';
        }
        // Add additional logic for other failure scenarios if needed
    });
}
