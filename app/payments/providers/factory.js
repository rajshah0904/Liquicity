"use strict";
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
exports.getProvider = getProvider;
exports.getBridgeProvider = getBridgeProvider;
const stargate_provider_1 = require("./stargate_provider");
// Mock implementations for payment providers (in a real app, these would be proper implementations)
class ModernTreasuryProvider {
    pull(amount, currency, accountOrId) {
        return __awaiter(this, void 0, void 0, function* () {
            console.log(`ModernTreasury pulling ${amount} ${currency} from ${accountOrId}`);
            return { transaction_id: `mt_pull_${Date.now()}`, status: "pending" };
        });
    }
    push(amount, currency, accountOrId, metadata) {
        return __awaiter(this, void 0, void 0, function* () {
            console.log(`ModernTreasury pushing ${amount} ${currency} to ${accountOrId}`);
            return { transaction_id: `mt_push_${Date.now()}`, status: "pending" };
        });
    }
}
class RapydProvider {
    pull(amount, currency, accountOrId) {
        return __awaiter(this, void 0, void 0, function* () {
            console.log(`Rapyd pulling ${amount} ${currency} from ${accountOrId}`);
            return { transaction_id: `rapyd_pull_${Date.now()}`, status: "pending" };
        });
    }
    push(amount, currency, accountOrId, metadata) {
        return __awaiter(this, void 0, void 0, function* () {
            console.log(`Rapyd pushing ${amount} ${currency} to ${accountOrId}`);
            return { transaction_id: `rapyd_push_${Date.now()}`, status: "pending" };
        });
    }
}
// Map of country codes to provider classes
const COUNTRY_PROVIDER_MAP = {
    "US": ModernTreasuryProvider,
    "CA": RapydProvider,
    "MX": RapydProvider,
    "NG": RapydProvider,
};
// Provider instances cache
const _provider_instances = {};
let _bridge_provider_instance = null;
/**
 * Get the appropriate payment provider for a country code
 *
 * @param countryCode ISO-2 country code (e.g., 'US', 'CA')
 * @returns An instance of the appropriate PaymentProvider
 * @throws Error if no provider is available for the given country code
 */
function getProvider(countryCode) {
    const c = countryCode.toUpperCase();
    // Check if the instance is already cached
    if (_provider_instances[c]) {
        return _provider_instances[c];
    }
    // Determine the provider class
    const ProviderClass = COUNTRY_PROVIDER_MAP[c];
    if (!ProviderClass) {
        throw new Error(`No payment provider available for country code: ${countryCode}`);
    }
    // Check if we already have an instance of this provider class
    for (const [code, instance] of Object.entries(_provider_instances)) {
        if (instance instanceof ProviderClass) {
            // Cache this instance for the current country code too
            _provider_instances[c] = instance;
            return instance;
        }
    }
    // Create a new instance
    const provider = new ProviderClass();
    // Cache the instance for future use
    _provider_instances[c] = provider;
    return provider;
}
/**
 * Get the bridge provider instance
 *
 * @returns An instance of BridgeProvider (currently only StargateProvider is supported)
 */
function getBridgeProvider() {
    if (_bridge_provider_instance === null) {
        _bridge_provider_instance = new stargate_provider_1.StargateProvider();
    }
    return _bridge_provider_instance;
}
