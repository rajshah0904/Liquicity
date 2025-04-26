from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap(
    {
        "first_part_address": "firstPartAddress",
        "second_part_address": "secondPartAddress",
        "country_code": "countryCode",
    }
)
class AddCardtoGooglePayResponseUserAddress(BaseModel):
    """The base64 encoded string that contains the encrypted object for Push Provisioning. Required for adding the card to the Google Pay wallet by using the Google Pay `pushTokenizeRequest` method. For more information refer to the Google Pay Provisioning developer documentation .Details of an account funding transaction (AFT), which transfers funds from a card to a cardholder's wallet.

    :param first_part_address: First part address., defaults to None
    :type first_part_address: str, optional
    :param second_part_address: Second part address., defaults to None
    :type second_part_address: str, optional
    :param country_code: Two character Country code., defaults to None
    :type country_code: str, optional
    :param locality: Locality such as city, town, etc., defaults to None
    :type locality: str, optional
    """

    def __init__(
        self,
        first_part_address: str = None,
        second_part_address: str = None,
        country_code: str = None,
        locality: str = None,
    ):
        """The base64 encoded string that contains the encrypted object for Push Provisioning. Required for adding the card to the Google Pay wallet by using the Google Pay `pushTokenizeRequest` method. For more information refer to the Google Pay Provisioning developer documentation .Details of an account funding transaction (AFT), which transfers funds from a card to a cardholder's wallet.

        :param first_part_address: First part address., defaults to None
        :type first_part_address: str, optional
        :param second_part_address: Second part address., defaults to None
        :type second_part_address: str, optional
        :param country_code: Two character Country code., defaults to None
        :type country_code: str, optional
        :param locality: Locality such as city, town, etc., defaults to None
        :type locality: str, optional
        """
        self.first_part_address = self._define_str(
            "first_part_address", first_part_address, nullable=True
        )
        self.second_part_address = self._define_str(
            "second_part_address", second_part_address, nullable=True
        )
        self.country_code = self._define_str(
            "country_code", country_code, nullable=True
        )
        self.locality = self._define_str("locality", locality, nullable=True)
