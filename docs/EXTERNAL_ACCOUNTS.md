# External Accounts and Deposits

This document explains the integration with Bridge API for external accounts and deposits in the Liquicity application.

## Overview

The system allows users to:
1. Link external bank accounts (either manually or via Plaid)
2. Deposit funds to their Bridge wallet using these accounts
3. Choose between standard deposits (slower but lower fees) and instant deposits (immediate credit)

## Components

### 1. External Accounts

External accounts represent a user's bank accounts that can be used to deposit funds. They can be created in two ways, with the system automatically routing users based on their region:

#### US Users: Plaid Integration
- Users in the United States are automatically directed to Plaid integration
- Plaid provides a secure way to link bank accounts without manually entering account details
- The system exchanges a Plaid public token for access to the user's account details

#### EU Users: Manual Entry
- Users in the European Union are automatically directed to manual entry
- They must provide their IBAN and bank details manually
- The system verifies these details with Bridge API

### 2. Deposits

Users can deposit funds from their linked external accounts to their Bridge wallet using two methods:

#### Standard Deposits
- Funds are transferred directly from the user's external account to their Bridge wallet
- Processing typically takes 1-3 business days
- No fee is charged for this service
- Uses ACH for US users and SEPA for EU users

#### Instant Deposits
- Funds are made available immediately in the user's Bridge wallet
- A small fee (typically 1.5%) is charged for this service
- The deposit is backed by Liquicity's custodial wallet until the actual bank transfer completes

## Bridge API Integration

The system integrates with Bridge API to handle all banking operations. The Bridge API provides endpoints for:

- Managing customer profiles
- Creating and managing external accounts
- Processing transfers between accounts
- Creating and managing Bridge wallets
- Integration with Plaid for US users

### Bridge API Reference

The system includes a comprehensive Bridge API reference file (`app/services/bridge_api_reference.py`) that organizes all Bridge API endpoints in a structured, easy-to-use format. This reference includes:

- Complete categorization of all Bridge API endpoints
- Proper URL formatting with parameters
- Documentation on endpoint purposes
- Method signatures that follow Bridge API conventions

The Bridge client (`app/services/bridge.py`) uses this reference to ensure consistency across all API calls.

## Database Structure

The system uses the following database tables:

1. `bridge_wallets` - Stores information about the user's Bridge wallet
2. `external_accounts` - Stores information about linked bank accounts
3. `virtual_accounts` - Stores information about virtual accounts/IBANs
4. `deposits` - Tracks deposit transactions

## Frontend Components

The frontend includes components for:

1. Linking bank accounts (with automatic routing based on region)
2. Managing linked accounts
3. Making deposits with flexible options

## API Endpoints

The backend exposes the following API endpoints for external account and deposit management:

### External Accounts
- `/external_accounts/region` - Get region information to determine account creation flow
- `/external_accounts/accounts` - Create and list external accounts
- `/external_accounts/accounts/{id}` - Get, update, or delete a specific external account
- `/external_accounts/plaid/link_token` - Get a Plaid link token (US only)
- `/external_accounts/plaid/exchange/{request_id}` - Exchange a Plaid public token (US only)

### Deposits
- `/deposits` - Create and list deposits
- `/deposits/{id}` - Get a specific deposit

## Data Flow

### Account Creation Flow
1. When a user selects "Add Bank Account," the system checks their region
2. US users are directed to Plaid Link
3. EU users are directed to the manual entry form with appropriate fields (IBAN instead of account/routing numbers)
4. After account creation, the system stores the account details and associates them with the user

### Standard Deposit Flow
1. User selects an external account and Bridge wallet
2. User enters amount and chooses "standard" deposit
3. System creates a direct transfer from external account to Bridge wallet
4. Transfer status is tracked and updated until completion

### Instant Deposit Flow
1. User selects an external account and Bridge wallet
2. User enters amount and chooses "instant" deposit
3. System creates two transfers:
   - From external account to Liquicity's custodial wallet (will clear in 1-3 days)
   - From Liquicity's custodial wallet to user's Bridge wallet (immediate)
4. User's wallet balance is updated immediately

## Setup Instructions

1. Ensure your environment has the `