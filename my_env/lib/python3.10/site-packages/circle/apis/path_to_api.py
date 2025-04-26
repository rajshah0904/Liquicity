import typing_extensions

from circle.paths import PathValues
from circle.apis.paths.ping import Ping
from circle.apis.paths.v1_configuration import V1Configuration
from circle.apis.paths.v1_encryption_public import V1EncryptionPublic
from circle.apis.paths.v1_notifications_subscriptions import V1NotificationsSubscriptions
from circle.apis.paths.v1_notifications_subscriptions_id import V1NotificationsSubscriptionsId
from circle.apis.paths.v1_channels import V1Channels
from circle.apis.paths.v1_stablecoins import V1Stablecoins
from circle.apis.paths.v1_business_account_balances import V1BusinessAccountBalances
from circle.apis.paths.v1_balances import V1Balances
from circle.apis.paths.v1_cards import V1Cards
from circle.apis.paths.v1_cards_id import V1CardsId
from circle.apis.paths.v1_payment_tokens import V1PaymentTokens
from circle.apis.paths.v1_business_account_banks_wires import V1BusinessAccountBanksWires
from circle.apis.paths.v1_business_account_banks_wires_id import V1BusinessAccountBanksWiresId
from circle.apis.paths.v1_business_account_banks_wires_id_instructions import V1BusinessAccountBanksWiresIdInstructions
from circle.apis.paths.v1_business_account_banks_cbit import V1BusinessAccountBanksCbit
from circle.apis.paths.v1_business_account_banks_cbit_id import V1BusinessAccountBanksCbitId
from circle.apis.paths.v1_business_account_banks_cbit_id_instructions import V1BusinessAccountBanksCbitIdInstructions
from circle.apis.paths.v1_business_account_wallets_addresses_deposit import V1BusinessAccountWalletsAddressesDeposit
from circle.apis.paths.v1_business_account_wallets_addresses_recipient import V1BusinessAccountWalletsAddressesRecipient
from circle.apis.paths.v1_business_account_wallets_addresses_recipient_id import V1BusinessAccountWalletsAddressesRecipientId
from circle.apis.paths.v1_business_account_deposits import V1BusinessAccountDeposits
from circle.apis.paths.v1_payment_intents import V1PaymentIntents
from circle.apis.paths.v1_payment_intents_id import V1PaymentIntentsId
from circle.apis.paths.v1_payment_intents_id_expire import V1PaymentIntentsIdExpire
from circle.apis.paths.v1_payment_intents_id_refund import V1PaymentIntentsIdRefund
from circle.apis.paths.v1_address_book_recipients import V1AddressBookRecipients
from circle.apis.paths.v1_address_book_recipients_id import V1AddressBookRecipientsId
from circle.apis.paths.v1_payments import V1Payments
from circle.apis.paths.v1_payments_crypto import V1PaymentsCrypto
from circle.apis.paths.v1_payments_id import V1PaymentsId
from circle.apis.paths.v1_payments_id_capture import V1PaymentsIdCapture
from circle.apis.paths.v1_payments_id_cancel import V1PaymentsIdCancel
from circle.apis.paths.v1_payments_id_refund import V1PaymentsIdRefund
from circle.apis.paths.v1_payments_presign import V1PaymentsPresign
from circle.apis.paths.v1_business_account_payouts import V1BusinessAccountPayouts
from circle.apis.paths.v1_business_account_payouts_id import V1BusinessAccountPayoutsId
from circle.apis.paths.v1_payouts import V1Payouts
from circle.apis.paths.v1_payouts_id import V1PayoutsId
from circle.apis.paths.v1_exchange_rates_trading_pair import V1ExchangeRatesTradingPair
from circle.apis.paths.v1_settlements import V1Settlements
from circle.apis.paths.v1_settlements_id import V1SettlementsId
from circle.apis.paths.v1_chargebacks import V1Chargebacks
from circle.apis.paths.v1_chargebacks_id import V1ChargebacksId
from circle.apis.paths.v1_wallets import V1Wallets
from circle.apis.paths.v1_wallets_wallet_id import V1WalletsWalletId
from circle.apis.paths.v1_wallets_wallet_id_addresses import V1WalletsWalletIdAddresses
from circle.apis.paths.v1_business_account_transfers import V1BusinessAccountTransfers
from circle.apis.paths.v1_business_account_transfers_id import V1BusinessAccountTransfersId
from circle.apis.paths.v1_transfers import V1Transfers
from circle.apis.paths.v1_transfers_id import V1TransfersId
from circle.apis.paths.v1_mocks_cards_chargebacks import V1MocksCardsChargebacks
from circle.apis.paths.v1_mocks_payments_wire import V1MocksPaymentsWire
from circle.apis.paths.v1_checkout_sessions import V1CheckoutSessions
from circle.apis.paths.v1_checkout_sessions_id import V1CheckoutSessionsId
from circle.apis.paths.v1_checkout_sessions_id_extend import V1CheckoutSessionsIdExtend

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.PING: Ping,
        PathValues.V1_CONFIGURATION: V1Configuration,
        PathValues.V1_ENCRYPTION_PUBLIC: V1EncryptionPublic,
        PathValues.V1_NOTIFICATIONS_SUBSCRIPTIONS: V1NotificationsSubscriptions,
        PathValues.V1_NOTIFICATIONS_SUBSCRIPTIONS_ID: V1NotificationsSubscriptionsId,
        PathValues.V1_CHANNELS: V1Channels,
        PathValues.V1_STABLECOINS: V1Stablecoins,
        PathValues.V1_BUSINESS_ACCOUNT_BALANCES: V1BusinessAccountBalances,
        PathValues.V1_BALANCES: V1Balances,
        PathValues.V1_CARDS: V1Cards,
        PathValues.V1_CARDS_ID: V1CardsId,
        PathValues.V1_PAYMENT_TOKENS: V1PaymentTokens,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_WIRES: V1BusinessAccountBanksWires,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_WIRES_ID: V1BusinessAccountBanksWiresId,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_WIRES_ID_INSTRUCTIONS: V1BusinessAccountBanksWiresIdInstructions,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_CBIT: V1BusinessAccountBanksCbit,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_CBIT_ID: V1BusinessAccountBanksCbitId,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_CBIT_ID_INSTRUCTIONS: V1BusinessAccountBanksCbitIdInstructions,
        PathValues.V1_BUSINESS_ACCOUNT_WALLETS_ADDRESSES_DEPOSIT: V1BusinessAccountWalletsAddressesDeposit,
        PathValues.V1_BUSINESS_ACCOUNT_WALLETS_ADDRESSES_RECIPIENT: V1BusinessAccountWalletsAddressesRecipient,
        PathValues.V1_BUSINESS_ACCOUNT_WALLETS_ADDRESSES_RECIPIENT_ID: V1BusinessAccountWalletsAddressesRecipientId,
        PathValues.V1_BUSINESS_ACCOUNT_DEPOSITS: V1BusinessAccountDeposits,
        PathValues.V1_PAYMENT_INTENTS: V1PaymentIntents,
        PathValues.V1_PAYMENT_INTENTS_ID: V1PaymentIntentsId,
        PathValues.V1_PAYMENT_INTENTS_ID_EXPIRE: V1PaymentIntentsIdExpire,
        PathValues.V1_PAYMENT_INTENTS_ID_REFUND: V1PaymentIntentsIdRefund,
        PathValues.V1_ADDRESS_BOOK_RECIPIENTS: V1AddressBookRecipients,
        PathValues.V1_ADDRESS_BOOK_RECIPIENTS_ID: V1AddressBookRecipientsId,
        PathValues.V1_PAYMENTS: V1Payments,
        PathValues.V1_PAYMENTS_CRYPTO: V1PaymentsCrypto,
        PathValues.V1_PAYMENTS_ID: V1PaymentsId,
        PathValues.V1_PAYMENTS_ID_CAPTURE: V1PaymentsIdCapture,
        PathValues.V1_PAYMENTS_ID_CANCEL: V1PaymentsIdCancel,
        PathValues.V1_PAYMENTS_ID_REFUND: V1PaymentsIdRefund,
        PathValues.V1_PAYMENTS_PRESIGN: V1PaymentsPresign,
        PathValues.V1_BUSINESS_ACCOUNT_PAYOUTS: V1BusinessAccountPayouts,
        PathValues.V1_BUSINESS_ACCOUNT_PAYOUTS_ID: V1BusinessAccountPayoutsId,
        PathValues.V1_PAYOUTS: V1Payouts,
        PathValues.V1_PAYOUTS_ID: V1PayoutsId,
        PathValues.V1_EXCHANGE_RATES_TRADINGPAIR: V1ExchangeRatesTradingPair,
        PathValues.V1_SETTLEMENTS: V1Settlements,
        PathValues.V1_SETTLEMENTS_ID: V1SettlementsId,
        PathValues.V1_CHARGEBACKS: V1Chargebacks,
        PathValues.V1_CHARGEBACKS_ID: V1ChargebacksId,
        PathValues.V1_WALLETS: V1Wallets,
        PathValues.V1_WALLETS_WALLET_ID: V1WalletsWalletId,
        PathValues.V1_WALLETS_WALLET_ID_ADDRESSES: V1WalletsWalletIdAddresses,
        PathValues.V1_BUSINESS_ACCOUNT_TRANSFERS: V1BusinessAccountTransfers,
        PathValues.V1_BUSINESS_ACCOUNT_TRANSFERS_ID: V1BusinessAccountTransfersId,
        PathValues.V1_TRANSFERS: V1Transfers,
        PathValues.V1_TRANSFERS_ID: V1TransfersId,
        PathValues.V1_MOCKS_CARDS_CHARGEBACKS: V1MocksCardsChargebacks,
        PathValues.V1_MOCKS_PAYMENTS_WIRE: V1MocksPaymentsWire,
        PathValues.V1_CHECKOUT_SESSIONS: V1CheckoutSessions,
        PathValues.V1_CHECKOUT_SESSIONS_ID: V1CheckoutSessionsId,
        PathValues.V1_CHECKOUT_SESSIONS_ID_EXTEND: V1CheckoutSessionsIdExtend,
    }
)

path_to_api = PathToApi(
    {
        PathValues.PING: Ping,
        PathValues.V1_CONFIGURATION: V1Configuration,
        PathValues.V1_ENCRYPTION_PUBLIC: V1EncryptionPublic,
        PathValues.V1_NOTIFICATIONS_SUBSCRIPTIONS: V1NotificationsSubscriptions,
        PathValues.V1_NOTIFICATIONS_SUBSCRIPTIONS_ID: V1NotificationsSubscriptionsId,
        PathValues.V1_CHANNELS: V1Channels,
        PathValues.V1_STABLECOINS: V1Stablecoins,
        PathValues.V1_BUSINESS_ACCOUNT_BALANCES: V1BusinessAccountBalances,
        PathValues.V1_BALANCES: V1Balances,
        PathValues.V1_CARDS: V1Cards,
        PathValues.V1_CARDS_ID: V1CardsId,
        PathValues.V1_PAYMENT_TOKENS: V1PaymentTokens,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_WIRES: V1BusinessAccountBanksWires,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_WIRES_ID: V1BusinessAccountBanksWiresId,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_WIRES_ID_INSTRUCTIONS: V1BusinessAccountBanksWiresIdInstructions,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_CBIT: V1BusinessAccountBanksCbit,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_CBIT_ID: V1BusinessAccountBanksCbitId,
        PathValues.V1_BUSINESS_ACCOUNT_BANKS_CBIT_ID_INSTRUCTIONS: V1BusinessAccountBanksCbitIdInstructions,
        PathValues.V1_BUSINESS_ACCOUNT_WALLETS_ADDRESSES_DEPOSIT: V1BusinessAccountWalletsAddressesDeposit,
        PathValues.V1_BUSINESS_ACCOUNT_WALLETS_ADDRESSES_RECIPIENT: V1BusinessAccountWalletsAddressesRecipient,
        PathValues.V1_BUSINESS_ACCOUNT_WALLETS_ADDRESSES_RECIPIENT_ID: V1BusinessAccountWalletsAddressesRecipientId,
        PathValues.V1_BUSINESS_ACCOUNT_DEPOSITS: V1BusinessAccountDeposits,
        PathValues.V1_PAYMENT_INTENTS: V1PaymentIntents,
        PathValues.V1_PAYMENT_INTENTS_ID: V1PaymentIntentsId,
        PathValues.V1_PAYMENT_INTENTS_ID_EXPIRE: V1PaymentIntentsIdExpire,
        PathValues.V1_PAYMENT_INTENTS_ID_REFUND: V1PaymentIntentsIdRefund,
        PathValues.V1_ADDRESS_BOOK_RECIPIENTS: V1AddressBookRecipients,
        PathValues.V1_ADDRESS_BOOK_RECIPIENTS_ID: V1AddressBookRecipientsId,
        PathValues.V1_PAYMENTS: V1Payments,
        PathValues.V1_PAYMENTS_CRYPTO: V1PaymentsCrypto,
        PathValues.V1_PAYMENTS_ID: V1PaymentsId,
        PathValues.V1_PAYMENTS_ID_CAPTURE: V1PaymentsIdCapture,
        PathValues.V1_PAYMENTS_ID_CANCEL: V1PaymentsIdCancel,
        PathValues.V1_PAYMENTS_ID_REFUND: V1PaymentsIdRefund,
        PathValues.V1_PAYMENTS_PRESIGN: V1PaymentsPresign,
        PathValues.V1_BUSINESS_ACCOUNT_PAYOUTS: V1BusinessAccountPayouts,
        PathValues.V1_BUSINESS_ACCOUNT_PAYOUTS_ID: V1BusinessAccountPayoutsId,
        PathValues.V1_PAYOUTS: V1Payouts,
        PathValues.V1_PAYOUTS_ID: V1PayoutsId,
        PathValues.V1_EXCHANGE_RATES_TRADINGPAIR: V1ExchangeRatesTradingPair,
        PathValues.V1_SETTLEMENTS: V1Settlements,
        PathValues.V1_SETTLEMENTS_ID: V1SettlementsId,
        PathValues.V1_CHARGEBACKS: V1Chargebacks,
        PathValues.V1_CHARGEBACKS_ID: V1ChargebacksId,
        PathValues.V1_WALLETS: V1Wallets,
        PathValues.V1_WALLETS_WALLET_ID: V1WalletsWalletId,
        PathValues.V1_WALLETS_WALLET_ID_ADDRESSES: V1WalletsWalletIdAddresses,
        PathValues.V1_BUSINESS_ACCOUNT_TRANSFERS: V1BusinessAccountTransfers,
        PathValues.V1_BUSINESS_ACCOUNT_TRANSFERS_ID: V1BusinessAccountTransfersId,
        PathValues.V1_TRANSFERS: V1Transfers,
        PathValues.V1_TRANSFERS_ID: V1TransfersId,
        PathValues.V1_MOCKS_CARDS_CHARGEBACKS: V1MocksCardsChargebacks,
        PathValues.V1_MOCKS_PAYMENTS_WIRE: V1MocksPaymentsWire,
        PathValues.V1_CHECKOUT_SESSIONS: V1CheckoutSessions,
        PathValues.V1_CHECKOUT_SESSIONS_ID: V1CheckoutSessionsId,
        PathValues.V1_CHECKOUT_SESSIONS_ID_EXTEND: V1CheckoutSessionsIdExtend,
    }
)
