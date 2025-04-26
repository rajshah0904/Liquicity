from __future__ import annotations
from enum import Enum
from typing import Union
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.one_of_base_model import OneOfBaseModel
from .subscription_hosted_page_reponse_custom_elements import (
    SubscriptionHostedPageReponseCustomElements,
)
from .discount import Discount
from .subscription_hosted_page_reponse_merchant_customer_support import (
    SubscriptionHostedPageReponseMerchantCustomerSupport,
)
from .subscription_items import SubscriptionItems


class SubscriptionHostedPageReponseBillingCycleAnchorGuard(OneOfBaseModel):
    class_list = {"str": str, "float": float}


SubscriptionHostedPageReponseBillingCycleAnchor = Union[str, float]


class SubscriptionHostedPageReponseStatus(Enum):
    """An enumeration representing different categories.

    :cvar ACTIVE: "active"
    :vartype ACTIVE: str
    :cvar CANCELED: "canceled"
    :vartype CANCELED: str
    :cvar PASTDUE: "past_due"
    :vartype PASTDUE: str
    :cvar TRIALING: "trialing"
    :vartype TRIALING: str
    :cvar UNPAID: "unpaid"
    :vartype UNPAID: str
    """

    ACTIVE = "active"
    CANCELED = "canceled"
    PASTDUE = "past_due"
    TRIALING = "trialing"
    UNPAID = "unpaid"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                SubscriptionHostedPageReponseStatus._member_map_.values(),
            )
        )


@JsonMap({"id_": "id"})
class SubscriptionHostedPageReponse(BaseModel):
    """SubscriptionHostedPageReponse

    :param billing: Determines the method of billing at the end of the billing cycle. Set to pay_automatically - Rapyd generates a 'payment' object, then attempts to pay it using the designated payment method., defaults to None
    :type billing: str, optional
    :param billing_cycle_anchor: Determines the start of the next full billing cycle, as defined in the plan described in the 'items'. One of the following values:  * **now** - The present day. The next billing cycle starts right now.  * \<em\>Timestamp\</em\> in Unix time - A time in the future, at or after the end of the free trial period, not more than the length of the billing cycle. The current billing cycle will be shorter than all other billing cycles. Relevant to creation of the subscription.  * **unchanged** - The original billing cycle anchor is unchanged. Relevant to updating a subscription. , defaults to None
    :type billing_cycle_anchor: SubscriptionHostedPageReponseBillingCycleAnchor, optional
    :param cancel_at_period_end: Determines the last date that charges accrue. **true** - Charges accrue until the end of the current billing period, then the subscription is canceled.  * When no trial period is set, after `cancel_at_period_end` is set to **true** the subscription will not be renewed at the next interval.  * When a trial period is set after `cancel_at_period_end` is set to **true**, the subscription will not begin. \<BR\> * **false** - This is the default.  * When the subscription is created, no end is defined. * When 'Cancel Subscription' is run, charges stop immediately and the subscription is canceled. , defaults to None
    :type cancel_at_period_end: bool, optional
    :param cancel_checkout_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs. or by the client. Unix time. Response only., defaults to None
    :type cancel_checkout_url: str, optional
    :param canceled_at: Date and time that the subscription is canceled by the customer or by the client. Unix time. Response only., defaults to None
    :type canceled_at: float, optional
    :param complete_checkout_url: URL where the customer is redirected after pressing **Finish** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type complete_checkout_url: str, optional
    :param complete_payment_url: URL where the customer is redirected when payment is successful, after returning from an external page such as a 3DS page. Does not support localhost URLs., defaults to None
    :type complete_payment_url: str, optional
    :param country: The two-letter ISO 3166-1 ALPHA-2 code for the country., defaults to None
    :type country: str, optional
    :param coupon: ID of a coupon to apply a discount to the subscription. String starting with **coupon_**., defaults to None
    :type coupon: str, optional
    :param created_at: Time of creation of this subscription, in Unix time. Response only., defaults to None
    :type created_at: float, optional
    :param current_period_end: End of the current billing cycle, in Unix time. Response only., defaults to None
    :type current_period_end: float, optional
    :param current_period_start: Start of the current billing cycle, in Unix time. Response only., defaults to None
    :type current_period_start: float, optional
    :param custom_elements: Description of the payment transaction., defaults to None
    :type custom_elements: SubscriptionHostedPageReponseCustomElements, optional
    :param customer: ID of the customer who pays for this subscription. String starting with cus_. Response only., defaults to None
    :type customer: str, optional
    :param days_until_due: Number of days from the invoice date for customer to complete the payment., defaults to None
    :type days_until_due: float, optional
    :param discount: Describes the fields relating to discounts in REST messages and webhooks for customer profiles and subscriptions Contains information about the coupon that applies to the customer. Read-only field. Adding a discount is a 2-step process: \<BR\> 1. Create Coupon, which returns a coupon ID. \<BR\>2. Add the coupon ID to the coupon field of the customer with Create Customer or Update Customer., defaults to None
    :type discount: Discount, optional
    :param error_payment_url: URL where the customer is redirected when payment is not successful, after returning from an external page, such as a 3DS page. Does not support localhost URLs., defaults to None
    :type error_payment_url: str, optional
    :param id_: ID of the subscription. String starting with **hp_sub_**., defaults to None
    :type id_: str, optional
    :param language: Determines the default language of the hosted page. For a list of values, see List Supported Languages.\<BR\> * When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param merchant_alias: Client's name., defaults to None
    :type merchant_alias: str, optional
    :param merchant_color: Color of the call-to-action (CTA) button on the hosted page.\<BR\> To configure this field, use the Client Portal., defaults to None
    :type merchant_color: str, optional
    :param merchant_customer_support: merchant_customer_support, defaults to None
    :type merchant_customer_support: SubscriptionHostedPageReponseMerchantCustomerSupport, optional
    :param merchant_main_button: Indicates the text for the call-to-action button on the subscription checkout page., defaults to None
    :type merchant_main_button: dict, optional
    :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers.\<BR\> To configure this field, use the Client Portal. See Customizing Your Hosted Page., defaults to None
    :type merchant_privacy_policy: str, optional
    :param merchant_reference_id: Identifier defined by the client for reference purposes. Limit: 45 characters., defaults to None
    :type merchant_reference_id: str, optional
    :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Portal., defaults to None
    :type merchant_terms: str, optional
    :param merchant_website: The URL where the customer is redirected after exiting the hosted page.\<BR\> Relevant when one or both of the following fields is unset:\<BR\>* **cancel_url**\<BR\>* **complete_url**\<BR\> To configure this field, use the Client Portal. See Customizing Your Hosted Page.URL for the client's terms and conditions. To configure this field, use the Client Portal., defaults to None
    :type merchant_website: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If page_expiration is not set, the hosted page expires 14 days after creation.\<BR\> * **Range**: 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param payment: Describes the payment that will result from the hosted page. The id and status values are **null** until the customer successfully submits the information on the hosted page. For more information about the fields in the 'payment' object, see Create Payment., defaults to None
    :type payment: dict, optional
    :param payment_fields: Additional `payment_options` fields., defaults to None
    :type payment_fields: dict, optional
    :param payment_method: Payment method used for paying invoices generated by this subscription. The ID is a string starting with **card_** or **other_**., defaults to None
    :type payment_method: str, optional
    :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
    :type redirect_url: str, optional
    :param status: Status of the subscription. One of the following:  * active - The customer is currently paying for this subscription.  * canceled - The customer has canceled this subscription, but it remains in the Rapyd database.  * past_due - Payment for this subscription was not received by the end of the billing period.  * trialing - The subscription is in its free trial period. * unpaid - An error occurred in the payment for this subscription. Response only. , defaults to None
    :type status: SubscriptionHostedPageReponseStatus, optional
    :param subscription_items: subscription_items, defaults to None
    :type subscription_items: SubscriptionItems, optional
    :param tax_percent: The percentage tax rate that is applied to the subtotal of the invoice, after subtracting all discounts. Decimal. Range: 0-100, with up to four decimal places., defaults to None
    :type tax_percent: float, optional
    :param total_count: Total number of subscription items., defaults to None
    :type total_count: float, optional
    :param trial_end: The date and time of the end of the customer's free trial period, in Unix time, or the string **now**. Takes precedence over `trial_period_days`. If `trial_end` is not set by the client, Rapyd calculates this date by adding `trial_period_days` to the date in `created_at`. Relevant when `trial_period_days` is not defined., defaults to None
    :type trial_end: float, optional
    :param trial_from_plan: Determines whether a free trial period can be defined in a plan attached to the subscription., defaults to None
    :type trial_from_plan: bool, optional
    :param trial_period_days: The number of days in the customer's free trial period. Integer. Range: 0-730. This value takes precedence over trial periods that are defined in a plan. Relevant when `trial_end` is not defined., defaults to None
    :type trial_period_days: float, optional
    :param trial_start: Date and time of the start of the customer's free trial period, in Unix time., defaults to None
    :type trial_start: float, optional
    """

    def __init__(
        self,
        billing: str = None,
        billing_cycle_anchor: SubscriptionHostedPageReponseBillingCycleAnchor = None,
        cancel_at_period_end: bool = None,
        cancel_checkout_url: str = None,
        canceled_at: float = None,
        complete_checkout_url: str = None,
        complete_payment_url: str = None,
        country: str = None,
        coupon: str = None,
        created_at: float = None,
        current_period_end: float = None,
        current_period_start: float = None,
        custom_elements: SubscriptionHostedPageReponseCustomElements = None,
        customer: str = None,
        days_until_due: float = None,
        discount: Discount = None,
        error_payment_url: str = None,
        id_: str = None,
        language: str = None,
        merchant_alias: str = None,
        merchant_color: str = None,
        merchant_customer_support: SubscriptionHostedPageReponseMerchantCustomerSupport = None,
        merchant_main_button: dict = None,
        merchant_privacy_policy: str = None,
        merchant_reference_id: str = None,
        merchant_terms: str = None,
        merchant_website: str = None,
        metadata: dict = None,
        page_expiration: float = None,
        payment: dict = None,
        payment_fields: dict = None,
        payment_method: str = None,
        redirect_url: str = None,
        status: SubscriptionHostedPageReponseStatus = None,
        subscription_items: SubscriptionItems = None,
        tax_percent: float = None,
        total_count: float = None,
        trial_end: float = None,
        trial_from_plan: bool = None,
        trial_period_days: float = None,
        trial_start: float = None,
    ):
        """SubscriptionHostedPageReponse

        :param billing: Determines the method of billing at the end of the billing cycle. Set to pay_automatically - Rapyd generates a 'payment' object, then attempts to pay it using the designated payment method., defaults to None
        :type billing: str, optional
        :param billing_cycle_anchor: Determines the start of the next full billing cycle, as defined in the plan described in the 'items'. One of the following values:  * **now** - The present day. The next billing cycle starts right now.  * \<em\>Timestamp\</em\> in Unix time - A time in the future, at or after the end of the free trial period, not more than the length of the billing cycle. The current billing cycle will be shorter than all other billing cycles. Relevant to creation of the subscription.  * **unchanged** - The original billing cycle anchor is unchanged. Relevant to updating a subscription. , defaults to None
        :type billing_cycle_anchor: SubscriptionHostedPageReponseBillingCycleAnchor, optional
        :param cancel_at_period_end: Determines the last date that charges accrue. **true** - Charges accrue until the end of the current billing period, then the subscription is canceled.  * When no trial period is set, after `cancel_at_period_end` is set to **true** the subscription will not be renewed at the next interval.  * When a trial period is set after `cancel_at_period_end` is set to **true**, the subscription will not begin. \<BR\> * **false** - This is the default.  * When the subscription is created, no end is defined. * When 'Cancel Subscription' is run, charges stop immediately and the subscription is canceled. , defaults to None
        :type cancel_at_period_end: bool, optional
        :param cancel_checkout_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs. or by the client. Unix time. Response only., defaults to None
        :type cancel_checkout_url: str, optional
        :param canceled_at: Date and time that the subscription is canceled by the customer or by the client. Unix time. Response only., defaults to None
        :type canceled_at: float, optional
        :param complete_checkout_url: URL where the customer is redirected after pressing **Finish** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type complete_checkout_url: str, optional
        :param complete_payment_url: URL where the customer is redirected when payment is successful, after returning from an external page such as a 3DS page. Does not support localhost URLs., defaults to None
        :type complete_payment_url: str, optional
        :param country: The two-letter ISO 3166-1 ALPHA-2 code for the country., defaults to None
        :type country: str, optional
        :param coupon: ID of a coupon to apply a discount to the subscription. String starting with **coupon_**., defaults to None
        :type coupon: str, optional
        :param created_at: Time of creation of this subscription, in Unix time. Response only., defaults to None
        :type created_at: float, optional
        :param current_period_end: End of the current billing cycle, in Unix time. Response only., defaults to None
        :type current_period_end: float, optional
        :param current_period_start: Start of the current billing cycle, in Unix time. Response only., defaults to None
        :type current_period_start: float, optional
        :param custom_elements: Description of the payment transaction., defaults to None
        :type custom_elements: SubscriptionHostedPageReponseCustomElements, optional
        :param customer: ID of the customer who pays for this subscription. String starting with cus_. Response only., defaults to None
        :type customer: str, optional
        :param days_until_due: Number of days from the invoice date for customer to complete the payment., defaults to None
        :type days_until_due: float, optional
        :param discount: Describes the fields relating to discounts in REST messages and webhooks for customer profiles and subscriptions Contains information about the coupon that applies to the customer. Read-only field. Adding a discount is a 2-step process: \<BR\> 1. Create Coupon, which returns a coupon ID. \<BR\>2. Add the coupon ID to the coupon field of the customer with Create Customer or Update Customer., defaults to None
        :type discount: Discount, optional
        :param error_payment_url: URL where the customer is redirected when payment is not successful, after returning from an external page, such as a 3DS page. Does not support localhost URLs., defaults to None
        :type error_payment_url: str, optional
        :param id_: ID of the subscription. String starting with **hp_sub_**., defaults to None
        :type id_: str, optional
        :param language: Determines the default language of the hosted page. For a list of values, see List Supported Languages.\<BR\> * When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param merchant_alias: Client's name., defaults to None
        :type merchant_alias: str, optional
        :param merchant_color: Color of the call-to-action (CTA) button on the hosted page.\<BR\> To configure this field, use the Client Portal., defaults to None
        :type merchant_color: str, optional
        :param merchant_customer_support: merchant_customer_support, defaults to None
        :type merchant_customer_support: SubscriptionHostedPageReponseMerchantCustomerSupport, optional
        :param merchant_main_button: Indicates the text for the call-to-action button on the subscription checkout page., defaults to None
        :type merchant_main_button: dict, optional
        :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers.\<BR\> To configure this field, use the Client Portal. See Customizing Your Hosted Page., defaults to None
        :type merchant_privacy_policy: str, optional
        :param merchant_reference_id: Identifier defined by the client for reference purposes. Limit: 45 characters., defaults to None
        :type merchant_reference_id: str, optional
        :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Portal., defaults to None
        :type merchant_terms: str, optional
        :param merchant_website: The URL where the customer is redirected after exiting the hosted page.\<BR\> Relevant when one or both of the following fields is unset:\<BR\>* **cancel_url**\<BR\>* **complete_url**\<BR\> To configure this field, use the Client Portal. See Customizing Your Hosted Page.URL for the client's terms and conditions. To configure this field, use the Client Portal., defaults to None
        :type merchant_website: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If page_expiration is not set, the hosted page expires 14 days after creation.\<BR\> * **Range**: 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param payment: Describes the payment that will result from the hosted page. The id and status values are **null** until the customer successfully submits the information on the hosted page. For more information about the fields in the 'payment' object, see Create Payment., defaults to None
        :type payment: dict, optional
        :param payment_fields: Additional `payment_options` fields., defaults to None
        :type payment_fields: dict, optional
        :param payment_method: Payment method used for paying invoices generated by this subscription. The ID is a string starting with **card_** or **other_**., defaults to None
        :type payment_method: str, optional
        :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
        :type redirect_url: str, optional
        :param status: Status of the subscription. One of the following:  * active - The customer is currently paying for this subscription.  * canceled - The customer has canceled this subscription, but it remains in the Rapyd database.  * past_due - Payment for this subscription was not received by the end of the billing period.  * trialing - The subscription is in its free trial period. * unpaid - An error occurred in the payment for this subscription. Response only. , defaults to None
        :type status: SubscriptionHostedPageReponseStatus, optional
        :param subscription_items: subscription_items, defaults to None
        :type subscription_items: SubscriptionItems, optional
        :param tax_percent: The percentage tax rate that is applied to the subtotal of the invoice, after subtracting all discounts. Decimal. Range: 0-100, with up to four decimal places., defaults to None
        :type tax_percent: float, optional
        :param total_count: Total number of subscription items., defaults to None
        :type total_count: float, optional
        :param trial_end: The date and time of the end of the customer's free trial period, in Unix time, or the string **now**. Takes precedence over `trial_period_days`. If `trial_end` is not set by the client, Rapyd calculates this date by adding `trial_period_days` to the date in `created_at`. Relevant when `trial_period_days` is not defined., defaults to None
        :type trial_end: float, optional
        :param trial_from_plan: Determines whether a free trial period can be defined in a plan attached to the subscription., defaults to None
        :type trial_from_plan: bool, optional
        :param trial_period_days: The number of days in the customer's free trial period. Integer. Range: 0-730. This value takes precedence over trial periods that are defined in a plan. Relevant when `trial_end` is not defined., defaults to None
        :type trial_period_days: float, optional
        :param trial_start: Date and time of the start of the customer's free trial period, in Unix time., defaults to None
        :type trial_start: float, optional
        """
        self.billing = self._define_str("billing", billing, nullable=True)
        self.billing_cycle_anchor = (
            SubscriptionHostedPageReponseBillingCycleAnchorGuard.return_one_of(
                billing_cycle_anchor
            )
        )
        self.cancel_at_period_end = cancel_at_period_end
        self.cancel_checkout_url = self._define_str(
            "cancel_checkout_url", cancel_checkout_url, nullable=True
        )
        self.canceled_at = self._define_number(
            "canceled_at", canceled_at, nullable=True
        )
        self.complete_checkout_url = self._define_str(
            "complete_checkout_url", complete_checkout_url, nullable=True
        )
        self.complete_payment_url = self._define_str(
            "complete_payment_url", complete_payment_url, nullable=True
        )
        self.country = self._define_str("country", country, nullable=True)
        self.coupon = self._define_str("coupon", coupon, nullable=True)
        self.created_at = self._define_number("created_at", created_at, nullable=True)
        self.current_period_end = self._define_number(
            "current_period_end", current_period_end, nullable=True
        )
        self.current_period_start = self._define_number(
            "current_period_start", current_period_start, nullable=True
        )
        self.custom_elements = self._define_object(
            custom_elements, SubscriptionHostedPageReponseCustomElements
        )
        self.customer = self._define_str("customer", customer, nullable=True)
        self.days_until_due = self._define_number(
            "days_until_due", days_until_due, nullable=True
        )
        self.discount = self._define_object(discount, Discount)
        self.error_payment_url = self._define_str(
            "error_payment_url", error_payment_url, nullable=True
        )
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.language = self._define_str("language", language, nullable=True)
        self.merchant_alias = self._define_str(
            "merchant_alias", merchant_alias, nullable=True
        )
        self.merchant_color = self._define_str(
            "merchant_color", merchant_color, nullable=True
        )
        self.merchant_customer_support = self._define_object(
            merchant_customer_support,
            SubscriptionHostedPageReponseMerchantCustomerSupport,
        )
        self.merchant_main_button = merchant_main_button
        self.merchant_privacy_policy = self._define_str(
            "merchant_privacy_policy", merchant_privacy_policy, nullable=True
        )
        self.merchant_reference_id = self._define_str(
            "merchant_reference_id", merchant_reference_id, nullable=True
        )
        self.merchant_terms = self._define_str(
            "merchant_terms", merchant_terms, nullable=True
        )
        self.merchant_website = self._define_str(
            "merchant_website", merchant_website, nullable=True
        )
        self.metadata = metadata
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.payment = payment
        self.payment_fields = payment_fields
        self.payment_method = self._define_str(
            "payment_method", payment_method, nullable=True
        )
        self.redirect_url = self._define_str(
            "redirect_url", redirect_url, nullable=True
        )
        self.status = (
            self._enum_matching(
                status, SubscriptionHostedPageReponseStatus.list(), "status"
            )
            if status
            else None
        )
        self.subscription_items = self._define_object(
            subscription_items, SubscriptionItems
        )
        self.tax_percent = self._define_number(
            "tax_percent", tax_percent, nullable=True
        )
        self.total_count = self._define_number(
            "total_count", total_count, nullable=True
        )
        self.trial_end = self._define_number("trial_end", trial_end, nullable=True)
        self.trial_from_plan = trial_from_plan
        self.trial_period_days = self._define_number(
            "trial_period_days", trial_period_days, nullable=True
        )
        self.trial_start = self._define_number(
            "trial_start", trial_start, nullable=True
        )
