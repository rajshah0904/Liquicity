from __future__ import annotations
from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .simulate_card_transaction_authorization_request_eea_auth_response import (
    SimulateCardTransactionAuthorizationRequestEeaAuthResponse,
)
from .simulate_clearing_card_transaction_eea_remote_auth_response import (
    SimulateClearingCardTransactionEeaRemoteAuthResponse,
)


class SimulateCardTransactionAuthorizationReversalEeaTxnType(Enum):
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
        return list(
            map(
                lambda x: x.value,
                SimulateCardTransactionAuthorizationReversalEeaTxnType._member_map_.values(),
            )
        )


@JsonMap({"id_": "id"})
class SimulateCardTransactionAuthorizationReversalEea(BaseModel):
    """SimulateCardTransactionAuthorizationReversalEea

    :param amount: Amount of the refund, in units defined in `currency`., defaults to None
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
    :param is_remote_auth: Indicates whether remote authorization is enabled., defaults to None
    :type is_remote_auth: bool, optional
    :param merchant_category_code: Four-digit merchant category code (MCC) of the initiator of the transaction, as defined in ISO 18245., defaults to None
    :type merchant_category_code: str, optional
    :param merchant_identification_code: Reserved., defaults to None
    :type merchant_identification_code: str, optional
    :param merchant_name_location: Name and location of the merchant. Maximum 40 characters., defaults to None
    :type merchant_name_location: str, optional
    :param remote_auth_endpoint: The URL where the remote authorization is sent., defaults to None
    :type remote_auth_endpoint: str, optional
    :param remote_auth_response: Response to a successful remote authorization request. Contains the following fields:, defaults to None
    :type remote_auth_response: SimulateClearingCardTransactionEeaRemoteAuthResponse, optional
    :param transaction_amount: Amount debited from the Rapyd Wallet. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015., defaults to None
    :type transaction_amount: float, optional
    :param txn_type: Type of transaction., defaults to None
    :type txn_type: SimulateCardTransactionAuthorizationReversalEeaTxnType, optional
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
        is_remote_auth: bool = None,
        merchant_category_code: str = None,
        merchant_identification_code: str = None,
        merchant_name_location: str = None,
        remote_auth_endpoint: str = None,
        remote_auth_response: SimulateClearingCardTransactionEeaRemoteAuthResponse = None,
        transaction_amount: float = None,
        txn_type: SimulateCardTransactionAuthorizationReversalEeaTxnType = None,
    ):
        """SimulateCardTransactionAuthorizationReversalEea

        :param amount: Amount of the refund, in units defined in `currency`., defaults to None
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
        :param is_remote_auth: Indicates whether remote authorization is enabled., defaults to None
        :type is_remote_auth: bool, optional
        :param merchant_category_code: Four-digit merchant category code (MCC) of the initiator of the transaction, as defined in ISO 18245., defaults to None
        :type merchant_category_code: str, optional
        :param merchant_identification_code: Reserved., defaults to None
        :type merchant_identification_code: str, optional
        :param merchant_name_location: Name and location of the merchant. Maximum 40 characters., defaults to None
        :type merchant_name_location: str, optional
        :param remote_auth_endpoint: The URL where the remote authorization is sent., defaults to None
        :type remote_auth_endpoint: str, optional
        :param remote_auth_response: Response to a successful remote authorization request. Contains the following fields:, defaults to None
        :type remote_auth_response: SimulateClearingCardTransactionEeaRemoteAuthResponse, optional
        :param transaction_amount: Amount debited from the Rapyd Wallet. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015., defaults to None
        :type transaction_amount: float, optional
        :param txn_type: Type of transaction., defaults to None
        :type txn_type: SimulateCardTransactionAuthorizationReversalEeaTxnType, optional
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
        self.is_remote_auth = is_remote_auth
        self.merchant_category_code = self._define_str(
            "merchant_category_code", merchant_category_code, nullable=True
        )
        self.merchant_identification_code = self._define_str(
            "merchant_identification_code", merchant_identification_code, nullable=True
        )
        self.merchant_name_location = self._define_str(
            "merchant_name_location", merchant_name_location, nullable=True
        )
        self.remote_auth_endpoint = self._define_str(
            "remote_auth_endpoint", remote_auth_endpoint, nullable=True
        )
        self.remote_auth_response = self._define_object(
            remote_auth_response, SimulateClearingCardTransactionEeaRemoteAuthResponse
        )
        self.transaction_amount = self._define_number(
            "transaction_amount", transaction_amount, nullable=True
        )
        self.txn_type = (
            self._enum_matching(
                txn_type,
                SimulateCardTransactionAuthorizationReversalEeaTxnType.list(),
                "txn_type",
            )
            if txn_type
            else None
        )
