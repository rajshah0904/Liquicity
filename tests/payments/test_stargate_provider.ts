import { expect } from 'chai';
import { StargateProvider } from '../../app/payments/providers/stargate_provider';
import { BridgeResult } from '../../app/payments/providers/bridge_base';
import { describe, it, beforeEach, afterEach } from 'mocha';
import * as sinon from 'sinon';

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

describe('StargateProvider', () => {
  let provider: StargateProvider;
  let originalEnv: NodeJS.ProcessEnv;
  
  beforeEach(() => {
    // Save original environment
    originalEnv = { ...process.env };
    
    // Setup test environment variables
    process.env.TESTING = '0'; // Use real mode for testing mocked SDK
    process.env.BRIDGE_SIGNER_PRIVATE_KEY = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef';
    process.env.STARGATE_RPC_URLS = JSON.stringify({
      1: 'https://mainnet.infura.io/v3/test-key',
      56: 'https://bsc-dataseed.binance.org/'
    });
    process.env.STARGATE_SLIPPAGE_BPS = '100'; // 1% slippage
    
    // Initialize provider
    provider = new StargateProvider();
    
    // Replace the provider's SDK with our controlled mock
    (provider as any).sdk = {
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
  
  afterEach(() => {
    // Restore original environment
    process.env = originalEnv;
    sinon.restore();
  });
  
  describe('onramp', () => {
    it('should successfully bridge tokens between chains', async () => {
      // Test parameters
      const amount = 100;
      const currency = 'USDC';
      const srcChain = 'ethereum';
      const dstChain = 'polygon';
      const recipient = '0xabcdef1234567890abcdef1234567890abcdef12';
      
      // Execute onramp
      const result = await provider.onramp(amount, currency, srcChain, dstChain, recipient);
      
      // Verify result
      expect(result).to.exist;
      expect(result.tx_id).to.equal('test-tx-hash-123');
      expect(result.status).to.equal('completed');
      expect(result.settled_at).to.be.instanceOf(Date);
    });
  });
  
  describe('offramp', () => {
    it('should successfully offramp tokens to fiat', async () => {
      // Test parameters
      const amount = 200;
      const currency = 'USDC';
      const chain = 'ethereum';
      const bankAccountId = 'bank-123';
      
      // Switch to test mode for offramp since it's not fully implemented
      process.env.TESTING = '1';
      provider = new StargateProvider();
      
      // Execute offramp
      const result = await provider.offramp(amount, currency, chain, bankAccountId);
      
      // Verify result
      expect(result).to.exist;
      expect(result.tx_id).to.include('stargate_offramp_');
      expect(result.status).to.equal('completed');
      expect(result.settled_at).to.be.instanceOf(Date);
    });
  });
}); 