from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class SubscriptionHostedPageReponseCustomElements(BaseModel):
    """Description of the payment transaction.

    :param billing_address_collect: Determines whether the customer is asked to fill in the billing address. Relevant when a card payment method is selected. \<BR\> * **true** - The address fields appear on the checkout page.\<BR\> * **false** - The address fields appear only if the country is **US, **GB** or **CA**., defaults to None
    :type billing_address_collect: bool, optional
    :param cardholder_name: The name of the card owner, printed on the front of the card., defaults to None
    :type cardholder_name: str, optional
    :param display_description: Determines whether the checkout page displays the payment description.\<BR\>* **true** - The payment description appears.\<BR\> * **false** - The payment description does not appear.\<BR\> Relevant when description is passed in the Create Checkout Page request., defaults to None
    :type display_description: bool, optional
    :param dynamic_currency_conversion: Determines whether the checkout page displays multiple currency options for a payment.\<BR\> * **true** - Multiple currency options appear.\<BR\> * **false** - Currency options do not appear.\<BR\>When the customer selects the requested currency, the checkout page displays the following information:\<BR\>* The original amount and currency.\<BR\> * The converted amount in the requested currency.\<BR\> * The exchange rate.\<BR\> Relevant when: \<BR\> * The Create Checkout Page request passes requested_currency.\<BR\> * `fixed_side` is **buy**. \<BR\> * One or more payment methods support the values for `currency` and `requested_currency`., defaults to None
    :type dynamic_currency_conversion: bool, optional
    :param merchant_color: reserved, defaults to None
    :type merchant_color: str, optional
    :param merchant_currency_only: In a payment with FX where fixed_side=**buy**, determines whether the buyer's currency and the exchange rate appear. One of the following:\<BR\> * **true** - The currency and the exchange rate are hidden.\<BR\> * **false** - The currency and the exchange rate appear., defaults to None
    :type merchant_currency_only: bool, optional
    :param payment_fees_display: Determines whether payment fees appear on the checkout page.\<BR\> * **true** - Payment fees appear when the `payment_fees` object is set in the 'Create Checkout Page' request.\<BR\> * **false** - Payment fees do not appear., defaults to None
    :type payment_fees_display: bool, optional
    :param required_customer_fields: Indicates the list of fields that the customer has to fill in on the payment page before completing the payment via hosted checkout. Valid values include:\<BR\>* **name** – The customer's full name (default).\<BR\> * **email** – The customer's email address.\<BR\> * **phone_number** – The customer's phone number.\<BR\> * **address** – The address of the customer., defaults to None
    :type required_customer_fields: any, optional
    :param save_card_default: Determines whether the save card checkbox is checked by default.\<BR\> * **true** - The **save card** checkbox is checked.\<BR\> * **false** - The **save card** checkbox is cleared.\<BR\> Relevant when `customer_id` is passed in the 'Create Checkout Page' request., defaults to None
    :type save_card_default: bool, optional
    """

    def __init__(
        self,
        billing_address_collect: bool = None,
        cardholder_name: str = None,
        display_description: bool = None,
        dynamic_currency_conversion: bool = None,
        merchant_color: str = None,
        merchant_currency_only: bool = None,
        payment_fees_display: bool = None,
        required_customer_fields: any = None,
        save_card_default: bool = None,
    ):
        """Description of the payment transaction.

        :param billing_address_collect: Determines whether the customer is asked to fill in the billing address. Relevant when a card payment method is selected. \<BR\> * **true** - The address fields appear on the checkout page.\<BR\> * **false** - The address fields appear only if the country is **US, **GB** or **CA**., defaults to None
        :type billing_address_collect: bool, optional
        :param cardholder_name: The name of the card owner, printed on the front of the card., defaults to None
        :type cardholder_name: str, optional
        :param display_description: Determines whether the checkout page displays the payment description.\<BR\>* **true** - The payment description appears.\<BR\> * **false** - The payment description does not appear.\<BR\> Relevant when description is passed in the Create Checkout Page request., defaults to None
        :type display_description: bool, optional
        :param dynamic_currency_conversion: Determines whether the checkout page displays multiple currency options for a payment.\<BR\> * **true** - Multiple currency options appear.\<BR\> * **false** - Currency options do not appear.\<BR\>When the customer selects the requested currency, the checkout page displays the following information:\<BR\>* The original amount and currency.\<BR\> * The converted amount in the requested currency.\<BR\> * The exchange rate.\<BR\> Relevant when: \<BR\> * The Create Checkout Page request passes requested_currency.\<BR\> * `fixed_side` is **buy**. \<BR\> * One or more payment methods support the values for `currency` and `requested_currency`., defaults to None
        :type dynamic_currency_conversion: bool, optional
        :param merchant_color: reserved, defaults to None
        :type merchant_color: str, optional
        :param merchant_currency_only: In a payment with FX where fixed_side=**buy**, determines whether the buyer's currency and the exchange rate appear. One of the following:\<BR\> * **true** - The currency and the exchange rate are hidden.\<BR\> * **false** - The currency and the exchange rate appear., defaults to None
        :type merchant_currency_only: bool, optional
        :param payment_fees_display: Determines whether payment fees appear on the checkout page.\<BR\> * **true** - Payment fees appear when the `payment_fees` object is set in the 'Create Checkout Page' request.\<BR\> * **false** - Payment fees do not appear., defaults to None
        :type payment_fees_display: bool, optional
        :param required_customer_fields: Indicates the list of fields that the customer has to fill in on the payment page before completing the payment via hosted checkout. Valid values include:\<BR\>* **name** – The customer's full name (default).\<BR\> * **email** – The customer's email address.\<BR\> * **phone_number** – The customer's phone number.\<BR\> * **address** – The address of the customer., defaults to None
        :type required_customer_fields: any, optional
        :param save_card_default: Determines whether the save card checkbox is checked by default.\<BR\> * **true** - The **save card** checkbox is checked.\<BR\> * **false** - The **save card** checkbox is cleared.\<BR\> Relevant when `customer_id` is passed in the 'Create Checkout Page' request., defaults to None
        :type save_card_default: bool, optional
        """
        self.billing_address_collect = billing_address_collect
        self.cardholder_name = self._define_str(
            "cardholder_name", cardholder_name, nullable=True
        )
        self.display_description = display_description
        self.dynamic_currency_conversion = dynamic_currency_conversion
        self.merchant_color = self._define_str(
            "merchant_color", merchant_color, nullable=True
        )
        self.merchant_currency_only = merchant_currency_only
        self.payment_fees_display = payment_fees_display
        self.required_customer_fields = required_customer_fields
        self.save_card_default = save_card_default
