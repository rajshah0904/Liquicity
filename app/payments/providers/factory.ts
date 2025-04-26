import { StargateProvider } from "./stargate_provider";
import { BridgeProvider } from "./bridge_base";

// Simplified interface for payment providers
interface PaymentProvider {
  pull(amount: number, currency: string, accountOrId: any): Promise<any>;
  push(amount: number, currency: string, accountOrId: any, metadata?: any): Promise<any>;
}

// Mock implementations for payment providers (in a real app, these would be proper implementations)
class ModernTreasuryProvider implements PaymentProvider {
  async pull(amount: number, currency: string, accountOrId: any): Promise<any> {
    console.log(`ModernTreasury pulling ${amount} ${currency} from ${accountOrId}`);
    return { transaction_id: `mt_pull_${Date.now()}`, status: "pending" };
  }
  
  async push(amount: number, currency: string, accountOrId: any, metadata?: any): Promise<any> {
    console.log(`ModernTreasury pushing ${amount} ${currency} to ${accountOrId}`);
    return { transaction_id: `mt_push_${Date.now()}`, status: "pending" };
  }
}

class RapydProvider implements PaymentProvider {
  async pull(amount: number, currency: string, accountOrId: any): Promise<any> {
    console.log(`Rapyd pulling ${amount} ${currency} from ${accountOrId}`);
    return { transaction_id: `rapyd_pull_${Date.now()}`, status: "pending" };
  }
  
  async push(amount: number, currency: string, accountOrId: any, metadata?: any): Promise<any> {
    console.log(`Rapyd pushing ${amount} ${currency} to ${accountOrId}`);
    return { transaction_id: `rapyd_push_${Date.now()}`, status: "pending" };
  }
}

// Map of country codes to provider classes
const COUNTRY_PROVIDER_MAP: Record<string, new () => PaymentProvider> = {
  "US": ModernTreasuryProvider,
  "CA": RapydProvider,
  "MX": RapydProvider,
  "NG": RapydProvider,
};

// Provider instances cache
const _provider_instances: Record<string, PaymentProvider> = {};
let _bridge_provider_instance: StargateProvider | null = null;

/**
 * Get the appropriate payment provider for a country code
 * 
 * @param countryCode ISO-2 country code (e.g., 'US', 'CA')
 * @returns An instance of the appropriate PaymentProvider
 * @throws Error if no provider is available for the given country code
 */
export function getProvider(countryCode: string): PaymentProvider {
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
export function getBridgeProvider(): BridgeProvider {
  if (_bridge_provider_instance === null) {
    _bridge_provider_instance = new StargateProvider();
  }
  
  return _bridge_provider_instance;
} 