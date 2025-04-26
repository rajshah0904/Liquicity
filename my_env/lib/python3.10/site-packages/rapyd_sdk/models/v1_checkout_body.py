from __future__ import annotations
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .hosted_page_additional_response_cart_items import (
    HostedPageAdditionalResponseCartItems,
)
from .hosted_page_additional_response_custom_elements import (
    HostedPageAdditionalResponseCustomElements,
)
from .payment import Payment


@JsonMap({"id_": "id"})
class V1CheckoutBody(BaseModel):
    """V1CheckoutBody

    :param account_funding_transaction: Details of an account funding transaction (AFT), which transfers funds from a card to a cardholder's wallet., defaults to None
    :type account_funding_transaction: dict, optional
    :param amount: The amount of the payment, in units of the currency defined in currency. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015. If the amount is a whole number, use an integer and not a decimal.
    :type amount: float
    :param cancel_checkout_url: URL where the customer is redirected after pressing Back to Website to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type cancel_checkout_url: str, optional
    :param cart_items: Describes the cart items that the customer is purchasing. These items are displayed at the checkout page., defaults to None
    :type cart_items: HostedPageAdditionalResponseCartItems, optional
    :param complete_checkout_url: URL where the customer is redirected after pressing Finish to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type complete_checkout_url: str, optional
    :param country: country
    :type country: str
    :param currency: In transactions without FX, defines the currency of the transaction. Three-letter ISO 4217 code.\<BR\> In FX transactions:\<BR\> * When `fixed_side` is **buy**, it is the currency received in the Rapyd wallet.\<BR\> * When `fixed_side` is **sell**, it is the currency charged to the buyer.
    :type currency: str
    :param customer: Description of the payment transaction. To display the description, set display_description to true in custom_elements., defaults to None
    :type customer: str, optional
    :param escrow: Determines whether the payment is held in escrow for later release., defaults to None
    :type escrow: bool, optional
    :param escrow_release_days: Determines the number of days after creation of the payment that funds are released from escrow. Funds are released at 5:00 pm GMT on the day indicated. Integer, range: 1-90., defaults to None
    :type escrow_release_days: float, optional
    :param id_: ID of the Rapyd checkout page. String starting with **checkout_**., defaults to None
    :type id_: str, optional
    :param merchant_main_button: A string that represents the text on the main Call to Action (CTA) button. One of the following:\<BR\>* place_your_order - Place Your Order.\<BR\>* pay - Pay.\<BR\>* pay_now - Pay Now.\<BR\>* make_payment - Make Payment.\<BR\>* purchase - Purchase.\<BR\>* buy - Buy.\<BR\>* donate - Donate.\<BR\>* To configure this button, use the Client Portal., defaults to None
    :type merchant_main_button: str, optional
    :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers. To configure this field, use the Client Portal., defaults to None
    :type merchant_privacy_policy: str, optional
    :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Portal, defaults to None
    :type merchant_terms: str, optional
    :param merchant_website: The URL where the customer is redirected after exiting the hosted page. Relevant when one or both of the following fields is unset: \<BR\>* `cancel_url` \<BR\>* `complete_url`.\<BR\> To configure this field, use the Client Portal, defaults to None
    :type merchant_website: str, optional
    :param custom_elements: Description of the payment transaction., defaults to None
    :type custom_elements: HostedPageAdditionalResponseCustomElements, optional
    :param page_expiration: Length of time for the payment to be completed after it is created, measured in seconds. When both expiration and payment_expiration are set, the payment expires at the earlier time., defaults to None
    :type page_expiration: float, optional
    :param payment: Collects money from a payment method and deposits it into one or more Rapyd Wallets, defaults to None
    :type payment: Payment, optional
    :param payment_expiration: Length of time for the payment to be completed after it is created, measured in seconds. When both expiration and payment_expiration are set, the payment expires at the earlier time., defaults to None
    :type payment_expiration: float, optional
    :param payment_method_type: The type of the payment method. For example, **it_visa_card**, defaults to None
    :type payment_method_type: str, optional
    :param payment_method_type_categories: A list of the categories of payment method that are supported on the checkout page. The categories appear on the page in the order provided, defaults to None
    :type payment_method_type_categories: List[str], optional
    :param payment_method_types_exclude: List of payment methods that are excluded from display on the checkout page., defaults to None
    :type payment_method_types_exclude: List[str], optional
    :param payment_method_types_include: List of payment methods that are displayed on the checkout page. The payment methods appear on the page in the order provided., defaults to None
    :type payment_method_types_include: List[str], optional
    :param timestamp: Time of creation of the checkout page, in Unix time., defaults to None
    :type timestamp: float, optional
    """

    def __init__(
        self,
        amount: float,
        country: str,
        currency: str,
        account_funding_transaction: dict = None,
        cancel_checkout_url: str = None,
        cart_items: HostedPageAdditionalResponseCartItems = None,
        complete_checkout_url: str = None,
        customer: str = None,
        escrow: bool = None,
        escrow_release_days: float = None,
        id_: str = None,
        merchant_main_button: str = None,
        merchant_privacy_policy: str = None,
        merchant_terms: str = None,
        merchant_website: str = None,
        custom_elements: HostedPageAdditionalResponseCustomElements = None,
        page_expiration: float = None,
        payment: Payment = None,
        payment_expiration: float = None,
        payment_method_type: str = None,
        payment_method_type_categories: List[str] = None,
        payment_method_types_exclude: List[str] = None,
        payment_method_types_include: List[str] = None,
        timestamp: float = None,
    ):
        """V1CheckoutBody

        :param account_funding_transaction: Details of an account funding transaction (AFT), which transfers funds from a card to a cardholder's wallet., defaults to None
        :type account_funding_transaction: dict, optional
        :param amount: The amount of the payment, in units of the currency defined in currency. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015. If the amount is a whole number, use an integer and not a decimal.
        :type amount: float
        :param cancel_checkout_url: URL where the customer is redirected after pressing Back to Website to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type cancel_checkout_url: str, optional
        :param cart_items: Describes the cart items that the customer is purchasing. These items are displayed at the checkout page., defaults to None
        :type cart_items: HostedPageAdditionalResponseCartItems, optional
        :param complete_checkout_url: URL where the customer is redirected after pressing Finish to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type complete_checkout_url: str, optional
        :param country: country
        :type country: str
        :param currency: In transactions without FX, defines the currency of the transaction. Three-letter ISO 4217 code.\<BR\> In FX transactions:\<BR\> * When `fixed_side` is **buy**, it is the currency received in the Rapyd wallet.\<BR\> * When `fixed_side` is **sell**, it is the currency charged to the buyer.
        :type currency: str
        :param customer: Description of the payment transaction. To display the description, set display_description to true in custom_elements., defaults to None
        :type customer: str, optional
        :param escrow: Determines whether the payment is held in escrow for later release., defaults to None
        :type escrow: bool, optional
        :param escrow_release_days: Determines the number of days after creation of the payment that funds are released from escrow. Funds are released at 5:00 pm GMT on the day indicated. Integer, range: 1-90., defaults to None
        :type escrow_release_days: float, optional
        :param id_: ID of the Rapyd checkout page. String starting with **checkout_**., defaults to None
        :type id_: str, optional
        :param merchant_main_button: A string that represents the text on the main Call to Action (CTA) button. One of the following:\<BR\>* place_your_order - Place Your Order.\<BR\>* pay - Pay.\<BR\>* pay_now - Pay Now.\<BR\>* make_payment - Make Payment.\<BR\>* purchase - Purchase.\<BR\>* buy - Buy.\<BR\>* donate - Donate.\<BR\>* To configure this button, use the Client Portal., defaults to None
        :type merchant_main_button: str, optional
        :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers. To configure this field, use the Client Portal., defaults to None
        :type merchant_privacy_policy: str, optional
        :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Portal, defaults to None
        :type merchant_terms: str, optional
        :param merchant_website: The URL where the customer is redirected after exiting the hosted page. Relevant when one or both of the following fields is unset: \<BR\>* `cancel_url` \<BR\>* `complete_url`.\<BR\> To configure this field, use the Client Portal, defaults to None
        :type merchant_website: str, optional
        :param custom_elements: Description of the payment transaction., defaults to None
        :type custom_elements: HostedPageAdditionalResponseCustomElements, optional
        :param page_expiration: Length of time for the payment to be completed after it is created, measured in seconds. When both expiration and payment_expiration are set, the payment expires at the earlier time., defaults to None
        :type page_expiration: float, optional
        :param payment: Collects money from a payment method and deposits it into one or more Rapyd Wallets, defaults to None
        :type payment: Payment, optional
        :param payment_expiration: Length of time for the payment to be completed after it is created, measured in seconds. When both expiration and payment_expiration are set, the payment expires at the earlier time., defaults to None
        :type payment_expiration: float, optional
        :param payment_method_type: The type of the payment method. For example, **it_visa_card**, defaults to None
        :type payment_method_type: str, optional
        :param payment_method_type_categories: A list of the categories of payment method that are supported on the checkout page. The categories appear on the page in the order provided, defaults to None
        :type payment_method_type_categories: List[str], optional
        :param payment_method_types_exclude: List of payment methods that are excluded from display on the checkout page., defaults to None
        :type payment_method_types_exclude: List[str], optional
        :param payment_method_types_include: List of payment methods that are displayed on the checkout page. The payment methods appear on the page in the order provided., defaults to None
        :type payment_method_types_include: List[str], optional
        :param timestamp: Time of creation of the checkout page, in Unix time., defaults to None
        :type timestamp: float, optional
        """
        self.account_funding_transaction = account_funding_transaction
        self.amount = amount
        self.cancel_checkout_url = self._define_str(
            "cancel_checkout_url", cancel_checkout_url, nullable=True
        )
        self.cart_items = self._define_object(
            cart_items, HostedPageAdditionalResponseCartItems
        )
        self.complete_checkout_url = self._define_str(
            "complete_checkout_url", complete_checkout_url, nullable=True
        )
        self.country = self._define_str(
            "country",
            country,
            pattern="Name of the country. Two-letter ISO 3166-1 alpha-2 code.",
        )
        self.currency = self._define_str(
            "currency",
            currency,
            pattern="/^AED|AFN|ALL|AMD|ANG|AOA|ARS|AUD|AWG|AZN|BAM|BBD|BDT|BGN|BHD|BIF|BMD|BND|BOB|BRL|BSD|BTN|BWP|BYR|BZD|CAD|CDF|CHF|CLP|CNY|COP|CRC|CUC|CUP|CVE|CZK|DJF|DKK|DOP|DZD|EGP|ERN|ETB|EUR|FJD|FKP|GBP|GEL|GGP|GHS|GIP|GMD|GNF|GTQ|GYD|HKD|HNL|HRK|HTG|HUF|IDR|ILS|IMP|INR|IQD|IRR|ISK|JEP|JMD|JOD|JPY|KES|KGS|KHR|KMF|KPW|KRW|KWD|KYD|KZT|LAK|LBP|LKR|LRD|LSL|LYD|MAD|MDL|MGA|MKD|MMK|MNT|MOP|MRO|MUR|MVR|MWK|MXN|MYR|MZN|NAD|NGN|NIO|NOK|NPR|NZD|OMR|PAB|PEN|PGK|PHP|PKR|PLN|PYG|QAR|RON|RSD|RUB|RWF|SAR|SBD|SCR|SDG|SEK|SGD|SHP|SLL|SOS|SPL|SRD|STD|SVC|SYP|SZL|THB|TJS|TMT|TND|TOP|TRY|TTD|TVD|TWD|TZS|UAH|UGX|USD|UYU|UZS|VEF|VND|VUV|WST|XAF|XCD|XDR|XOF|XPF|YER|ZAR|ZMW|ZWD$/",
        )
        self.customer = self._define_str("customer", customer, nullable=True)
        self.escrow = escrow
        self.escrow_release_days = self._define_number(
            "escrow_release_days", escrow_release_days, nullable=True
        )
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.merchant_main_button = self._define_str(
            "merchant_main_button", merchant_main_button, nullable=True
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
        self.custom_elements = self._define_object(
            custom_elements, HostedPageAdditionalResponseCustomElements
        )
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.payment = self._define_object(payment, Payment)
        self.payment_expiration = self._define_number(
            "payment_expiration", payment_expiration, nullable=True
        )
        self.payment_method_type = self._define_str(
            "payment_method_type", payment_method_type, nullable=True
        )
        self.payment_method_type_categories = payment_method_type_categories
        self.payment_method_types_exclude = payment_method_types_exclude
        self.payment_method_types_include = payment_method_types_include
        self.timestamp = self._define_number("timestamp", timestamp, nullable=True)
