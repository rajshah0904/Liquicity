from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .v1cnltermination_query_queried_merchant_principals_address import (
    V1cnlterminationQueryQueriedMerchantPrincipalsAddress,
)


@JsonMap({})
class V1cnlterminationQueryQueriedMerchantPrincipals(BaseModel):
    """Details of the registered principal owners of the merchant.<BR> Maximum - 3.

    :param first_name: The first name of the owner.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 1-35, defaults to None
    :type first_name: str, optional
    :param middle_initial: The initial letter of the owner's middle name.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: Maximum - 1, defaults to None
    :type middle_initial: str, optional
    :param last_name: The family name of the owner.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 1-40, defaults to None
    :type last_name: str, optional
    :param email: The primary email address of the merchant.\<BR\>String that starts with a combination of letters, numbers, ., _, %, or - before an **@** sign. After the **@** sign, a domain name with letters, numbers, ., or -, ending with a dot and a 2 to 4 letter domain type, such as **.com**. For example: **billsmith@snapphoto.com**\<BR\>Length: Maximum - 90, defaults to None
    :type email: str, optional
    :param phone_number: The phone number of the owner.\<BR\> Phone number in the format +[country code]/[phone number], where the forward slash (/) represents a separator between the country code and the telephone number.\<BR\>The plus sign before the country code is optional. The country code may only contain digits.\<BR\>The slash is required and must follow the country code.\<BR\>The telephone number may include blank spaces and hyphens (-).\<BR\>For example, in **+1/555 555-5555**, the country code is 1 and the telephone number is 5555555555.\<BR\>Length: 8-15, defaults to None
    :type phone_number: str, optional
    :param address: Details of the owner's business address., defaults to None
    :type address: V1cnlterminationQueryQueriedMerchantPrincipalsAddress, optional
    """

    def __init__(
        self,
        first_name: str = None,
        middle_initial: str = None,
        last_name: str = None,
        email: str = None,
        phone_number: str = None,
        address: V1cnlterminationQueryQueriedMerchantPrincipalsAddress = None,
    ):
        """Details of the registered principal owners of the merchant.<BR> Maximum - 3.

        :param first_name: The first name of the owner.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 1-35, defaults to None
        :type first_name: str, optional
        :param middle_initial: The initial letter of the owner's middle name.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: Maximum - 1, defaults to None
        :type middle_initial: str, optional
        :param last_name: The family name of the owner.\<BR\>String that starts and ends with any combination of characters, whitespace, a specified range of Latin letters with diacritics, and a specific set of special characters.\<BR\>Length: 1-40, defaults to None
        :type last_name: str, optional
        :param email: The primary email address of the merchant.\<BR\>String that starts with a combination of letters, numbers, ., _, %, or - before an **@** sign. After the **@** sign, a domain name with letters, numbers, ., or -, ending with a dot and a 2 to 4 letter domain type, such as **.com**. For example: **billsmith@snapphoto.com**\<BR\>Length: Maximum - 90, defaults to None
        :type email: str, optional
        :param phone_number: The phone number of the owner.\<BR\> Phone number in the format +[country code]/[phone number], where the forward slash (/) represents a separator between the country code and the telephone number.\<BR\>The plus sign before the country code is optional. The country code may only contain digits.\<BR\>The slash is required and must follow the country code.\<BR\>The telephone number may include blank spaces and hyphens (-).\<BR\>For example, in **+1/555 555-5555**, the country code is 1 and the telephone number is 5555555555.\<BR\>Length: 8-15, defaults to None
        :type phone_number: str, optional
        :param address: Details of the owner's business address., defaults to None
        :type address: V1cnlterminationQueryQueriedMerchantPrincipalsAddress, optional
        """
        self.first_name = self._define_str("first_name", first_name, nullable=True)
        self.middle_initial = self._define_str(
            "middle_initial", middle_initial, nullable=True
        )
        self.last_name = self._define_str("last_name", last_name, nullable=True)
        self.email = self._define_str("email", email, nullable=True)
        self.phone_number = self._define_str(
            "phone_number", phone_number, nullable=True
        )
        self.address = self._define_object(
            address, V1cnlterminationQueryQueriedMerchantPrincipalsAddress
        )
