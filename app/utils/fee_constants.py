"""
Fee structure constants for Liquicity application.

This file centralizes all fee-related constants to ensure consistency across the application.
"""

from decimal import Decimal

# Two-Tier Fee Structure

# Standard Tier (1-3 business days)
# Free deposit + 0.75% send; all-in ≤ Wise/Remitly fast rails
STANDARD_DEPOSIT_FEE_PCT = Decimal('0.0')  # No fee for standard deposits
STANDARD_SEND_FEE_PCT = Decimal('0.005')  # 0.5% for P2P wallet transfers

# Express Tier (Instant ≤ 15 min)
# Covers instant deposit (1.5076%) + balance-send (0.5%) rails
# Display as 1.5% in UI, but calculate with exact rate
INSTANT_DEPOSIT_FEE_PCT = Decimal('0.015076')  # 1.5076% for instant deposits
# All-in express fee is 2.0% (math: 1 - (1 - 0.015076) × (1 - 0.005) ≈ 0.02)

# P2P Wallet-Only (for users who have already deposited)
# Best-in-class pure P2P, 0.5% fee
P2P_WALLET_FEE_PCT = Decimal('0.005')  # 0.5% for wallet-to-wallet transfers

# Withdraw (no fee)
WITHDRAW_FEE_PCT = Decimal('0.0')  # Free withdrawal to bank

# Card Spend (no fee)
CARD_SPEND_FEE_PCT = Decimal('0.0')  # Free card spending

# Bank transfer fee (when using bank account directly for sending money)
BANK_TRANSFER_FEE_PCT = Decimal('0.029')  # 2.9% fee for bank-funded transfers

# For UI display (rounded to nearest tenth)
UI_INSTANT_DEPOSIT_FEE_PCT = '1.5%'  # Display as 1.5% in UI
UI_STANDARD_SEND_FEE_PCT = '0.5%'  # Display as 0.5% in UI
UI_BANK_TRANSFER_FEE_PCT = '2.9%'  # Display as 2.9% in UI 