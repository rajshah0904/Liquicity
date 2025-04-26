from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class IssuingPinBody(BaseModel):
    """IssuingPinBody

    :param cancel_url: URL where the customer is redirected after pressing **Back to Website**., defaults to None
    :type cancel_url: str, optional
    :param card: ID of the card. String starting with **card_**., defaults to None
    :type card: str, optional
    :param ewallet_contact: ID of the wallet contact that the card is assigned to. Must have a valid phone number. String starting with **cont_**.
    :type ewallet_contact: str
    :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'.\<BR\>* When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 7 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
    :type page_expiration: any, optional
    :param skip_pin: When **true**, the customer cannot reset the PIN., defaults to None
    :type skip_pin: bool, optional
    """

    def __init__(
        self,
        ewallet_contact: str,
        cancel_url: str = None,
        card: str = None,
        language: str = None,
        page_expiration: any = None,
        skip_pin: bool = None,
    ):
        """IssuingPinBody

        :param cancel_url: URL where the customer is redirected after pressing **Back to Website**., defaults to None
        :type cancel_url: str, optional
        :param card: ID of the card. String starting with **card_**., defaults to None
        :type card: str, optional
        :param ewallet_contact: ID of the wallet contact that the card is assigned to. Must have a valid phone number. String starting with **cont_**.
        :type ewallet_contact: str
        :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'.\<BR\>* When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 7 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
        :type page_expiration: any, optional
        :param skip_pin: When **true**, the customer cannot reset the PIN., defaults to None
        :type skip_pin: bool, optional
        """
        self.cancel_url = self._define_str("cancel_url", cancel_url, nullable=True)
        self.card = self._define_str("card", card, nullable=True)
        self.ewallet_contact = ewallet_contact
        self.language = self._define_str("language", language, nullable=True)
        self.page_expiration = page_expiration
        self.skip_pin = skip_pin
