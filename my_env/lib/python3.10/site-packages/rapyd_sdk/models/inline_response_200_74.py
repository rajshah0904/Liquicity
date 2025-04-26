from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .merchant_customer_support import MerchantCustomerSupport
from .hosted_page_status import HostedPageStatus
from .payment_params import PaymentParams
from .customer_payment_method import CustomerPaymentMethod, CustomerPaymentMethodGuard


@JsonMap({})
class Card(BaseModel):
    """Card

    :param name: The name of the person that the card is issued to., defaults to None
    :type name: str, optional
    """

    def __init__(self, name: str = None):
        """Card

        :param name: The name of the person that the card is issued to., defaults to None
        :type name: str, optional
        """
        self.name = self._define_str("name", name, nullable=True)


@JsonMap({"id_": "id"})
class InlineResponse200_74Data(BaseModel):
    """InlineResponse200_74Data

    :param language: Determines the default language of the hosted page. When this parameter is null, the language of the user's browser is used. If the language of the user's browser cannot be determined, the default language is English, defaults to None
    :type language: str, optional
    :param merchant_alias: Reserved, the default name is Rapyd, defaults to None
    :type merchant_alias: str, optional
    :param merchant_color: Color of the call-to-action (CTA) button on the hosted page. To configure this field, use the Client Portal, defaults to None
    :type merchant_color: str, optional
    :param merchant_customer_support: Contains details of the client’s customer support. To configure these fields, use the Client Portal., defaults to None
    :type merchant_customer_support: MerchantCustomerSupport, optional
    :param merchant_logo: URL for the image of the client's logo. To configure this field, use the Client Portal, defaults to None
    :type merchant_logo: str, optional
    :param merchant_website: The URL where the customer is redirected after exiting the hosted page. Relevant when cancel_url or complete_url or both fields is unset. To configure this field, use the Client Portal, defaults to None
    :type merchant_website: str, optional
    :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
    :type redirect_url: str, optional
    :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Portal, defaults to None
    :type merchant_terms: str, optional
    :param cancel_url: URL where the customer is redirected after pressing Back to Website to exit the hosted page. This URL overrides the merchant_website URL. Does not support localhost URLs., defaults to None
    :type cancel_url: str, optional
    :param complete_url: URL where the customer is redirected after pressing Close to exit the hosted page. This URL overrides the merchant_website URL. Does not support localhost URLs., defaults to None
    :type complete_url: str, optional
    :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers. To configure this field, use the Client Portal., defaults to None
    :type merchant_privacy_policy: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If page_expiration is not set, the hosted page expires 14 days after creation. Range is 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param status: Status of the hosted page. One of the following: NEW - The hosted page was created. DON - Done. The card was added to the customer profile. EXP - The hosted page expired. , defaults to None
    :type status: HostedPageStatus, optional
    :param card: card, defaults to None
    :type card: Card, optional
    :param country: country, defaults to None
    :type country: str, optional
    :param currency: In transactions without FX, defines the currency of the transaction. Three-letter ISO 4217 code.\<BR\> In FX transactions:\<BR\> * When `fixed_side` is **buy**, it is the currency received in the Rapyd wallet.\<BR\> * When `fixed_side` is **sell**, it is the currency charged to the buyer., defaults to None
    :type currency: str, optional
    :param customer: ID of the customer, a string starting with **cus_**., defaults to None
    :type customer: str, optional
    :param id_: ID of the card token hosted page, a string starting with hp_card_, defaults to None
    :type id_: str, optional
    :param payment_method_type: Limits the page to a specific type of payment method. For example, dk_visa_card, defaults to None
    :type payment_method_type: str, optional
    :param payment_params: payment_params, defaults to None
    :type payment_params: PaymentParams, optional
    :param customer_card_payment_methods: customer_card_payment_methods, defaults to None
    :type customer_card_payment_methods: CustomerPaymentMethod, optional
    """

    def __init__(
        self,
        language: str = None,
        merchant_alias: str = None,
        merchant_color: str = None,
        merchant_customer_support: MerchantCustomerSupport = None,
        merchant_logo: str = None,
        merchant_website: str = None,
        redirect_url: str = None,
        merchant_terms: str = None,
        cancel_url: str = None,
        complete_url: str = None,
        merchant_privacy_policy: str = None,
        page_expiration: float = None,
        status: HostedPageStatus = None,
        card: Card = None,
        country: str = None,
        currency: str = None,
        customer: str = None,
        id_: str = None,
        payment_method_type: str = None,
        payment_params: PaymentParams = None,
        customer_card_payment_methods: CustomerPaymentMethod = None,
    ):
        """InlineResponse200_74Data

        :param language: Determines the default language of the hosted page. When this parameter is null, the language of the user's browser is used. If the language of the user's browser cannot be determined, the default language is English, defaults to None
        :type language: str, optional
        :param merchant_alias: Reserved, the default name is Rapyd, defaults to None
        :type merchant_alias: str, optional
        :param merchant_color: Color of the call-to-action (CTA) button on the hosted page. To configure this field, use the Client Portal, defaults to None
        :type merchant_color: str, optional
        :param merchant_customer_support: Contains details of the client’s customer support. To configure these fields, use the Client Portal., defaults to None
        :type merchant_customer_support: MerchantCustomerSupport, optional
        :param merchant_logo: URL for the image of the client's logo. To configure this field, use the Client Portal, defaults to None
        :type merchant_logo: str, optional
        :param merchant_website: The URL where the customer is redirected after exiting the hosted page. Relevant when cancel_url or complete_url or both fields is unset. To configure this field, use the Client Portal, defaults to None
        :type merchant_website: str, optional
        :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
        :type redirect_url: str, optional
        :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Portal, defaults to None
        :type merchant_terms: str, optional
        :param cancel_url: URL where the customer is redirected after pressing Back to Website to exit the hosted page. This URL overrides the merchant_website URL. Does not support localhost URLs., defaults to None
        :type cancel_url: str, optional
        :param complete_url: URL where the customer is redirected after pressing Close to exit the hosted page. This URL overrides the merchant_website URL. Does not support localhost URLs., defaults to None
        :type complete_url: str, optional
        :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers. To configure this field, use the Client Portal., defaults to None
        :type merchant_privacy_policy: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If page_expiration is not set, the hosted page expires 14 days after creation. Range is 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param status: Status of the hosted page. One of the following: NEW - The hosted page was created. DON - Done. The card was added to the customer profile. EXP - The hosted page expired. , defaults to None
        :type status: HostedPageStatus, optional
        :param card: card, defaults to None
        :type card: Card, optional
        :param country: country, defaults to None
        :type country: str, optional
        :param currency: In transactions without FX, defines the currency of the transaction. Three-letter ISO 4217 code.\<BR\> In FX transactions:\<BR\> * When `fixed_side` is **buy**, it is the currency received in the Rapyd wallet.\<BR\> * When `fixed_side` is **sell**, it is the currency charged to the buyer., defaults to None
        :type currency: str, optional
        :param customer: ID of the customer, a string starting with **cus_**., defaults to None
        :type customer: str, optional
        :param id_: ID of the card token hosted page, a string starting with hp_card_, defaults to None
        :type id_: str, optional
        :param payment_method_type: Limits the page to a specific type of payment method. For example, dk_visa_card, defaults to None
        :type payment_method_type: str, optional
        :param payment_params: payment_params, defaults to None
        :type payment_params: PaymentParams, optional
        :param customer_card_payment_methods: customer_card_payment_methods, defaults to None
        :type customer_card_payment_methods: CustomerPaymentMethod, optional
        """
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
        self.merchant_website = self._define_str(
            "merchant_website", merchant_website, nullable=True
        )
        self.redirect_url = self._define_str(
            "redirect_url", redirect_url, nullable=True
        )
        self.merchant_terms = self._define_str(
            "merchant_terms", merchant_terms, nullable=True
        )
        self.cancel_url = self._define_str("cancel_url", cancel_url, nullable=True)
        self.complete_url = self._define_str(
            "complete_url", complete_url, nullable=True
        )
        self.merchant_privacy_policy = self._define_str(
            "merchant_privacy_policy", merchant_privacy_policy, nullable=True
        )
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.status = (
            self._enum_matching(status, HostedPageStatus.list(), "status")
            if status
            else None
        )
        self.card = self._define_object(card, Card)
        self.country = self._define_str(
            "country",
            country,
            nullable=True,
            pattern="Name of the country. Two-letter ISO 3166-1 alpha-2 code.",
        )
        self.currency = self._define_str(
            "currency",
            currency,
            nullable=True,
            pattern="/^AED|AFN|ALL|AMD|ANG|AOA|ARS|AUD|AWG|AZN|BAM|BBD|BDT|BGN|BHD|BIF|BMD|BND|BOB|BRL|BSD|BTN|BWP|BYR|BZD|CAD|CDF|CHF|CLP|CNY|COP|CRC|CUC|CUP|CVE|CZK|DJF|DKK|DOP|DZD|EGP|ERN|ETB|EUR|FJD|FKP|GBP|GEL|GGP|GHS|GIP|GMD|GNF|GTQ|GYD|HKD|HNL|HRK|HTG|HUF|IDR|ILS|IMP|INR|IQD|IRR|ISK|JEP|JMD|JOD|JPY|KES|KGS|KHR|KMF|KPW|KRW|KWD|KYD|KZT|LAK|LBP|LKR|LRD|LSL|LYD|MAD|MDL|MGA|MKD|MMK|MNT|MOP|MRO|MUR|MVR|MWK|MXN|MYR|MZN|NAD|NGN|NIO|NOK|NPR|NZD|OMR|PAB|PEN|PGK|PHP|PKR|PLN|PYG|QAR|RON|RSD|RUB|RWF|SAR|SBD|SCR|SDG|SEK|SGD|SHP|SLL|SOS|SPL|SRD|STD|SVC|SYP|SZL|THB|TJS|TMT|TND|TOP|TRY|TTD|TVD|TWD|TZS|UAH|UGX|USD|UYU|UZS|VEF|VND|VUV|WST|XAF|XCD|XDR|XOF|XPF|YER|ZAR|ZMW|ZWD$/",
        )
        self.customer = self._define_str("customer", customer, nullable=True)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.payment_method_type = self._define_str(
            "payment_method_type", payment_method_type, nullable=True
        )
        self.payment_params = self._define_object(payment_params, PaymentParams)
        self.customer_card_payment_methods = CustomerPaymentMethodGuard.return_one_of(
            customer_card_payment_methods
        )


@JsonMap({})
class InlineResponse200_74(BaseModel):
    """InlineResponse200_74

    :param data: data, defaults to None
    :type data: InlineResponse200_74Data, optional
    :param status: status, defaults to None
    :type status: Status1, optional
    """

    def __init__(self, data: InlineResponse200_74Data = None, status: Status1 = None):
        """InlineResponse200_74

        :param data: data, defaults to None
        :type data: InlineResponse200_74Data, optional
        :param status: status, defaults to None
        :type status: Status1, optional
        """
        self.data = self._define_object(data, InlineResponse200_74Data)
        self.status = self._define_object(status, Status1)
