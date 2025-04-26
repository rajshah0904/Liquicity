# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from circle.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    ADDRESSES = "Addresses"
    CRYPTO_ADDRESS_BOOK = "Crypto Address Book"
    BALANCES = "Balances"
    CARDS = "Cards"
    PAYMENT_TOKENS = "Payment Tokens"
    CHANNELS = "Channels"
    CHARGEBACKS = "Chargebacks"
    CRYPTO_PAYMENT_INTENTS = "Crypto Payment Intents"
    DEPOSITS = "Deposits"
    ENCRYPTION = "Encryption"
    CRYPTO_EXCHANGE_RATES = "Crypto Exchange Rates"
    HEALTH = "Health"
    MANAGEMENT = "Management"
    PAYMENTS = "Payments"
    PULL_CRYPTO_PAYMENTS = "Pull Crypto Payments"
    PAYOUTS = "Payouts"
    SETTLEMENTS = "Settlements"
    CBIT = "CBIT"
    STABLECOINS = "Stablecoins"
    SUBSCRIPTIONS = "Subscriptions"
    TRANSFERS = "Transfers"
    WALLETS = "Wallets"
    WIRES = "Wires"
    CHECKOUT_SESSIONS = "Checkout Sessions"
