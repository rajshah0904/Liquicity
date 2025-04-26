from __future__ import annotations
from typing import Union
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.one_of_base_model import OneOfBaseModel
from .fee import Fee
from .payment import Payment
from .v1paymentssubscriptions_subscription_items import (
    V1paymentssubscriptionsSubscriptionItems,
)
from .payment_method_type import PaymentMethodType


class CheckoutSubscriptionsBodyPaymentMethodGuard(OneOfBaseModel):
    class_list = {"str": str, "PaymentMethodType": PaymentMethodType}


CheckoutSubscriptionsBodyPaymentMethod = Union[str, PaymentMethodType]


@JsonMap({})
class CheckoutSubscriptionsBody(BaseModel):
    """CheckoutSubscriptionsBody

    :param billing: Determines the method of billing. Set to **pay_automatically**.
    :type billing: str
    :param cancel_at_period_end: Determines the last date that charges accrue.\<BR\>* **true** - Charges accrue until the end of the current billing period, then the subscription is canceled. When no trial period is set, after this parameter is set to **true** the subscription will not be renewed at the next interval. When a trial period is set after this parameter is set to true, the subscription will not begin.\<BR\>* **false** - When the subscription is created, no end is defined. When Cancel Subscription is run, charges stop immediately and the subscription is canceled., defaults to None
    :type cancel_at_period_end: bool, optional
    :param complete_payment_url: URL where the customer is redirected when payment is successful, after returning from an external page such as a 3DS page. Does not support localhost URLs., defaults to None
    :type complete_payment_url: str, optional
    :param country: The two-letter ISO 3166-1 ALPHA-2 code for the country., defaults to None
    :type country: str, optional
    :param coupon: The ID of a coupon to apply a discount to the subscription. If the coupon defines a fixed monetary discount, it must use the same currency as the subscription. String starting with **coupon_**., defaults to None
    :type coupon: str, optional
    :param customer: ID of the customer who pays for this subscription. String starting with **cus_**.
    :type customer: str
    :param days_until_due: Number of days from the invoice date for customer to complete the payment., defaults to None
    :type days_until_due: float, optional
    :param error_payment_url: URL where the customer is redirected when payment is not successful, after returning from an external page, such as a 3DS page. Does not support localhost URLs., defaults to None
    :type error_payment_url: str, optional
    :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'. \<BR\> * When this parameter is null, the language of the user's browser is used. \<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param merchant_main_button: Defines the text for the call-to-action button on the subscription checkout page.\<BR\> * When there is no trial period, the values are: **subscribe** (default), **purchase**, **pay** \<BR\> When there is a trial period, the value is **start_trial** (default)., defaults to None
    :type merchant_main_button: str, optional
    :param merchant_reference_id: Identifier defined by the client for reference purposes. Limit: 45 characters., defaults to None
    :type merchant_reference_id: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If page_expiration is not set, the hosted page expires 14 days after creation.\<BR\> Range: 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param payment_fees: payment_fees, defaults to None
    :type payment_fees: Fee, optional
    :param payment_fields: Collects money from a payment method and deposits it into one or more Rapyd Wallets, defaults to None
    :type payment_fields: Payment, optional
    :param payment_method: Payment Method object or ID., defaults to None
    :type payment_method: CheckoutSubscriptionsBodyPaymentMethod, optional
    :param subscription_items: Array of subscription items. Each item contains a plan (required) and a quantity
    :type subscription_items: List[V1paymentssubscriptionsSubscriptionItems]
    :param tax_percent: The percentage of tax that is applied to the entire amount of the invoice., defaults to None
    :type tax_percent: float, optional
    :param trial_end: The date and time of the end of the customer's free trial period, in Unix time, or the string **now**. Takes precedence over `trial_period_days`. If `trial_end` is not set by the client, Rapyd calculates this date by adding `trial_period_days` to the date in `created_at`. \<BR\> Relevant when `trial_period_days` is not defined., defaults to None
    :type trial_end: float, optional
    :param trial_from_plan: Determines whether a free trial period can be defined in a 'plan' object attached to the subscription.\<BR\> * **true** - Free trials can be defined in plans that are attached to the subscription. \<BR\> * **false** - Definitions of free trial in plans are ignored., defaults to None
    :type trial_from_plan: bool, optional
    :param trial_period_days: The number of days in the customer's free trial period. Integer. Range: 0-730. This value takes precedence over trial periods that are defined in a plan. Relevant when `trial_end` is not defined.The number of days in the customer's free trial period., defaults to None
    :type trial_period_days: float, optional
    """

    def __init__(
        self,
        billing: str,
        customer: str,
        subscription_items: List[V1paymentssubscriptionsSubscriptionItems],
        cancel_at_period_end: bool = None,
        complete_payment_url: str = None,
        country: str = None,
        coupon: str = None,
        days_until_due: float = None,
        error_payment_url: str = None,
        language: str = None,
        metadata: dict = None,
        merchant_main_button: str = None,
        merchant_reference_id: str = None,
        page_expiration: float = None,
        payment_fees: Fee = None,
        payment_fields: Payment = None,
        payment_method: CheckoutSubscriptionsBodyPaymentMethod = None,
        tax_percent: float = None,
        trial_end: float = None,
        trial_from_plan: bool = None,
        trial_period_days: float = None,
    ):
        """CheckoutSubscriptionsBody

        :param billing: Determines the method of billing. Set to **pay_automatically**.
        :type billing: str
        :param cancel_at_period_end: Determines the last date that charges accrue.\<BR\>* **true** - Charges accrue until the end of the current billing period, then the subscription is canceled. When no trial period is set, after this parameter is set to **true** the subscription will not be renewed at the next interval. When a trial period is set after this parameter is set to true, the subscription will not begin.\<BR\>* **false** - When the subscription is created, no end is defined. When Cancel Subscription is run, charges stop immediately and the subscription is canceled., defaults to None
        :type cancel_at_period_end: bool, optional
        :param complete_payment_url: URL where the customer is redirected when payment is successful, after returning from an external page such as a 3DS page. Does not support localhost URLs., defaults to None
        :type complete_payment_url: str, optional
        :param country: The two-letter ISO 3166-1 ALPHA-2 code for the country., defaults to None
        :type country: str, optional
        :param coupon: The ID of a coupon to apply a discount to the subscription. If the coupon defines a fixed monetary discount, it must use the same currency as the subscription. String starting with **coupon_**., defaults to None
        :type coupon: str, optional
        :param customer: ID of the customer who pays for this subscription. String starting with **cus_**.
        :type customer: str
        :param days_until_due: Number of days from the invoice date for customer to complete the payment., defaults to None
        :type days_until_due: float, optional
        :param error_payment_url: URL where the customer is redirected when payment is not successful, after returning from an external page, such as a 3DS page. Does not support localhost URLs., defaults to None
        :type error_payment_url: str, optional
        :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'. \<BR\> * When this parameter is null, the language of the user's browser is used. \<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param merchant_main_button: Defines the text for the call-to-action button on the subscription checkout page.\<BR\> * When there is no trial period, the values are: **subscribe** (default), **purchase**, **pay** \<BR\> When there is a trial period, the value is **start_trial** (default)., defaults to None
        :type merchant_main_button: str, optional
        :param merchant_reference_id: Identifier defined by the client for reference purposes. Limit: 45 characters., defaults to None
        :type merchant_reference_id: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If page_expiration is not set, the hosted page expires 14 days after creation.\<BR\> Range: 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param payment_fees: payment_fees, defaults to None
        :type payment_fees: Fee, optional
        :param payment_fields: Collects money from a payment method and deposits it into one or more Rapyd Wallets, defaults to None
        :type payment_fields: Payment, optional
        :param payment_method: Payment Method object or ID., defaults to None
        :type payment_method: CheckoutSubscriptionsBodyPaymentMethod, optional
        :param subscription_items: Array of subscription items. Each item contains a plan (required) and a quantity
        :type subscription_items: List[V1paymentssubscriptionsSubscriptionItems]
        :param tax_percent: The percentage of tax that is applied to the entire amount of the invoice., defaults to None
        :type tax_percent: float, optional
        :param trial_end: The date and time of the end of the customer's free trial period, in Unix time, or the string **now**. Takes precedence over `trial_period_days`. If `trial_end` is not set by the client, Rapyd calculates this date by adding `trial_period_days` to the date in `created_at`. \<BR\> Relevant when `trial_period_days` is not defined., defaults to None
        :type trial_end: float, optional
        :param trial_from_plan: Determines whether a free trial period can be defined in a 'plan' object attached to the subscription.\<BR\> * **true** - Free trials can be defined in plans that are attached to the subscription. \<BR\> * **false** - Definitions of free trial in plans are ignored., defaults to None
        :type trial_from_plan: bool, optional
        :param trial_period_days: The number of days in the customer's free trial period. Integer. Range: 0-730. This value takes precedence over trial periods that are defined in a plan. Relevant when `trial_end` is not defined.The number of days in the customer's free trial period., defaults to None
        :type trial_period_days: float, optional
        """
        self.billing = billing
        self.cancel_at_period_end = cancel_at_period_end
        self.complete_payment_url = self._define_str(
            "complete_payment_url", complete_payment_url, nullable=True
        )
        self.country = self._define_str("country", country, nullable=True)
        self.coupon = self._define_str("coupon", coupon, nullable=True)
        self.customer = customer
        self.days_until_due = self._define_number(
            "days_until_due", days_until_due, nullable=True
        )
        self.error_payment_url = self._define_str(
            "error_payment_url", error_payment_url, nullable=True
        )
        self.language = self._define_str("language", language, nullable=True)
        self.metadata = metadata
        self.merchant_main_button = self._define_str(
            "merchant_main_button", merchant_main_button, nullable=True
        )
        self.merchant_reference_id = self._define_str(
            "merchant_reference_id", merchant_reference_id, nullable=True
        )
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.payment_fees = self._define_object(payment_fees, Fee)
        self.payment_fields = self._define_object(payment_fields, Payment)
        self.payment_method = CheckoutSubscriptionsBodyPaymentMethodGuard.return_one_of(
            payment_method
        )
        self.subscription_items = self._define_list(
            subscription_items, V1paymentssubscriptionsSubscriptionItems
        )
        self.tax_percent = self._define_number(
            "tax_percent", tax_percent, nullable=True
        )
        self.trial_end = self._define_number("trial_end", trial_end, nullable=True)
        self.trial_from_plan = trial_from_plan
        self.trial_period_days = self._define_number(
            "trial_period_days", trial_period_days, nullable=True
        )
