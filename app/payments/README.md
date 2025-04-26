# TerraFlow Payment Services

This directory contains the payment services and providers for the TerraFlow platform, which enable cross-border transfers between multiple countries.

## Architecture

The payment system is designed with a modular architecture:

- **Payment Providers**: Handle fiat currency transactions in specific countries
  - `ModernTreasuryProvider`: US domestic payments (ACH, Wire, RTP)
  - `RapydProvider`: International payments (Canada, Mexico, Nigeria)

- **Bridge Provider**: Handles cross-chain transfers for cross-border transactions
  - `StargateProvider`: Cross-chain bridging between different blockchains
  
- **Orchestration Services**: Coordinate the end-to-end payment flows
  - `transferCrossBorder`: Main function for executing cross-border transfers

## Supported Countries

- 🇺🇸 United States (via Modern Treasury)
- 🇨🇦 Canada (via Rapyd)
- 🇲🇽 Mexico (via Rapyd)
- 🇳🇬 Nigeria (via Rapyd)

## Supported Payment Rails

- ACH (US)
- Wire Transfer (US)
- RTP - Real-Time Payments (US)
- FedNow (US)
- EFT (Canada)
- SPEI (Mexico)
- NIBSS (Nigeria)

## Cross-Chain Bridging

### Switching to Stargate Protocol

We now use Stargate Protocol for cross-chain bridging because:

- **Unified Liquidity Pools**: Assets are available across all chains through unified pools
- **Native Asset Support**: No wrapped tokens required, reducing complexity and fees
- **Lower Latency**: Transactions confirm in seconds rather than minutes
- **Higher Throughput**: Batching transactions together for greater efficiency
- **Competitive Fees**: Lower cost structure compared to other cross-chain solutions

The Stargate Protocol provides these key benefits:

1. **Instant Guaranteed Finality**: No more waiting for block confirmations
2. **Delta Solving Mechanism**: Prevents liquidity fragmentation across chains
3. **Native Asset Transfers**: Tokens arrive on destination chains in their native form
4. **Composable**: Can be integrated with other DeFi protocols
5. **Layer Zero Security**: Built on the secure LayerZero messaging protocol

## Environment Variables

### Payment Providers

- `MODERN_TREASURY_API_KEY`: API key for Modern Treasury
- `MODERN_TREASURY_ORGANIZATION_ID`: Organization ID for Modern Treasury
- `MODERN_TREASURY_DEFAULT_ACCOUNT_ID`: Default account ID for Modern Treasury transactions
- `RAPYD_ACCESS_KEY`: Access key for Rapyd API
- `RAPYD_SECRET_KEY`: Secret key for Rapyd API

### Bridge Provider

- `BRIDGE_SIGNER_PRIVATE_KEY`: Private key for signing cross-chain transactions
- `STARGATE_RPC_URLS`: JSON object with RPC URLs for each chain ID
- `STARGATE_SLIPPAGE_BPS`: Slippage tolerance in basis points (default: 300 = 3%)

### Testing

- `TESTING`: Set to "1" to enable test mode with mock responses

## Usage

To execute a cross-border transfer:

```typescript
import { transferCrossBorder } from './services/orchestrator';

const result = await transferCrossBorder({
  userId: "user_123",
  amount: 100.0,
  srcCountryCode: "US",
  dstCountryCode: "MX",
  currency: "USDC",
  srcChain: 1,       // Ethereum Mainnet
  dstChain: 137,     // Polygon
  recipient: "0x1234...",  // Recipient's wallet address
  metadata: { reference: "test_transfer" }
});
``` 