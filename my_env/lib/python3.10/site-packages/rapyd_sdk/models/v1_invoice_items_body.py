from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class V1InvoiceItemsBody(BaseModel):
    """V1InvoiceItemsBody

    :param amount: The amount of the total charge or credit for this item. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015.\<BR\> This is `quantity` times `unit_amount`. A credit is indicated by a negative number., defaults to None
    :type amount: float, optional
    :param currency: Three-letter ISO 4217 code for the currency used in the `amount` field.
    :type currency: str
    :param customer: ID of the customer. String starting with **cus_**.
    :type customer: str
    :param description: Description of the invoice item., defaults to None
    :type description: str, optional
    :param discountable: Determines whether this invoice item is subject to the discount defined in the coupon that is assigned to the customer or subscription.\<BR\> For negative amounts and prorations, the default is **false**, and for all other invoice items, the default is **true**., defaults to None
    :type discountable: bool, optional
    :param invoice: ID of the invoice that this invoice item is assigned to. Relevant when `subscription` is not set., defaults to None
    :type invoice: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param quantity: Indicates the number of units charged as a single invoice item. Integer., defaults to None
    :type quantity: float, optional
    :param subscription: ID of the subscription to assign this invoice item to. By default, the invoice item is assigned to the customer's subscription whose current billing cycle ends first. Relevant when `invoice` is not set., defaults to None
    :type subscription: str, optional
    :param unit_amount: Per-unit price of the product or service, adjusted as defined in the plan. Decimal., defaults to None
    :type unit_amount: float, optional
    """

    def __init__(
        self,
        currency: str,
        customer: str,
        amount: float = None,
        description: str = None,
        discountable: bool = None,
        invoice: str = None,
        metadata: dict = None,
        quantity: float = None,
        subscription: str = None,
        unit_amount: float = None,
    ):
        """V1InvoiceItemsBody

        :param amount: The amount of the total charge or credit for this item. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015.\<BR\> This is `quantity` times `unit_amount`. A credit is indicated by a negative number., defaults to None
        :type amount: float, optional
        :param currency: Three-letter ISO 4217 code for the currency used in the `amount` field.
        :type currency: str
        :param customer: ID of the customer. String starting with **cus_**.
        :type customer: str
        :param description: Description of the invoice item., defaults to None
        :type description: str, optional
        :param discountable: Determines whether this invoice item is subject to the discount defined in the coupon that is assigned to the customer or subscription.\<BR\> For negative amounts and prorations, the default is **false**, and for all other invoice items, the default is **true**., defaults to None
        :type discountable: bool, optional
        :param invoice: ID of the invoice that this invoice item is assigned to. Relevant when `subscription` is not set., defaults to None
        :type invoice: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param quantity: Indicates the number of units charged as a single invoice item. Integer., defaults to None
        :type quantity: float, optional
        :param subscription: ID of the subscription to assign this invoice item to. By default, the invoice item is assigned to the customer's subscription whose current billing cycle ends first. Relevant when `invoice` is not set., defaults to None
        :type subscription: str, optional
        :param unit_amount: Per-unit price of the product or service, adjusted as defined in the plan. Decimal., defaults to None
        :type unit_amount: float, optional
        """
        self.amount = self._define_number("amount", amount, nullable=True)
        self.currency = currency
        self.customer = customer
        self.description = self._define_str("description", description, nullable=True)
        self.discountable = discountable
        self.invoice = self._define_str("invoice", invoice, nullable=True)
        self.metadata = metadata
        self.quantity = self._define_number("quantity", quantity, nullable=True)
        self.subscription = self._define_str(
            "subscription", subscription, nullable=True
        )
        self.unit_amount = self._define_number(
            "unit_amount", unit_amount, nullable=True
        )
