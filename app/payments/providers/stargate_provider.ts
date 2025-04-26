import { ethers } from 'ethers';
import { StargateSDK } from '@stargate-protocol/stargate';
import { ChainId } from '@layerzerolabs/lz-sdk';
import { randomUUID } from 'crypto';
import { BridgeProvider, BridgeResult } from './bridge_base';

// Add interfaces for offramp services
interface OfframpService {
  name: string;
  transferToExchange(amount: number, currency: string, address: string): Promise<string>;
  withdrawToBank(amount: number, currency: string, bankAccountId: string): Promise<string>;
}

// Mock exchange service for offramp simulation
class ExchangeService implements OfframpService {
  name: string;
  
  constructor(name: string) {
    this.name = name;
  }
  
  async transferToExchange(amount: number, currency: string, address: string): Promise<string> {
    console.log(`[${this.name}] Transferring ${amount} ${currency} from ${address} to exchange wallet`);
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));
    return `exchange_transfer_${randomUUID().slice(0, 8)}`;
  }
  
  async withdrawToBank(amount: number, currency: string, bankAccountId: string): Promise<string> {
    console.log(`[${this.name}] Withdrawing ${amount} ${currency} to bank account ${bankAccountId}`);
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));
    return `bank_withdrawal_${randomUUID().slice(0, 8)}`;
  }
}

interface ChainMapping {
  [key: string]: number;  // Maps chain name to chain ID
}

interface PoolMapping {
  [chainId: number]: {
    [currency: string]: number;  // Maps currency to pool ID
  };
}

interface RpcUrlMapping {
  [chainId: number]: string;  // Maps chain ID to RPC URL
}

// Status mapping
const TX_STATUS_MAP: { [key: string]: string } = {
  'completed': 'completed',
  'pending': 'pending',
  'failed': 'failed'
};

export class StargateProvider implements BridgeProvider {
  private chainIdMap: ChainMapping;
  private poolIdMap: PoolMapping;
  private rpcUrls: RpcUrlMapping;
  private slippageBps: number;
  private sdk: StargateSDK | null = null;
  private signer: ethers.Wallet | null = null;
  private providerClients: { [chainId: number]: ethers.providers.JsonRpcProvider } = {};
  private offrampServices: { [chain: string]: OfframpService } = {};

  constructor() {
    // Initialize chain ID mappings
    this.chainIdMap = {
      'ethereum': ChainId.ETHEREUM,
      'bsc': ChainId.BSC,
      'avalanche': ChainId.AVALANCHE,
      'polygon': ChainId.POLYGON,
      'arbitrum': ChainId.ARBITRUM,
      'optimism': ChainId.OPTIMISM,
      'fantom': ChainId.FANTOM,
    };

    // Initialize pool ID mappings for each chain and supported tokens
    this.poolIdMap = {
      [ChainId.ETHEREUM]: {
        'USDC': 1,
        'USDT': 2,
        'ETH': 13,
      },
      [ChainId.BSC]: {
        'USDC': 1,
        'USDT': 2,
        'BUSD': 5,
      },
      [ChainId.AVALANCHE]: {
        'USDC': 1,
        'USDT': 2,
      },
      [ChainId.POLYGON]: {
        'USDC': 1,
        'USDT': 2,
      },
      [ChainId.ARBITRUM]: {
        'USDC': 1,
        'USDT': 2,
        'ETH': 13,
      },
      [ChainId.OPTIMISM]: {
        'USDC': 1,
        'ETH': 13,
      },
      [ChainId.FANTOM]: {
        'USDC': 1,
      },
    };

    this.rpcUrls = {};
    this.slippageBps = 100; // Default 1% slippage

    // Initialize offramp services for each chain
    this.initializeOfframpServices();
    this.loadEnvironmentVariables();
    this.initializeProvider();
  }

  private initializeOfframpServices() {
    // Set up offramp services for each supported chain
    this.offrampServices = {
      'ethereum': new ExchangeService('Coinbase'),
      'polygon': new ExchangeService('Binance'),
      'bsc': new ExchangeService('Binance'),
      'avalanche': new ExchangeService('Coinbase'),
      'arbitrum': new ExchangeService('Kraken'),
      'optimism': new ExchangeService('Kraken'),
      'fantom': new ExchangeService('Binance'),
      // Add chain IDs as strings too for direct chain ID references
      '1': new ExchangeService('Coinbase'),  // Ethereum
      '137': new ExchangeService('Binance'), // Polygon
      '56': new ExchangeService('Binance'),  // BSC
    };
  }

  private loadEnvironmentVariables() {
    try {
      // Load RPC URLs from environment
      if (process.env.STARGATE_RPC_URLS) {
        this.rpcUrls = JSON.parse(process.env.STARGATE_RPC_URLS);
      } else {
        console.warn('STARGATE_RPC_URLS environment variable not set');
      }

      // Load slippage from environment
      if (process.env.STARGATE_SLIPPAGE_BPS) {
        this.slippageBps = parseInt(process.env.STARGATE_SLIPPAGE_BPS);
      }
    } catch (error) {
      console.error('Error loading environment variables for StargateProvider:', error);
    }
  }

  private initializeProvider() {
    // Skip initialization in test mode
    if (process.env.TESTING === '1') {
      console.log('StargateProvider running in TEST mode');
      return;
    }

    try {
      // Create provider clients for each chain
      for (const [chainIdStr, rpcUrl] of Object.entries(this.rpcUrls)) {
        const chainId = parseInt(chainIdStr);
        this.providerClients[chainId] = new ethers.providers.JsonRpcProvider(rpcUrl);
      }

      // Initialize signer
      if (process.env.BRIDGE_SIGNER_PRIVATE_KEY) {
        // Default to Ethereum as the base network if available
        const baseChainId = this.rpcUrls[ChainId.ETHEREUM] 
          ? ChainId.ETHEREUM 
          : parseInt(Object.keys(this.rpcUrls)[0]);
        
        if (baseChainId && this.providerClients[baseChainId]) {
          this.signer = new ethers.Wallet(
            process.env.BRIDGE_SIGNER_PRIVATE_KEY,
            this.providerClients[baseChainId]
          );
          console.log(`Initialized Stargate signer for chain ID ${baseChainId}`);
          
          // Initialize the Stargate SDK
          this.sdk = new StargateSDK({
            rpcUrls: this.rpcUrls,
            signer: this.signer
          });
        } else {
          console.error('No valid provider client available for initializing signer');
        }
      } else {
        console.error('BRIDGE_SIGNER_PRIVATE_KEY environment variable not set');
      }
    } catch (error) {
      console.error('Error initializing StargateProvider:', error);
    }
  }

  private getChainId(chainName: string): number {
    const chainId = this.chainIdMap[chainName.toLowerCase()];
    if (!chainId) {
      throw new Error(`Unsupported chain: ${chainName}`);
    }
    return chainId;
  }

  private getPoolId(chainId: number, currency: string): number {
    const chain = this.poolIdMap[chainId];
    if (!chain) {
      throw new Error(`No pool configuration for chain ID: ${chainId}`);
    }
    
    const poolId = chain[currency.toUpperCase()];
    if (!poolId) {
      throw new Error(`Unsupported currency ${currency} on chain ID ${chainId}`);
    }
    
    return poolId;
  }

  private getProvider(chainId: number): ethers.providers.JsonRpcProvider {
    const provider = this.providerClients[chainId];
    if (!provider) {
      throw new Error(`No provider configured for chain ID: ${chainId}`);
    }
    return provider;
  }

  private getOfframpService(chain: string | number): OfframpService {
    const chainKey = chain.toString().toLowerCase();
    const service = this.offrampServices[chainKey];
    
    if (!service) {
      throw new Error(`No offramp service configured for chain: ${chain}`);
    }
    
    return service;
  }

  /**
   * Bridges tokens from one chain to another using Stargate protocol
   */
  async onramp(
    amount: number,
    currency: string,
    srcChain: string,
    dstChain: string,
    recipient: string
  ): Promise<BridgeResult> {
    console.log(`StargateProvider.onramp: Bridging ${amount} ${currency} from ${srcChain} to ${dstChain} for ${recipient}`);

    // In test mode, return a mock result
    if (process.env.TESTING === '1') {
      return this.mockBridgeResult('onramp');
    }

    try {
      // Verify SDK is initialized
      if (!this.sdk) {
        throw new Error('Stargate SDK not initialized');
      }

      // Get chain IDs and pool IDs
      const srcChainId = this.getChainId(srcChain);
      const dstChainId = this.getChainId(dstChain);
      const srcPoolId = this.getPoolId(srcChainId, currency);
      const dstPoolId = this.getPoolId(dstChainId, currency);

      // Normalize amount to proper decimals (assuming USDC/USDT with 6 decimals)
      // For mainnet ERC20s:
      // - USDC, USDT have 6 decimal places
      // - ETH has 18 decimal places
      const decimals = currency.toUpperCase() === 'ETH' ? 18 : 6;
      const amountBigNum = ethers.utils.parseUnits(amount.toString(), decimals);

      // Special handling for ETH
      if (currency.toUpperCase() === 'ETH') {
        const result = await this.sdk.swapETH({
          srcChainId,
          dstChainId,
          amount: amountBigNum,
          dstPoolId,
          slippageBps: this.slippageBps,
          dstAddress: recipient,
        });

        return {
          tx_id: result.txHash,
          status: TX_STATUS_MAP[result.status] || 'pending',
          settled_at: new Date()
        };
      }

      // For other tokens (USDC, USDT, etc.)
      const result = await this.sdk.swap({
        srcChainId,
        dstChainId,
        srcPoolId,
        dstPoolId,
        amount: amountBigNum,
        slippageBps: this.slippageBps,
        dstAddress: recipient,
      });

      return {
        tx_id: result.txHash,
        status: TX_STATUS_MAP[result.status] || 'pending',
        settled_at: new Date()
      };
    } catch (error) {
      console.error('Error in StargateProvider.onramp:', error);
      throw error;
    }
  }

  /**
   * Offramps tokens from a chain to fiat currency (bank account)
   * This implements a two-step approach:
   * 1. Transfer tokens to an exchange or fiat on-ramp service
   * 2. Initiate a withdrawal to the user's bank account
   */
  async offramp(
    amount: number,
    currency: string,
    chain: string,
    bankAccountId: string
  ): Promise<BridgeResult> {
    console.log(`StargateProvider.offramp: Offramping ${amount} ${currency} from ${chain} to bank account ${bankAccountId}`);

    // In test mode, return a mock result
    if (process.env.TESTING === '1') {
      return this.mockBridgeResult('offramp');
    }

    try {
      // Get the appropriate offramp service for this chain
      const offrampService = this.getOfframpService(chain);
      
      // Get the recipient address (wallet) to transfer funds to
      // In a real implementation, this would be the exchange's deposit address
      const exchangeAddress = this.signer?.address || `0x${randomUUID().replace(/-/g, '')}`;
      
      // Step 1: Transfer tokens to the exchange or fiat on-ramp service
      const transferTxId = await offrampService.transferToExchange(
        amount,
        currency,
        exchangeAddress
      );
      
      console.log(`Successfully transferred tokens to exchange: ${transferTxId}`);
      
      // Step 2: Initiate withdrawal from exchange to bank account
      const withdrawalTxId = await offrampService.withdrawToBank(
        amount,
        currency,
        bankAccountId
      );
      
      console.log(`Successfully initiated withdrawal to bank account: ${withdrawalTxId}`);
      
      // Return combined result
      return {
        tx_id: `${withdrawalTxId}_${transferTxId}`,
        status: 'pending', // In a real implementation, this would be determined by the service
        settled_at: new Date(Date.now() + 24 * 60 * 60 * 1000) // Estimate settlement in 24 hours
      };
    } catch (error) {
      console.error('Error in StargateProvider.offramp:', error);
      throw error;
    }
  }

  /**
   * Creates a mock bridge result for testing or unsupported operations
   */
  private mockBridgeResult(operation: string = 'generic'): BridgeResult {
    return {
      tx_id: `stargate_${operation}_${randomUUID().slice(0, 8)}`,
      status: 'completed',
      settled_at: new Date()
    };
  }
} 