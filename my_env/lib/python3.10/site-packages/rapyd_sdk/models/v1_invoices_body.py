from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class V1InvoicesBody(BaseModel):
    """V1InvoicesBody

    :param billing: Determines the method of billing at the end of the billing cycle. Set to **pay_automatically** - Rapyd generates a `payment` object, then attempts to pay it using the designated payment method.The number of days until the due date.
    :type billing: float
    :param currency: Three-letter ISO 4217 currency code for the currency used in all fields that refer to a monetary amount. Required when the subscription field is not provided. If subscription field is provided, then the currency defined in the subscription's plan is used., defaults to None
    :type currency: str, optional
    :param customer: ID of the customer that pays this invoice. String starting with **cus_**.
    :type customer: str
    :param days_until_due: The number of days until the due date., defaults to None
    :type days_until_due: float, optional
    :param description: Description of the invoice., defaults to None
    :type description: str, optional
    :param due_date: The date payment is due on this invoice. This value is calculated from the date the invoice is created, plus the number of days specified in the `days_until_due` field. Relevant when `billing` is **send_invoice**.  Format is in Unix time., defaults to None
    :type due_date: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param payment_fields: Object containing additional payment_options fields., defaults to None
    :type payment_fields: dict, optional
    :param payment_method: ID of the payment method for paying the invoice. If not provided, then the payment method is taken from the subscription. If the payment method is not provided in the subscription, the payment method is the customer's default payment method., defaults to None
    :type payment_method: str, optional
    :param statement_descriptor: Description of the invoice for the customer's credit card statement. Limited to 22 characters., defaults to None
    :type statement_descriptor: str, optional
    :param subscription: ID of the subscription that generates charges to this customer. String starting with **sub_**., defaults to None
    :type subscription: str, optional
    :param tax_percent: The tax rate, defined as a percentage., defaults to None
    :type tax_percent: float, optional
    """

    def __init__(
        self,
        billing: float,
        customer: str,
        currency: str = None,
        days_until_due: float = None,
        description: str = None,
        due_date: str = None,
        metadata: dict = None,
        payment_fields: dict = None,
        payment_method: str = None,
        statement_descriptor: str = None,
        subscription: str = None,
        tax_percent: float = None,
    ):
        """V1InvoicesBody

        :param billing: Determines the method of billing at the end of the billing cycle. Set to **pay_automatically** - Rapyd generates a `payment` object, then attempts to pay it using the designated payment method.The number of days until the due date.
        :type billing: float
        :param currency: Three-letter ISO 4217 currency code for the currency used in all fields that refer to a monetary amount. Required when the subscription field is not provided. If subscription field is provided, then the currency defined in the subscription's plan is used., defaults to None
        :type currency: str, optional
        :param customer: ID of the customer that pays this invoice. String starting with **cus_**.
        :type customer: str
        :param days_until_due: The number of days until the due date., defaults to None
        :type days_until_due: float, optional
        :param description: Description of the invoice., defaults to None
        :type description: str, optional
        :param due_date: The date payment is due on this invoice. This value is calculated from the date the invoice is created, plus the number of days specified in the `days_until_due` field. Relevant when `billing` is **send_invoice**.  Format is in Unix time., defaults to None
        :type due_date: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param payment_fields: Object containing additional payment_options fields., defaults to None
        :type payment_fields: dict, optional
        :param payment_method: ID of the payment method for paying the invoice. If not provided, then the payment method is taken from the subscription. If the payment method is not provided in the subscription, the payment method is the customer's default payment method., defaults to None
        :type payment_method: str, optional
        :param statement_descriptor: Description of the invoice for the customer's credit card statement. Limited to 22 characters., defaults to None
        :type statement_descriptor: str, optional
        :param subscription: ID of the subscription that generates charges to this customer. String starting with **sub_**., defaults to None
        :type subscription: str, optional
        :param tax_percent: The tax rate, defined as a percentage., defaults to None
        :type tax_percent: float, optional
        """
        self.billing = billing
        self.currency = self._define_str("currency", currency, nullable=True)
        self.customer = customer
        self.days_until_due = self._define_number(
            "days_until_due", days_until_due, nullable=True
        )
        self.description = self._define_str("description", description, nullable=True)
        self.due_date = self._define_str("due_date", due_date, nullable=True)
        self.metadata = metadata
        self.payment_fields = payment_fields
        self.payment_method = self._define_str(
            "payment_method", payment_method, nullable=True
        )
        self.statement_descriptor = self._define_str(
            "statement_descriptor", statement_descriptor, nullable=True
        )
        self.subscription = self._define_str(
            "subscription", subscription, nullable=True
        )
        self.tax_percent = self._define_number(
            "tax_percent", tax_percent, nullable=True
        )
