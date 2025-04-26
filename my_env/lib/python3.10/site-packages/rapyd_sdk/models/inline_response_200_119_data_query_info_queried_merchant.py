from __future__ import annotations
from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .v1cnltermination_query_queried_merchant_principals_address import (
    V1cnlterminationQueryQueriedMerchantPrincipalsAddress,
)


class InlineResponse200_119DataQueryInfoQueriedMerchantBusinessCategory(Enum):
    """An enumeration representing different categories.

    :cvar MERCHANT: "Merchant"
    :vartype MERCHANT: str
    :cvar PAYMENTFACILITATOR: "Payment Facilitator"
    :vartype PAYMENTFACILITATOR: str
    :cvar INDEPENDENTSALESORGANIZATION: "Independent Sales Organization"
    :vartype INDEPENDENTSALESORGANIZATION: str
    :cvar MARKETPLACE: "Marketplace"
    :vartype MARKETPLACE: str
    :cvar STAGEDDIGITALWALLETOPERATOR: "Staged Digital Wallet Operator"
    :vartype STAGEDDIGITALWALLETOPERATOR: str
    :cvar SPONSOREDMERCHANT: "Sponsored Merchant"
    :vartype SPONSOREDMERCHANT: str
    """

    MERCHANT = "Merchant"
    PAYMENTFACILITATOR = "Payment Facilitator"
    INDEPENDENTSALESORGANIZATION = "Independent Sales Organization"
    MARKETPLACE = "Marketplace"
    STAGEDDIGITALWALLETOPERATOR = "Staged Digital Wallet Operator"
    SPONSOREDMERCHANT = "Sponsored Merchant"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                InlineResponse200_119DataQueryInfoQueriedMerchantBusinessCategory._member_map_.values(),
            )
        )


@JsonMap({})
class InlineResponse200_119DataQueryInfoQueriedMerchant(BaseModel):
    """Details of the merchant who is the subject of the query.

    :param business_category: The category of the merchant's business., defaults to None
    :type business_category: InlineResponse200_119DataQueryInfoQueriedMerchantBusinessCategory, optional
    :param dba_name: The "doing business as" name of the merchant.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 4-60, defaults to None
    :type dba_name: str, optional
    :param legal_name: The registered legal name of the merchant., defaults to None
    :type legal_name: str, optional
    :param address: Details of the owner's business address., defaults to None
    :type address: V1cnlterminationQueryQueriedMerchantPrincipalsAddress, optional
    :param phone_numbers: Business phone numbers of the merchant.\<BR\<Array of strings. Maximum - 2. Each string is a phone number in the format +[country code]/[phone number], where the forward slash (/) represents a separator between the country code and the telephone number.\<BR\>The plus sign before the country code is optional. The country code may only contain digits.\<BR\>The slash is required and must follow the country code.\<BR\>The telephone number may include blank spaces and hyphens (-).\<BR\>For example, in **+1/555 555-5555**, the country code is 1 and the telephone number is 5555555555.\<BR\>Length of each phone number: 8-15., defaults to None
    :type phone_numbers: dict, optional
    :param is_ecommerce: Indicates whether the merchant trades through the internet., defaults to None
    :type is_ecommerce: bool, optional
    """

    def __init__(
        self,
        business_category: InlineResponse200_119DataQueryInfoQueriedMerchantBusinessCategory = None,
        dba_name: str = None,
        legal_name: str = None,
        address: V1cnlterminationQueryQueriedMerchantPrincipalsAddress = None,
        phone_numbers: dict = None,
        is_ecommerce: bool = None,
    ):
        """Details of the merchant who is the subject of the query.

        :param business_category: The category of the merchant's business., defaults to None
        :type business_category: InlineResponse200_119DataQueryInfoQueriedMerchantBusinessCategory, optional
        :param dba_name: The "doing business as" name of the merchant.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 4-60, defaults to None
        :type dba_name: str, optional
        :param legal_name: The registered legal name of the merchant., defaults to None
        :type legal_name: str, optional
        :param address: Details of the owner's business address., defaults to None
        :type address: V1cnlterminationQueryQueriedMerchantPrincipalsAddress, optional
        :param phone_numbers: Business phone numbers of the merchant.\<BR\<Array of strings. Maximum - 2. Each string is a phone number in the format +[country code]/[phone number], where the forward slash (/) represents a separator between the country code and the telephone number.\<BR\>The plus sign before the country code is optional. The country code may only contain digits.\<BR\>The slash is required and must follow the country code.\<BR\>The telephone number may include blank spaces and hyphens (-).\<BR\>For example, in **+1/555 555-5555**, the country code is 1 and the telephone number is 5555555555.\<BR\>Length of each phone number: 8-15., defaults to None
        :type phone_numbers: dict, optional
        :param is_ecommerce: Indicates whether the merchant trades through the internet., defaults to None
        :type is_ecommerce: bool, optional
        """
        self.business_category = (
            self._enum_matching(
                business_category,
                InlineResponse200_119DataQueryInfoQueriedMerchantBusinessCategory.list(),
                "business_category",
            )
            if business_category
            else None
        )
        self.dba_name = self._define_str("dba_name", dba_name, nullable=True)
        self.legal_name = self._define_str("legal_name", legal_name, nullable=True)
        self.address = self._define_object(
            address, V1cnlterminationQueryQueriedMerchantPrincipalsAddress
        )
        self.phone_numbers = phone_numbers
        self.is_ecommerce = is_ecommerce
