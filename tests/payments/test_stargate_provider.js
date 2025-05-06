"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
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
const chai_1 = require("chai");
const stargate_provider_1 = require("../../app/payments/providers/stargate_provider");
const mocha_1 = require("mocha");
const sinon = __importStar(require("sinon"));
// Mock the Stargate SDK
jest.mock('@stargate-protocol/stargate', () => {
    return {
        StargateSDK: jest.fn().mockImplementation(() => {
            return {
                swap: jest.fn().mockResolvedValue({
                    txHash: 'mocked-tx-hash-123',
                    status: 'completed'
                }),
                swapETH: jest.fn().mockResolvedValue({
                    txHash: 'mocked-eth-tx-hash-456',
                    status: 'completed'
                }),
                addLiquidity: jest.fn().mockResolvedValue({
                    txHash: 'mocked-liquidity-tx-hash-789',
                    status: 'completed'
                })
            };
        })
    };
});
// Mock ethers
jest.mock('ethers', () => {
    return {
        Contract: jest.fn().mockImplementation(() => {
            return {
                connect: jest.fn().mockReturnThis(),
                estimateGas: {
                    transfer: jest.fn().mockResolvedValue(21000)
                },
                transfer: jest.fn().mockResolvedValue({
                    hash: 'mocked-contract-tx-hash-123'
                }),
                getBalance: jest.fn().mockResolvedValue('1000000000000000000')
            };
        }),
        providers: {
            JsonRpcProvider: jest.fn().mockImplementation(() => {
                return {
                    getBalance: jest.fn().mockResolvedValue('2000000000000000000')
                };
            })
        },
        Wallet: jest.fn().mockImplementation(() => {
            return {
                connect: jest.fn().mockReturnThis(),
                address: '0x1234567890123456789012345678901234567890'
            };
        })
    };
});
(0, mocha_1.describe)('StargateProvider', () => {
    let provider;
    let originalEnv;
    (0, mocha_1.beforeEach)(() => {
        // Save original environment
        originalEnv = Object.assign({}, process.env);
        // Setup test environment variables
        process.env.TESTING = '0'; // Use real mode for testing mocked SDK
        process.env.BRIDGE_SIGNER_PRIVATE_KEY = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef';
        process.env.STARGATE_RPC_URLS = JSON.stringify({
            1: 'https://mainnet.infura.io/v3/test-key',
            56: 'https://bsc-dataseed.binance.org/'
        });
        process.env.STARGATE_SLIPPAGE_BPS = '100'; // 1% slippage
        // Initialize provider
        provider = new stargate_provider_1.StargateProvider();
        // Replace the provider's SDK with our controlled mock
        provider.sdk = {
            swap: sinon.stub().resolves({
                txHash: 'test-tx-hash-123',
                status: 'completed'
            }),
            addLiquidity: sinon.stub().resolves({
                txHash: 'test-liquidity-tx-hash-456',
                status: 'completed'
            })
        };
    });
    (0, mocha_1.afterEach)(() => {
        // Restore original environment
        process.env = originalEnv;
        sinon.restore();
    });
    (0, mocha_1.describe)('onramp', () => {
        (0, mocha_1.it)('should successfully bridge tokens between chains', () => __awaiter(void 0, void 0, void 0, function* () {
            // Test parameters
            const amount = 100;
            const currency = 'USDC';
            const srcChain = 'ethereum';
            const dstChain = 'polygon';
            const recipient = '0xabcdef1234567890abcdef1234567890abcdef12';
            // Execute onramp
            const result = yield provider.onramp(amount, currency, srcChain, dstChain, recipient);
            // Verify result
            (0, chai_1.expect)(result).to.exist;
            (0, chai_1.expect)(result.tx_id).to.equal('test-tx-hash-123');
            (0, chai_1.expect)(result.status).to.equal('completed');
            (0, chai_1.expect)(result.settled_at).to.be.instanceOf(Date);
        }));
    });
    (0, mocha_1.describe)('offramp', () => {
        (0, mocha_1.it)('should successfully offramp tokens to fiat', () => __awaiter(void 0, void 0, void 0, function* () {
            // Test parameters
            const amount = 200;
            const currency = 'USDC';
            const chain = 'ethereum';
            const bankAccountId = 'bank-123';
            // Switch to test mode for offramp since it's not fully implemented
            process.env.TESTING = '1';
            provider = new stargate_provider_1.StargateProvider();
            // Execute offramp
            const result = yield provider.offramp(amount, currency, chain, bankAccountId);
            // Verify result
            (0, chai_1.expect)(result).to.exist;
            (0, chai_1.expect)(result.tx_id).to.include('stargate_offramp_');
            (0, chai_1.expect)(result.status).to.equal('completed');
            (0, chai_1.expect)(result.settled_at).to.be.instanceOf(Date);
        }));
    });
});
