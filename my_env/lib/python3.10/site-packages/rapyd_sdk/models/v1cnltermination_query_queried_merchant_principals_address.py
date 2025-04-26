from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class V1cnlterminationQueryQueriedMerchantPrincipalsAddress(BaseModel):
    """Details of the owner's business address.

    :param address_line_1: Line 1 of the address, such as a building number and street name.\<BR\>String with letters, numbers, numeric letters, and spaces. Applicable street details in this order: building number/name, street number and name, shop number, floor number.\<BR\>Length: 1-60, defaults to None
    :type address_line_1: str, optional
    :param address_line_2: Line 2 of the address, such as a building number and street name.\<BR\>String with letters, numbers, numeric letters, and spaces.\<BR\>Length: 1-60, defaults to None
    :type address_line_2: str, optional
    :param city: City portion of the address.\<BR\>String with letters, numbers, and spaces.\<BR\>Length: 1-20, defaults to None
    :type city: str, optional
    :param country: Code for the country.\<BR\>The two-letter ISO 3166-1 ALPHA-2 country code.\<BR\>Length: 2, defaults to None
    :type country: str, optional
    :param postal_code: Postal code portion of the address.\<BR\>String with letters, numbers, and spaces.\<BR\>Length: 1-10, defaults to None
    :type postal_code: str, optional
    """

    def __init__(
        self,
        address_line_1: str = None,
        address_line_2: str = None,
        city: str = None,
        country: str = None,
        postal_code: str = None,
    ):
        """Details of the owner's business address.

        :param address_line_1: Line 1 of the address, such as a building number and street name.\<BR\>String with letters, numbers, numeric letters, and spaces. Applicable street details in this order: building number/name, street number and name, shop number, floor number.\<BR\>Length: 1-60, defaults to None
        :type address_line_1: str, optional
        :param address_line_2: Line 2 of the address, such as a building number and street name.\<BR\>String with letters, numbers, numeric letters, and spaces.\<BR\>Length: 1-60, defaults to None
        :type address_line_2: str, optional
        :param city: City portion of the address.\<BR\>String with letters, numbers, and spaces.\<BR\>Length: 1-20, defaults to None
        :type city: str, optional
        :param country: Code for the country.\<BR\>The two-letter ISO 3166-1 ALPHA-2 country code.\<BR\>Length: 2, defaults to None
        :type country: str, optional
        :param postal_code: Postal code portion of the address.\<BR\>String with letters, numbers, and spaces.\<BR\>Length: 1-10, defaults to None
        :type postal_code: str, optional
        """
        self.address_line_1 = self._define_str(
            "address_line_1", address_line_1, nullable=True
        )
        self.address_line_2 = self._define_str(
            "address_line_2", address_line_2, nullable=True
        )
        self.city = self._define_str("city", city, nullable=True)
        self.country = self._define_str("country", country, nullable=True)
        self.postal_code = self._define_str("postal_code", postal_code, nullable=True)
