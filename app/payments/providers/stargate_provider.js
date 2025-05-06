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
exports.StargateProvider = void 0;
const ethers_1 = require("ethers");
const stargate_1 = require("@stargate-protocol/stargate");
const lz_sdk_1 = require("@layerzerolabs/lz-sdk");
const crypto_1 = require("crypto");
// Mock exchange service for offramp simulation
class ExchangeService {
    constructor(name) {
        this.name = name;
    }
    transferToExchange(amount, currency, address) {
        return __awaiter(this, void 0, void 0, function* () {
            console.log(`[${this.name}] Transferring ${amount} ${currency} from ${address} to exchange wallet`);
            // Simulate API call delay
            yield new Promise(resolve => setTimeout(resolve, 500));
            return `exchange_transfer_${(0, crypto_1.randomUUID)().slice(0, 8)}`;
        });
    }
    withdrawToBank(amount, currency, bankAccountId) {
        return __awaiter(this, void 0, void 0, function* () {
            console.log(`[${this.name}] Withdrawing ${amount} ${currency} to bank account ${bankAccountId}`);
            // Simulate API call delay
            yield new Promise(resolve => setTimeout(resolve, 500));
            return `bank_withdrawal_${(0, crypto_1.randomUUID)().slice(0, 8)}`;
        });
    }
}
// Status mapping
const TX_STATUS_MAP = {
    'completed': 'completed',
    'pending': 'pending',
    'failed': 'failed'
};
class StargateProvider {
    constructor() {
        this.sdk = null;
        this.signer = null;
        this.providerClients = {};
        this.offrampServices = {};
        // Initialize chain ID mappings
        this.chainIdMap = {
            'ethereum': lz_sdk_1.ChainId.ETHEREUM,
            'bsc': lz_sdk_1.ChainId.BSC,
            'avalanche': lz_sdk_1.ChainId.AVALANCHE,
            'polygon': lz_sdk_1.ChainId.POLYGON,
            'arbitrum': lz_sdk_1.ChainId.ARBITRUM,
            'optimism': lz_sdk_1.ChainId.OPTIMISM,
            'fantom': lz_sdk_1.ChainId.FANTOM,
        };
        // Initialize pool ID mappings for each chain and supported tokens
        this.poolIdMap = {
            [lz_sdk_1.ChainId.ETHEREUM]: {
                'USDC': 1,
                'USDT': 2,
                'ETH': 13,
            },
            [lz_sdk_1.ChainId.BSC]: {
                'USDC': 1,
                'USDT': 2,
                'BUSD': 5,
            },
            [lz_sdk_1.ChainId.AVALANCHE]: {
                'USDC': 1,
                'USDT': 2,
            },
            [lz_sdk_1.ChainId.POLYGON]: {
                'USDC': 1,
                'USDT': 2,
            },
            [lz_sdk_1.ChainId.ARBITRUM]: {
                'USDC': 1,
                'USDT': 2,
                'ETH': 13,
            },
            [lz_sdk_1.ChainId.OPTIMISM]: {
                'USDC': 1,
                'ETH': 13,
            },
            [lz_sdk_1.ChainId.FANTOM]: {
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
    initializeOfframpServices() {
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
            '1': new ExchangeService('Coinbase'), // Ethereum
            '137': new ExchangeService('Binance'), // Polygon
            '56': new ExchangeService('Binance'), // BSC
        };
    }
    loadEnvironmentVariables() {
        try {
            // Load RPC URLs from environment
            if (process.env.STARGATE_RPC_URLS) {
                this.rpcUrls = JSON.parse(process.env.STARGATE_RPC_URLS);
            }
            else {
                console.warn('STARGATE_RPC_URLS environment variable not set');
            }
            // Load slippage from environment
            if (process.env.STARGATE_SLIPPAGE_BPS) {
                this.slippageBps = parseInt(process.env.STARGATE_SLIPPAGE_BPS);
            }
        }
        catch (error) {
            console.error('Error loading environment variables for StargateProvider:', error);
        }
    }
    initializeProvider() {
        // Skip initialization in test mode
        if (process.env.TESTING === '1') {
            console.log('StargateProvider running in TEST mode');
            return;
        }
        try {
            // Create provider clients for each chain
            for (const [chainIdStr, rpcUrl] of Object.entries(this.rpcUrls)) {
                const chainId = parseInt(chainIdStr);
                this.providerClients[chainId] = new ethers_1.ethers.providers.JsonRpcProvider(rpcUrl);
            }
            // Initialize signer
            if (process.env.BRIDGE_SIGNER_PRIVATE_KEY) {
                // Default to Ethereum as the base network if available
                const baseChainId = this.rpcUrls[lz_sdk_1.ChainId.ETHEREUM]
                    ? lz_sdk_1.ChainId.ETHEREUM
                    : parseInt(Object.keys(this.rpcUrls)[0]);
                if (baseChainId && this.providerClients[baseChainId]) {
                    this.signer = new ethers_1.ethers.Wallet(process.env.BRIDGE_SIGNER_PRIVATE_KEY, this.providerClients[baseChainId]);
                    console.log(`Initialized Stargate signer for chain ID ${baseChainId}`);
                    // Initialize the Stargate SDK
                    this.sdk = new stargate_1.StargateSDK({
                        rpcUrls: this.rpcUrls,
                        signer: this.signer
                    });
                }
                else {
                    console.error('No valid provider client available for initializing signer');
                }
            }
            else {
                console.error('BRIDGE_SIGNER_PRIVATE_KEY environment variable not set');
            }
        }
        catch (error) {
            console.error('Error initializing StargateProvider:', error);
        }
    }
    getChainId(chainName) {
        const chainId = this.chainIdMap[chainName.toLowerCase()];
        if (!chainId) {
            throw new Error(`Unsupported chain: ${chainName}`);
        }
        return chainId;
    }
    getPoolId(chainId, currency) {
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
    getProvider(chainId) {
        const provider = this.providerClients[chainId];
        if (!provider) {
            throw new Error(`No provider configured for chain ID: ${chainId}`);
        }
        return provider;
    }
    getOfframpService(chain) {
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
    onramp(amount, currency, srcChain, dstChain, recipient) {
        return __awaiter(this, void 0, void 0, function* () {
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
                const amountBigNum = ethers_1.ethers.utils.parseUnits(amount.toString(), decimals);
                // Special handling for ETH
                if (currency.toUpperCase() === 'ETH') {
                    const result = yield this.sdk.swapETH({
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
                const result = yield this.sdk.swap({
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
            }
            catch (error) {
                console.error('Error in StargateProvider.onramp:', error);
                throw error;
            }
        });
    }
    /**
     * Offramps tokens from a chain to fiat currency (bank account)
     * This implements a two-step approach:
     * 1. Transfer tokens to an exchange or fiat on-ramp service
     * 2. Initiate a withdrawal to the user's bank account
     */
    offramp(amount, currency, chain, bankAccountId) {
        return __awaiter(this, void 0, void 0, function* () {
            var _a;
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
                const exchangeAddress = ((_a = this.signer) === null || _a === void 0 ? void 0 : _a.address) || `0x${(0, crypto_1.randomUUID)().replace(/-/g, '')}`;
                // Step 1: Transfer tokens to the exchange or fiat on-ramp service
                const transferTxId = yield offrampService.transferToExchange(amount, currency, exchangeAddress);
                console.log(`Successfully transferred tokens to exchange: ${transferTxId}`);
                // Step 2: Initiate withdrawal from exchange to bank account
                const withdrawalTxId = yield offrampService.withdrawToBank(amount, currency, bankAccountId);
                console.log(`Successfully initiated withdrawal to bank account: ${withdrawalTxId}`);
                // Return combined result
                return {
                    tx_id: `${withdrawalTxId}_${transferTxId}`,
                    status: 'pending', // In a real implementation, this would be determined by the service
                    settled_at: new Date(Date.now() + 24 * 60 * 60 * 1000) // Estimate settlement in 24 hours
                };
            }
            catch (error) {
                console.error('Error in StargateProvider.offramp:', error);
                throw error;
            }
        });
    }
    /**
     * Creates a mock bridge result for testing or unsupported operations
     */
    mockBridgeResult(operation = 'generic') {
        return {
            tx_id: `stargate_${operation}_${(0, crypto_1.randomUUID)().slice(0, 8)}`,
            status: 'completed',
            settled_at: new Date()
        };
    }
}
exports.StargateProvider = StargateProvider;
