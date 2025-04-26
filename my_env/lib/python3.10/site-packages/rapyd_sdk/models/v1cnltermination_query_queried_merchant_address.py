from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class V1cnlterminationQueryQueriedMerchantAddress(BaseModel):
    """Details of the merchant's business address.

    :param address_line_1: Line 1 of the address, such as a building number and street name.\<BR\>String with letters, numbers, numeric letters, and spaces. Applicable street details in this order: building number/name, street number and name, shop number, floor number.\<BR\>Length: 1-60
    :type address_line_1: str
    :param address_line_2: Line 2 of the address, such as a building number and street name.\<BR\>String with letters, numbers, numeric letters, and spaces.\<BR\>Length: 1-60
    :type address_line_2: str
    :param city: City portion of the address.\<BR\>String with letters, numbers, and spaces.\<BR\>Length: 1-20
    :type city: str
    :param country: Code for the country.\<BR\>The two-letter ISO 3166-1 ALPHA-2 country code.\<BR\>Length: 2
    :type country: str
    :param postal_code: Postal code portion of the address.\<BR\>String with letters, numbers, and spaces.\<BR\>Length: 1-10, defaults to None
    :type postal_code: str, optional
    """

    def __init__(
        self,
        address_line_1: str,
        address_line_2: str,
        city: str,
        country: str,
        postal_code: str = None,
    ):
        """Details of the merchant's business address.

        :param address_line_1: Line 1 of the address, such as a building number and street name.\<BR\>String with letters, numbers, numeric letters, and spaces. Applicable street details in this order: building number/name, street number and name, shop number, floor number.\<BR\>Length: 1-60
        :type address_line_1: str
        :param address_line_2: Line 2 of the address, such as a building number and street name.\<BR\>String with letters, numbers, numeric letters, and spaces.\<BR\>Length: 1-60
        :type address_line_2: str
        :param city: City portion of the address.\<BR\>String with letters, numbers, and spaces.\<BR\>Length: 1-20
        :type city: str
        :param country: Code for the country.\<BR\>The two-letter ISO 3166-1 ALPHA-2 country code.\<BR\>Length: 2
        :type country: str
        :param postal_code: Postal code portion of the address.\<BR\>String with letters, numbers, and spaces.\<BR\>Length: 1-10, defaults to None
        :type postal_code: str, optional
        """
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.city = city
        self.country = country
        self.postal_code = self._define_str("postal_code", postal_code, nullable=True)
