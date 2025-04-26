from enum import Enum
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class AcceptSwift(Enum):
    """An enumeration representing different categories.

    :cvar TRUE: "true"
    :vartype TRUE: str
    :cvar FALSE: "false"
    :vartype FALSE: str
    """

    TRUE = "true"
    FALSE = "false"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, AcceptSwift._member_map_.values()))


class AccountIdType(Enum):
    """An enumeration representing different categories.

    :cvar IBANINTERNATIONALBANKACCOUNTNUMBERIBAN_: "iban - International bank account number (IBAN)."
    :vartype IBANINTERNATIONALBANKACCOUNTNUMBERIBAN_: str
    :cvar CLABECLABENUMBER_: "clabe - CLABE number."
    :vartype CLABECLABENUMBER_: str
    :cvar NULLREGULARBANKACCOUNTNUMBER_: "null - Regular bank account number."
    :vartype NULLREGULARBANKACCOUNTNUMBER_: str
    """

    IBANINTERNATIONALBANKACCOUNTNUMBERIBAN_ = (
        "iban - International bank account number (IBAN)."
    )
    CLABECLABENUMBER_ = "clabe - CLABE number."
    NULLREGULARBANKACCOUNTNUMBER_ = "null - Regular bank account number."

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, AccountIdType._member_map_.values()))


class LocalBankCodeType(Enum):
    """An enumeration representing different categories.

    :cvar BIC: "bic"
    :vartype BIC: str
    :cvar ABA: "aba"
    :vartype ABA: str
    :cvar SORTCODE: "sort_code"
    :vartype SORTCODE: str
    :cvar BSB: "bsb"
    :vartype BSB: str
    :cvar CNAPS: "cnaps"
    :vartype CNAPS: str
    :cvar IFSC: "ifsc"
    :vartype IFSC: str
    """

    BIC = "bic"
    ABA = "aba"
    SORTCODE = "sort_code"
    BSB = "bsb"
    CNAPS = "cnaps"
    IFSC = "ifsc"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, LocalBankCodeType._member_map_.values()))


class Refundable(Enum):
    """An enumeration representing different categories.

    :cvar TRUE: "true"
    :vartype TRUE: str
    :cvar FALSE: "false"
    :vartype FALSE: str
    """

    TRUE = "true"
    FALSE = "false"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, Refundable._member_map_.values()))


class RemitterDetails(Enum):
    """An enumeration representing different categories.

    :cvar TRUE: "true"
    :vartype TRUE: str
    :cvar FALSE: "false"
    :vartype FALSE: str
    """

    TRUE = "true"
    FALSE = "false"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, RemitterDetails._member_map_.values()))


@JsonMap({})
class InlineResponse200_95Data(BaseModel):
    """InlineResponse200_95Data

    :param accept_swift: Indicates whether the virtual account has a SWIFT code., defaults to None
    :type accept_swift: AcceptSwift, optional
    :param account_id_type: Type of the virtual account number., defaults to None
    :type account_id_type: AccountIdType, optional
    :param country: Two-letter ISO 3166-1 ALPHA-2 code for the country. code., defaults to None
    :type country: str, optional
    :param local_bank_code_type: Type of the local bank code., defaults to None
    :type local_bank_code_type: LocalBankCodeType, optional
    :param refundable: Indicates whether the virtual account has a SWIFT code., defaults to None
    :type refundable: Refundable, optional
    :param remitter_details: Indicates whether remitter details are available., defaults to None
    :type remitter_details: RemitterDetails, optional
    :param supported_currencies: Array of currencies supported for the virtual account. Array of strings., defaults to None
    :type supported_currencies: List[str], optional
    """

    def __init__(
        self,
        accept_swift: AcceptSwift = None,
        account_id_type: AccountIdType = None,
        country: str = None,
        local_bank_code_type: LocalBankCodeType = None,
        refundable: Refundable = None,
        remitter_details: RemitterDetails = None,
        supported_currencies: List[str] = None,
    ):
        """InlineResponse200_95Data

        :param accept_swift: Indicates whether the virtual account has a SWIFT code., defaults to None
        :type accept_swift: AcceptSwift, optional
        :param account_id_type: Type of the virtual account number., defaults to None
        :type account_id_type: AccountIdType, optional
        :param country: Two-letter ISO 3166-1 ALPHA-2 code for the country. code., defaults to None
        :type country: str, optional
        :param local_bank_code_type: Type of the local bank code., defaults to None
        :type local_bank_code_type: LocalBankCodeType, optional
        :param refundable: Indicates whether the virtual account has a SWIFT code., defaults to None
        :type refundable: Refundable, optional
        :param remitter_details: Indicates whether remitter details are available., defaults to None
        :type remitter_details: RemitterDetails, optional
        :param supported_currencies: Array of currencies supported for the virtual account. Array of strings., defaults to None
        :type supported_currencies: List[str], optional
        """
        self.accept_swift = (
            self._enum_matching(accept_swift, AcceptSwift.list(), "accept_swift")
            if accept_swift
            else None
        )
        self.account_id_type = (
            self._enum_matching(
                account_id_type, AccountIdType.list(), "account_id_type"
            )
            if account_id_type
            else None
        )
        self.country = self._define_str("country", country, nullable=True)
        self.local_bank_code_type = (
            self._enum_matching(
                local_bank_code_type, LocalBankCodeType.list(), "local_bank_code_type"
            )
            if local_bank_code_type
            else None
        )
        self.refundable = (
            self._enum_matching(refundable, Refundable.list(), "refundable")
            if refundable
            else None
        )
        self.remitter_details = (
            self._enum_matching(
                remitter_details, RemitterDetails.list(), "remitter_details"
            )
            if remitter_details
            else None
        )
        self.supported_currencies = supported_currencies
