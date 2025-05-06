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
const chai_1 = require("chai");
const stargate_provider_1 = require("../app/payments/providers/stargate_provider");
const mocha_1 = require("mocha");
(0, mocha_1.describe)('StargateProvider', () => {
    let originalEnv;
    let provider;
    (0, mocha_1.beforeEach)(() => {
        // Save original env vars
        originalEnv = Object.assign({}, process.env);
        // Setup test environment
        process.env.TESTING = '1';
        process.env.BRIDGE_SIGNER_PRIVATE_KEY = 'test_private_key';
        process.env.STARGATE_RPC_URLS = JSON.stringify({
            1: 'https://eth-mainnet.example.com',
            137: 'https://polygon-mainnet.example.com'
        });
        process.env.STARGATE_SLIPPAGE_BPS = '300';
        // Create provider instance
        provider = new stargate_provider_1.StargateProvider();
    });
    (0, mocha_1.afterEach)(() => {
        // Restore original env vars
        process.env = originalEnv;
    });
    (0, mocha_1.describe)('onramp', () => {
        (0, mocha_1.it)('should successfully bridge tokens in test mode', () => __awaiter(void 0, void 0, void 0, function* () {
            const result = yield provider.onramp(100, 'USDC', 'ethereum', 'polygon', '0x1234567890abcdef1234567890abcdef12345678');
            (0, chai_1.expect)(result).to.exist;
            (0, chai_1.expect)(result.tx_id).to.be.a('string');
            (0, chai_1.expect)(result.tx_id).to.include('stargate_onramp_');
            (0, chai_1.expect)(result.status).to.equal('completed');
            (0, chai_1.expect)(result.settled_at).to.be.instanceOf(Date);
        }));
        (0, mocha_1.it)('should handle unsupported chain errors', () => __awaiter(void 0, void 0, void 0, function* () {
            try {
                yield provider.onramp(100, 'USDC', 'unsupported_chain', 'polygon', '0x1234567890abcdef1234567890abcdef12345678');
                chai_1.expect.fail('Should have thrown an error');
            }
            catch (error) {
                (0, chai_1.expect)(error.message).to.include('Unsupported chain');
            }
        }));
        (0, mocha_1.it)('should handle unsupported currency errors', () => __awaiter(void 0, void 0, void 0, function* () {
            try {
                yield provider.onramp(100, 'INVALID', 'ethereum', 'polygon', '0x1234567890abcdef1234567890abcdef12345678');
                chai_1.expect.fail('Should have thrown an error');
            }
            catch (error) {
                (0, chai_1.expect)(error.message).to.include('Unsupported currency');
            }
        }));
    });
    (0, mocha_1.describe)('offramp', () => {
        (0, mocha_1.it)('should successfully offramp tokens in test mode', () => __awaiter(void 0, void 0, void 0, function* () {
            const result = yield provider.offramp(100, 'USDC', 'ethereum', 'bank_account_123');
            (0, chai_1.expect)(result).to.exist;
            (0, chai_1.expect)(result.tx_id).to.be.a('string');
            (0, chai_1.expect)(result.tx_id).to.include('stargate_offramp_');
            (0, chai_1.expect)(result.status).to.equal('completed');
            (0, chai_1.expect)(result.settled_at).to.be.instanceOf(Date);
        }));
        (0, mocha_1.it)('should handle unsupported chain errors', () => __awaiter(void 0, void 0, void 0, function* () {
            try {
                yield provider.offramp(100, 'USDC', 'unsupported_chain', 'bank_account_123');
                chai_1.expect.fail('Should have thrown an error');
            }
            catch (error) {
                (0, chai_1.expect)(error.message).to.include('Unsupported chain');
            }
        }));
    });
});
