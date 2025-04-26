from __future__ import annotations
from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .v1cnltermination_query_queried_merchant_address import (
    V1cnlterminationQueryQueriedMerchantAddress,
)
from .v1cnltermination_query_queried_merchant_principals import (
    V1cnlterminationQueryQueriedMerchantPrincipals,
)


class V1cnlterminationQueryQueriedMerchantBusinessCategory(Enum):
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
                V1cnlterminationQueryQueriedMerchantBusinessCategory._member_map_.values(),
            )
        )


@JsonMap({})
class V1cnlterminationQueryQueriedMerchant(BaseModel):
    """Information about the merchant who is the subject of the query.

    :param address: Details of the merchant's business address., defaults to None
    :type address: V1cnlterminationQueryQueriedMerchantAddress, optional
    :param phone_numbers: Business phone numbers of the merchant.\<BR\<Array of strings. Maximum - 2. Each string is a phone number in the format +[country code]/[phone number], where the forward slash (/) represents a separator between the country code and the telephone number.\<BR\>The plus sign before the country code is optional. The country code may only contain digits.\<BR\>The slash is required and must follow the country code.\<BR\>The telephone number may include blank spaces and hyphens (-).\<BR\>For example, in **+1/555 555-5555**, the country code is 1 and the telephone number is 5555555555.\<BR\>Length of each phone number: 8-15., defaults to None
    :type phone_numbers: dict, optional
    :param business_category: The category of the merchant's business., defaults to None
    :type business_category: V1cnlterminationQueryQueriedMerchantBusinessCategory, optional
    :param dba_name: The "doing business as" name of the merchant.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 4-60, defaults to None
    :type dba_name: str, optional
    :param mcc: Merchant category codes of the merchant's business.\<BR\>Array of strings. Numbers or US letters. Maximum - 5 items. \<BR\>Length of each string: 4., defaults to None
    :type mcc: dict, optional
    :param principals: Details of the registered principal owners of the merchant.\<BR\> Maximum - 3., defaults to None
    :type principals: V1cnlterminationQueryQueriedMerchantPrincipals, optional
    :param is_ecommerce: Indicates whether the merchant trades through the internet., defaults to None
    :type is_ecommerce: bool, optional
    :param legal_name: The family name of the owner.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 1-40, defaults to None
    :type legal_name: str, optional
    :param url: Web addresses associated with the merchant.\<BR\>Array of strings. Numbers or US letters. Maximum - 3 items. For example: ["https://fourstarmarket.com", "https://fourstarmarket.net"]\<BR\>Length: Maximum - 40, defaults to None
    :type url: dict, optional
    :param email: The primary email address of the owner.\<BR\>String that starts with a combination of letters, numbers, ., _, %, or - before an **@** sign. After the **@** sign, a domain name with letters, numbers, ., or -, ending with a dot and a 2 to 4 letter domain type, such as **.com**. For example: **davidsmith@snapphoto.com**\<BR\>Length: Maximum - 90, defaults to None
    :type email: str, optional
    """

    def __init__(
        self,
        address: V1cnlterminationQueryQueriedMerchantAddress = None,
        phone_numbers: dict = None,
        business_category: V1cnlterminationQueryQueriedMerchantBusinessCategory = None,
        dba_name: str = None,
        mcc: dict = None,
        principals: V1cnlterminationQueryQueriedMerchantPrincipals = None,
        is_ecommerce: bool = None,
        legal_name: str = None,
        url: dict = None,
        email: str = None,
    ):
        """Information about the merchant who is the subject of the query.

        :param address: Details of the merchant's business address., defaults to None
        :type address: V1cnlterminationQueryQueriedMerchantAddress, optional
        :param phone_numbers: Business phone numbers of the merchant.\<BR\<Array of strings. Maximum - 2. Each string is a phone number in the format +[country code]/[phone number], where the forward slash (/) represents a separator between the country code and the telephone number.\<BR\>The plus sign before the country code is optional. The country code may only contain digits.\<BR\>The slash is required and must follow the country code.\<BR\>The telephone number may include blank spaces and hyphens (-).\<BR\>For example, in **+1/555 555-5555**, the country code is 1 and the telephone number is 5555555555.\<BR\>Length of each phone number: 8-15., defaults to None
        :type phone_numbers: dict, optional
        :param business_category: The category of the merchant's business., defaults to None
        :type business_category: V1cnlterminationQueryQueriedMerchantBusinessCategory, optional
        :param dba_name: The "doing business as" name of the merchant.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 4-60, defaults to None
        :type dba_name: str, optional
        :param mcc: Merchant category codes of the merchant's business.\<BR\>Array of strings. Numbers or US letters. Maximum - 5 items. \<BR\>Length of each string: 4., defaults to None
        :type mcc: dict, optional
        :param principals: Details of the registered principal owners of the merchant.\<BR\> Maximum - 3., defaults to None
        :type principals: V1cnlterminationQueryQueriedMerchantPrincipals, optional
        :param is_ecommerce: Indicates whether the merchant trades through the internet., defaults to None
        :type is_ecommerce: bool, optional
        :param legal_name: The family name of the owner.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 1-40, defaults to None
        :type legal_name: str, optional
        :param url: Web addresses associated with the merchant.\<BR\>Array of strings. Numbers or US letters. Maximum - 3 items. For example: ["https://fourstarmarket.com", "https://fourstarmarket.net"]\<BR\>Length: Maximum - 40, defaults to None
        :type url: dict, optional
        :param email: The primary email address of the owner.\<BR\>String that starts with a combination of letters, numbers, ., _, %, or - before an **@** sign. After the **@** sign, a domain name with letters, numbers, ., or -, ending with a dot and a 2 to 4 letter domain type, such as **.com**. For example: **davidsmith@snapphoto.com**\<BR\>Length: Maximum - 90, defaults to None
        :type email: str, optional
        """
        self.address = self._define_object(
            address, V1cnlterminationQueryQueriedMerchantAddress
        )
        self.phone_numbers = phone_numbers
        self.business_category = (
            self._enum_matching(
                business_category,
                V1cnlterminationQueryQueriedMerchantBusinessCategory.list(),
                "business_category",
            )
            if business_category
            else None
        )
        self.dba_name = self._define_str("dba_name", dba_name, nullable=True)
        self.mcc = mcc
        self.principals = self._define_object(
            principals, V1cnlterminationQueryQueriedMerchantPrincipals
        )
        self.is_ecommerce = is_ecommerce
        self.legal_name = self._define_str("legal_name", legal_name, nullable=True)
        self.url = url
        self.email = self._define_str("email", email, nullable=True)
