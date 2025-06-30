# Bridge Payment System Integration

This document explains the integration of the Bridge API for payment processing in the Liquicity application.

## Overview

The payment system uses Bridge API to:
1. Create Bridge wallets for users
2. Set up virtual accounts (US) or virtual IBANs (EU) based on user region
3. Process deposits and display balances in the Liquicity wallet

## Components

### 1. Bridge Customer

When a user completes KYC successfully, they are automatically registered as a Bridge customer. This is a prerequisite for all other Bridge services.

### 2. Bridge Wallet

Each user is issued at least one Bridge wallet on their preferred blockchain network (default: Solana). The wallet is used to:
- Receive funds from virtual accounts
- Send funds to external accounts
- Track user crypto balances

### 3. Virtual Accounts

Based on a user's region (determined by their country):
- **US users**: Receive a virtual US bank account with routing and account numbers
- **EU users**: Receive a virtual IBAN

These accounts allow users to deposit fiat currency (USD or EUR) which is automatically converted to USDB (a stablecoin) in their Bridge wallet.

## Data Flow

1. User is created in Liquicity
2. User completes KYC
3. Bridge customer is created
4. Bridge wallet is created (Solana network by default)
5. Virtual account is created based on user's region
6. User deposits funds to their virtual account
7. Funds are converted to USDB and appear in Bridge wallet
8. Liquicity wallet displays the combined balance

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bridge/customers` | GET | Get or create Bridge customer |
| `/api/bridge/wallets` | GET | List user's Bridge wallets |
| `/api/bridge/wallets` | POST | Create a new Bridge wallet |
| `/api/bridge/virtual_accounts` | GET | List user's virtual accounts |
| `/api/bridge/virtual_accounts` | POST | Create a new virtual account |
| `/api/bridge/virtual_accounts/{id}` | GET | Get virtual account details |
| `/api/wallet/overview` | GET | Get wallet overview with balances |

## Testing

To test the integration, you can run:
```
python -m app.scripts.test_bridge_integration
```

This will create a test customer, wallet, and virtual accounts to verify the API connections.

## Database Schema

The integration adds two new tables to the database:

### bridge_wallets
- `id`: Primary key
- `user_id`: Foreign key to users
- `bridge_wallet_id`: Bridge wallet identifier
- `chain`: Blockchain network (e.g., "solana")
- `address`: Wallet address
- `balance`: Current balance
- `currency`: Currency (usually "usdb")
- `last_sync`: Last sync timestamp
- `created_at`: Creation timestamp

### virtual_accounts
- `id`: Primary key
- `user_id`: Foreign key to users
- `bridge_wallet_id`: Foreign key to bridge_wallets
- `virtual_account_id`: Bridge virtual account identifier
- `account_type`: "us_account" or "eu_iban"
- `currency`: Source currency (e.g., "usd", "eur")
- `destination_currency`: Destination currency (e.g., "usdb")
- `payment_rail`: Blockchain network (e.g., "solana")
- `account_details`: JSON with account details
- `balance`: Current balance
- `developer_fee_percent`: Developer fee percentage
- `last_sync`: Last sync timestamp
- `created_at`: Creation timestamp

## Setup Instructions

1. Ensure your environment has the `BRIDGE_API_KEY` variable set
2. Run the database migration: `python -m app.scripts.add_bridge_tables`
3. Restart the application server

## Security Considerations

- Bridge API keys must be kept secure and never exposed to clients
- Always verify user ownership of wallets and accounts
- Use idempotency keys for all POST requests to prevent duplicate operations 