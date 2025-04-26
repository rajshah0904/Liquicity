from __future__ import annotations
from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .simulate_card_transaction_authorization_request_eea_auth_response import (
    SimulateCardTransactionAuthorizationRequestEeaAuthResponse,
)


class IssuingTxnType(Enum):
    """An enumeration representing different categories.

    :cvar ADJUSTMENT: "ADJUSTMENT"
    :vartype ADJUSTMENT: str
    :cvar ATMFEE: "ATM_FEE"
    :vartype ATMFEE: str
    :cvar CREDIT: "CREDIT"
    :vartype CREDIT: str
    :cvar REFUND: "REFUND"
    :vartype REFUND: str
    :cvar REVERSAL: "REVERSAL"
    :vartype REVERSAL: str
    :cvar SALE: "SALE"
    :vartype SALE: str
    """

    ADJUSTMENT = "ADJUSTMENT"
    ATMFEE = "ATM_FEE"
    CREDIT = "CREDIT"
    REFUND = "REFUND"
    REVERSAL = "REVERSAL"
    SALE = "SALE"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, IssuingTxnType._member_map_.values()))


class SimulateCardTransactionAuthorizationRequestEeaPosEntryMode(Enum):
    """An enumeration representing different categories.

    :cvar ADJUSTMENT: "adjustment"
    :vartype ADJUSTMENT: str
    :cvar ECOMMERCE: "ecommerce"
    :vartype ECOMMERCE: str
    :cvar EMV: "emv"
    :vartype EMV: str
    :cvar EMVSTANDIN: "emv_standin"
    :vartype EMVSTANDIN: str
    :cvar MAGSTRIPE: "magstripe"
    :vartype MAGSTRIPE: str
    :cvar MANUALENTERED: "manual_entered"
    :vartype MANUALENTERED: str
    :cvar NETWORKTOKEN: "network_token"
    :vartype NETWORKTOKEN: str
    :cvar NFC: "nfc"
    :vartype NFC: str
    :cvar _3DSECOMMERCE: "3ds_ecommerce"
    :vartype _3DSECOMMERCE: str
    """

    ADJUSTMENT = "adjustment"
    ECOMMERCE = "ecommerce"
    EMV = "emv"
    EMVSTANDIN = "emv_standin"
    MAGSTRIPE = "magstripe"
    MANUALENTERED = "manual_entered"
    NETWORKTOKEN = "network_token"
    NFC = "nfc"
    _3DSECOMMERCE = "3ds_ecommerce"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                SimulateCardTransactionAuthorizationRequestEeaPosEntryMode._member_map_.values(),
            )
        )


@JsonMap({"id_": "id"})
class SimulateCardTransactionAuthorizationRequestEea(BaseModel):
    """SimulateCardTransactionAuthorizationRequestEea

    :param amount: Amount of the transaction, in units defined in `currency`., defaults to None
    :type amount: float, optional
    :param auth_response: Response related to an authorization. Contains the following fields:, defaults to None
    :type auth_response: SimulateCardTransactionAuthorizationRequestEeaAuthResponse, optional
    :param card_id: ID of the card. String starting with **card_**., defaults to None
    :type card_id: str, optional
    :param card_transaction_id: ID of the transaction. String starting with **cit_**., defaults to None
    :type card_transaction_id: str, optional
    :param currency_code: Currency of the transaction. Three-letter ISO 4217 code.Currency of the refund transaction. Three-letter ISO 4217 code., defaults to None
    :type currency_code: str, optional
    :param fx_rate: The exchange rate. Relevant to capture (clearing) transactions., defaults to None
    :type fx_rate: str, optional
    :param id_: ID of the issued card transaction. String starting with **cit_**., defaults to None
    :type id_: str, optional
    :param issuing_txn_type: Type of transaction on the issued card., defaults to None
    :type issuing_txn_type: IssuingTxnType, optional
    :param last4: Last 4 digits of the card number., defaults to None
    :type last4: str, optional
    :param merchant_category_code: Four-digit merchant category code (MCC) of the initiator of the transaction, as defined in ISO 18245., defaults to None
    :type merchant_category_code: str, optional
    :param merchant_name_location: Name and location of the merchant., defaults to None
    :type merchant_name_location: str, optional
    :param original_transaction_id: ID of the original issued card transaction. String starting with **cit_**., defaults to None
    :type original_transaction_id: str, optional
    :param original_txn_amount: Original amount for FX transactions, when `currency` is different from `original_txn_currency`., defaults to None
    :type original_txn_amount: float, optional
    :param original_txn_currency: Original currency in an FX transaction., defaults to None
    :type original_txn_currency: str, optional
    :param pos_entry_mode: The mode of entry of the transaction at the point of sale., defaults to None
    :type pos_entry_mode: SimulateCardTransactionAuthorizationRequestEeaPosEntryMode, optional
    :param retrieval_reference_number: Retrieval reference number for the card transaction., defaults to None
    :type retrieval_reference_number: str, optional
    :param systems_trace_audit_number: Reserved., defaults to None
    :type systems_trace_audit_number: str, optional
    :param wallet_transaction_id: ID of the wallet transaction String starting with **wt_**., defaults to None
    :type wallet_transaction_id: str, optional
    """

    def __init__(
        self,
        amount: float = None,
        auth_response: SimulateCardTransactionAuthorizationRequestEeaAuthResponse = None,
        card_id: str = None,
        card_transaction_id: str = None,
        currency_code: str = None,
        fx_rate: str = None,
        id_: str = None,
        issuing_txn_type: IssuingTxnType = None,
        last4: str = None,
        merchant_category_code: str = None,
        merchant_name_location: str = None,
        original_transaction_id: str = None,
        original_txn_amount: float = None,
        original_txn_currency: str = None,
        pos_entry_mode: SimulateCardTransactionAuthorizationRequestEeaPosEntryMode = None,
        retrieval_reference_number: str = None,
        systems_trace_audit_number: str = None,
        wallet_transaction_id: str = None,
    ):
        """SimulateCardTransactionAuthorizationRequestEea

        :param amount: Amount of the transaction, in units defined in `currency`., defaults to None
        :type amount: float, optional
        :param auth_response: Response related to an authorization. Contains the following fields:, defaults to None
        :type auth_response: SimulateCardTransactionAuthorizationRequestEeaAuthResponse, optional
        :param card_id: ID of the card. String starting with **card_**., defaults to None
        :type card_id: str, optional
        :param card_transaction_id: ID of the transaction. String starting with **cit_**., defaults to None
        :type card_transaction_id: str, optional
        :param currency_code: Currency of the transaction. Three-letter ISO 4217 code.Currency of the refund transaction. Three-letter ISO 4217 code., defaults to None
        :type currency_code: str, optional
        :param fx_rate: The exchange rate. Relevant to capture (clearing) transactions., defaults to None
        :type fx_rate: str, optional
        :param id_: ID of the issued card transaction. String starting with **cit_**., defaults to None
        :type id_: str, optional
        :param issuing_txn_type: Type of transaction on the issued card., defaults to None
        :type issuing_txn_type: IssuingTxnType, optional
        :param last4: Last 4 digits of the card number., defaults to None
        :type last4: str, optional
        :param merchant_category_code: Four-digit merchant category code (MCC) of the initiator of the transaction, as defined in ISO 18245., defaults to None
        :type merchant_category_code: str, optional
        :param merchant_name_location: Name and location of the merchant., defaults to None
        :type merchant_name_location: str, optional
        :param original_transaction_id: ID of the original issued card transaction. String starting with **cit_**., defaults to None
        :type original_transaction_id: str, optional
        :param original_txn_amount: Original amount for FX transactions, when `currency` is different from `original_txn_currency`., defaults to None
        :type original_txn_amount: float, optional
        :param original_txn_currency: Original currency in an FX transaction., defaults to None
        :type original_txn_currency: str, optional
        :param pos_entry_mode: The mode of entry of the transaction at the point of sale., defaults to None
        :type pos_entry_mode: SimulateCardTransactionAuthorizationRequestEeaPosEntryMode, optional
        :param retrieval_reference_number: Retrieval reference number for the card transaction., defaults to None
        :type retrieval_reference_number: str, optional
        :param systems_trace_audit_number: Reserved., defaults to None
        :type systems_trace_audit_number: str, optional
        :param wallet_transaction_id: ID of the wallet transaction String starting with **wt_**., defaults to None
        :type wallet_transaction_id: str, optional
        """
        self.amount = self._define_number("amount", amount, nullable=True)
        self.auth_response = self._define_object(
            auth_response, SimulateCardTransactionAuthorizationRequestEeaAuthResponse
        )
        self.card_id = self._define_str("card_id", card_id, nullable=True)
        self.card_transaction_id = self._define_str(
            "card_transaction_id", card_transaction_id, nullable=True
        )
        self.currency_code = self._define_str(
            "currency_code", currency_code, nullable=True
        )
        self.fx_rate = self._define_str("fx_rate", fx_rate, nullable=True)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.issuing_txn_type = (
            self._enum_matching(
                issuing_txn_type, IssuingTxnType.list(), "issuing_txn_type"
            )
            if issuing_txn_type
            else None
        )
        self.last4 = self._define_str("last4", last4, nullable=True)
        self.merchant_category_code = self._define_str(
            "merchant_category_code", merchant_category_code, nullable=True
        )
        self.merchant_name_location = self._define_str(
            "merchant_name_location", merchant_name_location, nullable=True
        )
        self.original_transaction_id = self._define_str(
            "original_transaction_id", original_transaction_id, nullable=True
        )
        self.original_txn_amount = self._define_number(
            "original_txn_amount", original_txn_amount, nullable=True
        )
        self.original_txn_currency = self._define_str(
            "original_txn_currency", original_txn_currency, nullable=True
        )
        self.pos_entry_mode = (
            self._enum_matching(
                pos_entry_mode,
                SimulateCardTransactionAuthorizationRequestEeaPosEntryMode.list(),
                "pos_entry_mode",
            )
            if pos_entry_mode
            else None
        )
        self.retrieval_reference_number = self._define_str(
            "retrieval_reference_number", retrieval_reference_number, nullable=True
        )
        self.systems_trace_audit_number = self._define_str(
            "systems_trace_audit_number", systems_trace_audit_number, nullable=True
        )
        self.wallet_transaction_id = self._define_str(
            "wallet_transaction_id", wallet_transaction_id, nullable=True
        )
