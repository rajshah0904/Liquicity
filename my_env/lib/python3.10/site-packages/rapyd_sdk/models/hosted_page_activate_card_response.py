from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .merchant_customer_support import MerchantCustomerSupport
from .hosted_page_status import HostedPageStatus


@JsonMap({"id_": "id"})
class HostedPageActivateCardResponse(BaseModel):
    """HostedPageActivateCardResponse

    :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type cancel_url: str, optional
    :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type complete_url: str, optional
    :param ewallet_contact: ID of the wallet contact that the card is assigned to. Must have a valid phone number. String starting with **cont_**., defaults to None
    :type ewallet_contact: str, optional
    :param geo_country: Reserved., defaults to None
    :type geo_country: str, optional
    :param id_: ID of the hosted page for activating a card, a string starting with **hp_issuing_act_**., defaults to None
    :type id_: str, optional
    :param language: Determines the default language of the hosted page.\<BR\>* When this parameter is null, the language of the user's browser is used.\<BR\>* If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param merchant_alias: Client's name., defaults to None
    :type merchant_alias: str, optional
    :param merchant_color: Color of the call-to-action (CTA) button on the hosted page. To configure this field, use the Client Portal., defaults to None
    :type merchant_color: str, optional
    :param merchant_customer_support: Contains details of the client’s customer support. To configure these fields, use the Client Portal., defaults to None
    :type merchant_customer_support: MerchantCustomerSupport, optional
    :param merchant_logo: URL for the image of the client's logo. To configure this field, use the Client Portal., defaults to None
    :type merchant_logo: str, optional
    :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers.\<BR\>To configure this field, use the Client Portal., defaults to None
    :type merchant_privacy_policy: str, optional
    :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Porta, defaults to None
    :type merchant_terms: str, optional
    :param merchant_website: The URL where the customer is redirected after exiting the hosted page. Relevant when `cancel_url`, `complete_url` or both fields are not set. To configure this field, use the Client Portal., defaults to None
    :type merchant_website: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param personalize: When **true**, connects an issued card to a wallet contact. Relevant to a card that was issued in bulk and is not assigned to a specific person. Transparent to the customer. See also 'Personalize Bulk-Issued Card' in online documentation., defaults to None
    :type personalize: float, optional
    :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
    :type redirect_url: str, optional
    :param region: Reserved., defaults to None
    :type region: str, optional
    :param skip_pin: When **true**, the customer cannot reset the PIN via a hosted page., defaults to None
    :type skip_pin: bool, optional
    :param status: Status of the hosted page. One of the following: NEW - The hosted page was created. DON - Done. The card was added to the customer profile. EXP - The hosted page expired. , defaults to None
    :type status: HostedPageStatus, optional
    """

    def __init__(
        self,
        cancel_url: str = None,
        complete_url: str = None,
        ewallet_contact: str = None,
        geo_country: str = None,
        id_: str = None,
        language: str = None,
        merchant_alias: str = None,
        merchant_color: str = None,
        merchant_customer_support: MerchantCustomerSupport = None,
        merchant_logo: str = None,
        merchant_privacy_policy: str = None,
        merchant_terms: str = None,
        merchant_website: str = None,
        page_expiration: float = None,
        personalize: float = None,
        redirect_url: str = None,
        region: str = None,
        skip_pin: bool = None,
        status: HostedPageStatus = None,
    ):
        """HostedPageActivateCardResponse

        :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type cancel_url: str, optional
        :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type complete_url: str, optional
        :param ewallet_contact: ID of the wallet contact that the card is assigned to. Must have a valid phone number. String starting with **cont_**., defaults to None
        :type ewallet_contact: str, optional
        :param geo_country: Reserved., defaults to None
        :type geo_country: str, optional
        :param id_: ID of the hosted page for activating a card, a string starting with **hp_issuing_act_**., defaults to None
        :type id_: str, optional
        :param language: Determines the default language of the hosted page.\<BR\>* When this parameter is null, the language of the user's browser is used.\<BR\>* If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param merchant_alias: Client's name., defaults to None
        :type merchant_alias: str, optional
        :param merchant_color: Color of the call-to-action (CTA) button on the hosted page. To configure this field, use the Client Portal., defaults to None
        :type merchant_color: str, optional
        :param merchant_customer_support: Contains details of the client’s customer support. To configure these fields, use the Client Portal., defaults to None
        :type merchant_customer_support: MerchantCustomerSupport, optional
        :param merchant_logo: URL for the image of the client's logo. To configure this field, use the Client Portal., defaults to None
        :type merchant_logo: str, optional
        :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers.\<BR\>To configure this field, use the Client Portal., defaults to None
        :type merchant_privacy_policy: str, optional
        :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Porta, defaults to None
        :type merchant_terms: str, optional
        :param merchant_website: The URL where the customer is redirected after exiting the hosted page. Relevant when `cancel_url`, `complete_url` or both fields are not set. To configure this field, use the Client Portal., defaults to None
        :type merchant_website: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param personalize: When **true**, connects an issued card to a wallet contact. Relevant to a card that was issued in bulk and is not assigned to a specific person. Transparent to the customer. See also 'Personalize Bulk-Issued Card' in online documentation., defaults to None
        :type personalize: float, optional
        :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
        :type redirect_url: str, optional
        :param region: Reserved., defaults to None
        :type region: str, optional
        :param skip_pin: When **true**, the customer cannot reset the PIN via a hosted page., defaults to None
        :type skip_pin: bool, optional
        :param status: Status of the hosted page. One of the following: NEW - The hosted page was created. DON - Done. The card was added to the customer profile. EXP - The hosted page expired. , defaults to None
        :type status: HostedPageStatus, optional
        """
        self.cancel_url = self._define_str("cancel_url", cancel_url, nullable=True)
        self.complete_url = self._define_str(
            "complete_url", complete_url, nullable=True
        )
        self.ewallet_contact = self._define_str(
            "ewallet_contact", ewallet_contact, nullable=True
        )
        self.geo_country = self._define_str("geo_country", geo_country, nullable=True)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.language = self._define_str("language", language, nullable=True)
        self.merchant_alias = self._define_str(
            "merchant_alias", merchant_alias, nullable=True
        )
        self.merchant_color = self._define_str(
            "merchant_color", merchant_color, nullable=True
        )
        self.merchant_customer_support = self._define_object(
            merchant_customer_support, MerchantCustomerSupport
        )
        self.merchant_logo = self._define_str(
            "merchant_logo", merchant_logo, nullable=True
        )
        self.merchant_privacy_policy = self._define_str(
            "merchant_privacy_policy", merchant_privacy_policy, nullable=True
        )
        self.merchant_terms = self._define_str(
            "merchant_terms", merchant_terms, nullable=True
        )
        self.merchant_website = self._define_str(
            "merchant_website", merchant_website, nullable=True
        )
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.personalize = self._define_number(
            "personalize", personalize, nullable=True
        )
        self.redirect_url = self._define_str(
            "redirect_url", redirect_url, nullable=True
        )
        self.region = self._define_str("region", region, nullable=True)
        self.skip_pin = skip_pin
        self.status = (
            self._enum_matching(status, HostedPageStatus.list(), "status")
            if status
            else None
        )
