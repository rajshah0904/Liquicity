import { expect } from 'chai';
import { StargateProvider } from '../app/payments/providers/stargate_provider';
import { describe, it, beforeEach, afterEach } from 'mocha';

describe('StargateProvider', () => {
  let originalEnv: NodeJS.ProcessEnv;
  let provider: StargateProvider;

  beforeEach(() => {
    // Save original env vars
    originalEnv = { ...process.env };
    
    // Setup test environment
    process.env.TESTING = '1';
    process.env.BRIDGE_SIGNER_PRIVATE_KEY = 'test_private_key';
    process.env.STARGATE_RPC_URLS = JSON.stringify({
      1: 'https://eth-mainnet.example.com',
      137: 'https://polygon-mainnet.example.com'
    });
    process.env.STARGATE_SLIPPAGE_BPS = '300';
    
    // Create provider instance
    provider = new StargateProvider();
  });

  afterEach(() => {
    // Restore original env vars
    process.env = originalEnv;
  });

  describe('onramp', () => {
    it('should successfully bridge tokens in test mode', async () => {
      const result = await provider.onramp(100, 'USDC', 'ethereum', 'polygon', '0x1234567890abcdef1234567890abcdef12345678');
      
      expect(result).to.exist;
      expect(result.tx_id).to.be.a('string');
      expect(result.tx_id).to.include('stargate_onramp_');
      expect(result.status).to.equal('completed');
      expect(result.settled_at).to.be.instanceOf(Date);
    });

    it('should handle unsupported chain errors', async () => {
      try {
        await provider.onramp(100, 'USDC', 'unsupported_chain', 'polygon', '0x1234567890abcdef1234567890abcdef12345678');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).to.include('Unsupported chain');
      }
    });

    it('should handle unsupported currency errors', async () => {
      try {
        await provider.onramp(100, 'INVALID', 'ethereum', 'polygon', '0x1234567890abcdef1234567890abcdef12345678');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).to.include('Unsupported currency');
      }
    });
  });

  describe('offramp', () => {
    it('should successfully offramp tokens in test mode', async () => {
      const result = await provider.offramp(100, 'USDC', 'ethereum', 'bank_account_123');
      
      expect(result).to.exist;
      expect(result.tx_id).to.be.a('string');
      expect(result.tx_id).to.include('stargate_offramp_');
      expect(result.status).to.equal('completed');
      expect(result.settled_at).to.be.instanceOf(Date);
    });

    it('should handle unsupported chain errors', async () => {
      try {
        await provider.offramp(100, 'USDC', 'unsupported_chain', 'bank_account_123');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).to.include('Unsupported chain');
      }
    });
  });
}); 