"use strict";
/**
 * Payment service for Liquicity.
 *
 * This module provides basic payment operations for sending and
 * receiving fiat currency through payment providers.
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
exports.receiveFiat = receiveFiat;
exports.sendFiat = sendFiat;
const factory_1 = require("../providers/factory");
/**
 * Receive fiat currency from a user's account
 *
 * @param userId ID of the user to receive from
 * @param amount Amount to receive
 * @param currency Currency code (e.g., "USD")
 * @returns Transaction result
 */
function receiveFiat(userId, amount, currency) {
    return __awaiter(this, void 0, void 0, function* () {
        // Determine the country code from the user profile or transaction data
        // For simplicity, defaulting to "US" in this implementation
        const countryCode = "US";
        // Get the appropriate payment provider for the country
        const provider = (0, factory_1.getProvider)(countryCode);
        // Execute the pull operation
        // This would normally use account details from a database
        return yield provider.pull(amount, currency, userId);
    });
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
function sendFiat(userId_1, amount_1, currency_1) {
    return __awaiter(this, arguments, void 0, function* (userId, amount, currency, isRefund = false) {
        // Determine the country code from the user profile or transaction data
        // For simplicity, defaulting to "US" in this implementation
        const countryCode = "US";
        // Get the appropriate payment provider for the country
        const provider = (0, factory_1.getProvider)(countryCode);
        // Execute the push operation
        // This would normally use account details from a database
        const metadata = isRefund
            ? { refund: true, original_user_id: userId }
            : { user_id: userId };
        return yield provider.push(amount, currency, userId, metadata);
    });
}
