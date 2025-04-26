from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class IssuingActivateCardBody(BaseModel):
    """IssuingActivateCardBody

    :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type cancel_url: str, optional
    :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type complete_url: str, optional
    :param ewallet_contact: ID of the wallet contact that the card is assigned to. Must have a valid phone number. String starting with **cont_**.
    :type ewallet_contact: str
    :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'.\<BR\>* When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param personalize: When **true**, connects an issued card to a wallet contact. Relevant to a card that was issued in bulk and is not assigned to a specific person., defaults to None
    :type personalize: bool, optional
    :param skip_pin: When **true**, the customer cannot reset the PIN., defaults to None
    :type skip_pin: bool, optional
    """

    def __init__(
        self,
        ewallet_contact: str,
        cancel_url: str = None,
        complete_url: str = None,
        language: str = None,
        page_expiration: float = None,
        personalize: bool = None,
        skip_pin: bool = None,
    ):
        """IssuingActivateCardBody

        :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type cancel_url: str, optional
        :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type complete_url: str, optional
        :param ewallet_contact: ID of the wallet contact that the card is assigned to. Must have a valid phone number. String starting with **cont_**.
        :type ewallet_contact: str
        :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'.\<BR\>* When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param personalize: When **true**, connects an issued card to a wallet contact. Relevant to a card that was issued in bulk and is not assigned to a specific person., defaults to None
        :type personalize: bool, optional
        :param skip_pin: When **true**, the customer cannot reset the PIN., defaults to None
        :type skip_pin: bool, optional
        """
        self.cancel_url = self._define_str("cancel_url", cancel_url, nullable=True)
        self.complete_url = self._define_str(
            "complete_url", complete_url, nullable=True
        )
        self.ewallet_contact = ewallet_contact
        self.language = self._define_str("language", language, nullable=True)
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.personalize = personalize
        self.skip_pin = skip_pin
