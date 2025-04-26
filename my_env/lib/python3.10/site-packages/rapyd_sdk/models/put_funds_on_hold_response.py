from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class PutFundsOnHoldResponseDestinationBalanceType(Enum):
    """An enumeration representing different categories.

    :cvar AVAILABLEBALANCE: "available_balance"
    :vartype AVAILABLEBALANCE: str
    :cvar ONHOLDBALANCE: "on_hold_balance"
    :vartype ONHOLDBALANCE: str
    :cvar RECEIVEDBALANCE: "received_balance"
    :vartype RECEIVEDBALANCE: str
    :cvar RESERVEBALANCE: "reserve_balance"
    :vartype RESERVEBALANCE: str
    """

    AVAILABLEBALANCE = "available_balance"
    ONHOLDBALANCE = "on_hold_balance"
    RECEIVEDBALANCE = "received_balance"
    RESERVEBALANCE = "reserve_balance"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                PutFundsOnHoldResponseDestinationBalanceType._member_map_.values(),
            )
        )


class PutFundsOnHoldResponseSourceBalanceType(Enum):
    """An enumeration representing different categories.

    :cvar AVAILABLEBALANCE: "available_balance"
    :vartype AVAILABLEBALANCE: str
    :cvar ONHOLDBALANCE: "on_hold_balance"
    :vartype ONHOLDBALANCE: str
    :cvar RECEIVEDBALANCE: "received_balance"
    :vartype RECEIVEDBALANCE: str
    :cvar RESERVEBALANCE: "reserve_balance"
    :vartype RESERVEBALANCE: str
    """

    AVAILABLEBALANCE = "available_balance"
    ONHOLDBALANCE = "on_hold_balance"
    RECEIVEDBALANCE = "received_balance"
    RESERVEBALANCE = "reserve_balance"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                PutFundsOnHoldResponseSourceBalanceType._member_map_.values(),
            )
        )


@JsonMap({"id_": "id"})
class PutFundsOnHoldResponse(BaseModel):
    """PutFundsOnHoldResponse

    :param amount:  * **Transactions** - Amount of the transaction, in units of the currency defined in `currency`. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 4217:2015.\<BR\> * **Wallet Account Operations** - Amount of the account limit., defaults to None
    :type amount: float, optional
    :param currency_code: Three-letter ISO 4217 code for the currency used in the `amount` field., defaults to None
    :type currency_code: str, optional
    :param destination_account_id: ID of the wallet owner's user. UUID., defaults to None
    :type destination_account_id: str, optional
    :param destination_balance_type: Balance type that the funds are transferred to. See 'Wallet Balance Types'., defaults to None
    :type destination_balance_type: PutFundsOnHoldResponseDestinationBalanceType, optional
    :param destination_transaction_id: ID of the transaction with regard to the destination. String starting with **wt_**., defaults to None
    :type destination_transaction_id: str, optional
    :param destination_user_profile_id: ID of the wallet owner's user. UUID., defaults to None
    :type destination_user_profile_id: str, optional
    :param id_: ID of the transaction. UUID., defaults to None
    :type id_: str, optional
    :param source_balance_type: Balance type that the funds are transferred from. See 'Wallet Balance Types'. See 'Wallet Balance Types'., defaults to None
    :type source_balance_type: PutFundsOnHoldResponseSourceBalanceType, optional
    :param source_transaction_id: ID of the transaction with regard to the source. String starting with **wt_**., defaults to None
    :type source_transaction_id: dict, optional
    :param source_user_profile_id: ID of the wallet owner's user. UUID., defaults to None
    :type source_user_profile_id: str, optional
    """

    def __init__(
        self,
        amount: float = None,
        currency_code: str = None,
        destination_account_id: str = None,
        destination_balance_type: PutFundsOnHoldResponseDestinationBalanceType = None,
        destination_transaction_id: str = None,
        destination_user_profile_id: str = None,
        id_: str = None,
        source_balance_type: PutFundsOnHoldResponseSourceBalanceType = None,
        source_transaction_id: dict = None,
        source_user_profile_id: str = None,
    ):
        """PutFundsOnHoldResponse

        :param amount:  * **Transactions** - Amount of the transaction, in units of the currency defined in `currency`. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 4217:2015.\<BR\> * **Wallet Account Operations** - Amount of the account limit., defaults to None
        :type amount: float, optional
        :param currency_code: Three-letter ISO 4217 code for the currency used in the `amount` field., defaults to None
        :type currency_code: str, optional
        :param destination_account_id: ID of the wallet owner's user. UUID., defaults to None
        :type destination_account_id: str, optional
        :param destination_balance_type: Balance type that the funds are transferred to. See 'Wallet Balance Types'., defaults to None
        :type destination_balance_type: PutFundsOnHoldResponseDestinationBalanceType, optional
        :param destination_transaction_id: ID of the transaction with regard to the destination. String starting with **wt_**., defaults to None
        :type destination_transaction_id: str, optional
        :param destination_user_profile_id: ID of the wallet owner's user. UUID., defaults to None
        :type destination_user_profile_id: str, optional
        :param id_: ID of the transaction. UUID., defaults to None
        :type id_: str, optional
        :param source_balance_type: Balance type that the funds are transferred from. See 'Wallet Balance Types'. See 'Wallet Balance Types'., defaults to None
        :type source_balance_type: PutFundsOnHoldResponseSourceBalanceType, optional
        :param source_transaction_id: ID of the transaction with regard to the source. String starting with **wt_**., defaults to None
        :type source_transaction_id: dict, optional
        :param source_user_profile_id: ID of the wallet owner's user. UUID., defaults to None
        :type source_user_profile_id: str, optional
        """
        self.amount = self._define_number("amount", amount, nullable=True)
        self.currency_code = self._define_str(
            "currency_code", currency_code, nullable=True
        )
        self.destination_account_id = self._define_str(
            "destination_account_id", destination_account_id, nullable=True
        )
        self.destination_balance_type = (
            self._enum_matching(
                destination_balance_type,
                PutFundsOnHoldResponseDestinationBalanceType.list(),
                "destination_balance_type",
            )
            if destination_balance_type
            else None
        )
        self.destination_transaction_id = self._define_str(
            "destination_transaction_id", destination_transaction_id, nullable=True
        )
        self.destination_user_profile_id = self._define_str(
            "destination_user_profile_id", destination_user_profile_id, nullable=True
        )
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.source_balance_type = (
            self._enum_matching(
                source_balance_type,
                PutFundsOnHoldResponseSourceBalanceType.list(),
                "source_balance_type",
            )
            if source_balance_type
            else None
        )
        self.source_transaction_id = source_transaction_id
        self.source_user_profile_id = self._define_str(
            "source_user_profile_id", source_user_profile_id, nullable=True
        )
