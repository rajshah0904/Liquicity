from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class RequestedCurrency(Enum):
    """An enumeration representing different categories.

    :cvar AUD: "AUD"
    :vartype AUD: str
    :cvar EUR: "EUR"
    :vartype EUR: str
    :cvar GBP: "GBP"
    :vartype GBP: str
    :cvar HKD: "HKD"
    :vartype HKD: str
    :cvar SGD: "SGD"
    :vartype SGD: str
    :cvar USD: "USD"
    :vartype USD: str
    """

    AUD = "AUD"
    EUR = "EUR"
    GBP = "GBP"
    HKD = "HKD"
    SGD = "SGD"
    USD = "USD"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, RequestedCurrency._member_map_.values()))


class InlineResponse200_103DataBankAccountsStatus(Enum):
    """An enumeration representing different categories.

    :cvar ACT: "ACT"
    :vartype ACT: str
    :cvar CLO: "CLO"
    :vartype CLO: str
    :cvar ERR: "ERR"
    :vartype ERR: str
    :cvar REJ: "REJ"
    :vartype REJ: str
    """

    ACT = "ACT"
    CLO = "CLO"
    ERR = "ERR"
    REJ = "REJ"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                InlineResponse200_103DataBankAccountsStatus._member_map_.values(),
            )
        )


@JsonMap({})
class InlineResponse200_103DataBankAccounts(BaseModel):
    """Array of objects with details of the virtual accounts. Each object contains the following fields

    :param account_id: The actual account number that was assigned to the virtual account when it was created., defaults to None
    :type account_id: str, optional
    :param account_id_type: Type of the virtual account number, such as IBAN or CLABE., defaults to None
    :type account_id_type: str, optional
    :param country_iso: Two-letter ISO 3166-1 ALPHA-2 code of the country of the virtual account., defaults to None
    :type country_iso: str, optional
    :param currency: Currency of the virtual account. Three-letter ISO 4217 code., defaults to None
    :type currency: str, optional
    :param ewallet: ID of the Rapyd Wallet that the virtual accounts were issued to. String starting with **ewallet_**., defaults to None
    :type ewallet: str, optional
    :param issuing_id: ID of the virtual account number object. String starting with **issuing_**., defaults to None
    :type issuing_id: str, optional
    :param requested_currency: Currency received by the virtual account after conversion.\<BR\>When not specified, the funds appear in the wallet’s currency account for the currency of the transaction., defaults to None
    :type requested_currency: RequestedCurrency, optional
    :param status: Indicates the status of the virtual account., defaults to None
    :type status: InlineResponse200_103DataBankAccountsStatus, optional
    """

    def __init__(
        self,
        account_id: str = None,
        account_id_type: str = None,
        country_iso: str = None,
        currency: str = None,
        ewallet: str = None,
        issuing_id: str = None,
        requested_currency: RequestedCurrency = None,
        status: InlineResponse200_103DataBankAccountsStatus = None,
    ):
        """Array of objects with details of the virtual accounts. Each object contains the following fields

        :param account_id: The actual account number that was assigned to the virtual account when it was created., defaults to None
        :type account_id: str, optional
        :param account_id_type: Type of the virtual account number, such as IBAN or CLABE., defaults to None
        :type account_id_type: str, optional
        :param country_iso: Two-letter ISO 3166-1 ALPHA-2 code of the country of the virtual account., defaults to None
        :type country_iso: str, optional
        :param currency: Currency of the virtual account. Three-letter ISO 4217 code., defaults to None
        :type currency: str, optional
        :param ewallet: ID of the Rapyd Wallet that the virtual accounts were issued to. String starting with **ewallet_**., defaults to None
        :type ewallet: str, optional
        :param issuing_id: ID of the virtual account number object. String starting with **issuing_**., defaults to None
        :type issuing_id: str, optional
        :param requested_currency: Currency received by the virtual account after conversion.\<BR\>When not specified, the funds appear in the wallet’s currency account for the currency of the transaction., defaults to None
        :type requested_currency: RequestedCurrency, optional
        :param status: Indicates the status of the virtual account., defaults to None
        :type status: InlineResponse200_103DataBankAccountsStatus, optional
        """
        self.account_id = self._define_str("account_id", account_id, nullable=True)
        self.account_id_type = self._define_str(
            "account_id_type", account_id_type, nullable=True
        )
        self.country_iso = self._define_str("country_iso", country_iso, nullable=True)
        self.currency = self._define_str("currency", currency, nullable=True)
        self.ewallet = self._define_str("ewallet", ewallet, nullable=True)
        self.issuing_id = self._define_str("issuing_id", issuing_id, nullable=True)
        self.requested_currency = (
            self._enum_matching(
                requested_currency, RequestedCurrency.list(), "requested_currency"
            )
            if requested_currency
            else None
        )
        self.status = (
            self._enum_matching(
                status, InlineResponse200_103DataBankAccountsStatus.list(), "status"
            )
            if status
            else None
        )
