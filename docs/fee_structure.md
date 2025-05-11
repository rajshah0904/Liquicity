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

### Other Operations
- **Wallet-to-Wallet Transfer**: 0.50% fee
- **Withdrawals**: 0% (FREE)
- **Card Spending**: 0% (FREE)

## Implementation Details

The actual fee calculations use precise values:
- Instant Deposit Fee: 1.5076% (displayed as 1.5% in UI)
- P2P Send Fee: 0.5%
- Bank Transfer Fee: 2.9%

The all-in Express fee equals: 1 - (1 - 0.015076) × (1 - 0.005) = 2.00%

## API and Code Constants

Fee constants are maintained in two central locations:
- Backend: `app/utils/fee_constants.py`
- Frontend: `frontend/src/utils/feeConstants.js`

These values should be kept in sync to ensure consistent fee calculations across the application. 