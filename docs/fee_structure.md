# Liquicity Fee Structure

## Overview

Liquicity offers a straightforward, competitive two-tier fee structure designed to be transparent and economical for users.

### Two-Tier Structure

| Tier | Timing | Fee (all-in) | Notes |
|------|--------|--------------|-------|
| Standard | 1–3 business days | 0.50% | Free deposit + 0.50% send; all-in ≤ Wise/Remitly fast rails |
| Express | Instant (≤ 15 min) | 2.00% | Covers instant deposit (1.5076%) + balance-send (0.50%) rails |
| P2P Wallet-Only | Instant | 0.50% | Best-in-class pure P2P (after you've deposited) |
| Withdraw | 1–3 business days | 0% | Free burn → bank rails |
| Card Spend | Instant | 0% | Matches industry free-spend cards |

## Breaking Down the Fees

### Standard Option (0.50% all-in)
- **Deposit**: 0% (FREE)
- **Send**: 0.50%
- **Time**: Funds are available in 1-3 business days

This option provides the most economical way to send money, undercutting major remitters' fastest 1-3 day options. Standard cross-border at 0.75% all-in undercuts every major remitter's fastest 1–3 day cost (Wise ≈ 0.6%, Remitly ≈ 0.5% but slower).

### Express Option (2.00% all-in)
- **Deposit**: 1.5076% (displayed as 1.5% in UI)
- **Send**: 0.50%
- **Time**: Funds available instantly (≤15 minutes)

This option provides true instant processing at competitive rates compared to PayPal's 1.5–2.9% card rails.

### Handling Partial Transactions

When a user initiates a transfer but has insufficient wallet balance:

#### Standard Tier Partial Transactions
- **Wallet portion**: Available balance is sent instantly with 0.50% fee
- **Bank portion**: Remaining amount is processed with standard deposit (0% fee) plus 0.50% send fee
- **Timing**: Wallet portion arrives instantly, bank portion in 1-3 business days
- **Total fee**: Still 0.50% all-in

#### Express Tier Partial Transactions
- All funds are sent instantly regardless of wallet balance
- The wallet portion is transferred immediately with a 2.00% fee
- The bank portion is advanced from treasury with a 2.00% fee
- **Timing**: All funds arrive instantly (≤15 minutes)
- **Total fee**: 2.00% all-in

### Other Operations
- **Wallet-to-Wallet Transfer**: 0.50% fee
- **Withdrawals**: 0% (FREE)
- **Card Spending**: 0% (FREE)

## Mathematical Verification

The actual fee calculations use precise values:

### Standard Tier (0.50% all-in)
Standard = Slow Deposit + P2P Send
1 - (1 - 0) × (1 - 0.005) = 0.005 = 0.50%

### Express Tier (2.00% all-in)
Express = Instant Deposit + P2P Send
1 - (1 - 0.015076) × (1 - 0.005) = 1 - 0.984924 × 0.995 ≈ 1 - 0.98 = 0.02 = 2.00%

For UI display, we round 1.5076% to 1.5% to keep things readable, but calculations use the exact rates with fees always rounded up to the nearest cent.

## API and Code Constants

Fee constants are maintained in two central locations:
- Backend: `app/utils/fee_constants.py`
- Frontend: `frontend/src/utils/feeConstants.js`

These values should be kept in sync to ensure consistent fee calculations across the application. 