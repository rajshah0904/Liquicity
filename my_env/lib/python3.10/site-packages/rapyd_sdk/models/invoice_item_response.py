from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .invoice_item_response_period import InvoiceItemResponsePeriod
from .plan import Plan


@JsonMap({"id_": "id", "date_": "date"})
class InvoiceItemResponse(BaseModel):
    """Invoice item

    :param id_: ID of the invoice item. String starting with **ii_**., defaults to None
    :type id_: str, optional
    :param amount: The amount of the total charge or credit for this item. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015.\<BR\> This is `quantity` times `unit_amount`. A credit is indicated by a negative number., defaults to None
    :type amount: float, optional
    :param currency: Three-letter ISO 4217 code for the currency used in the `amount` field., defaults to None
    :type currency: str, optional
    :param customer: ID of the customer. String starting with **cus_**., defaults to None
    :type customer: str, optional
    :param date_: The time of the charge or credit, in Unix time., defaults to None
    :type date_: str, optional
    :param description: item description, defaults to None
    :type description: str, optional
    :param discountable: Determines whether this invoice item is subject to the discount defined in the coupon that is assigned to the customer or subscription., defaults to None
    :type discountable: bool, optional
    :param invoice_item: ID of the invoice item. String starting with **ii_**., defaults to None
    :type invoice_item: str, optional
    :param invoice: ID of the invoice that this invoice item is assigned to. Relevant when `subscription` is not set., defaults to None
    :type invoice: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param period: Defines the start and end of the time period that this invoice item refers to. Relevant when the invoice item refers to more than one day. Contains the following fields:, defaults to None
    :type period: InvoiceItemResponsePeriod, optional
    :param plan: Describes the pricing structure for the invoice item. For details of the fields in the `plan` object, see 'Create Plan'., defaults to None
    :type plan: Plan, optional
    :param proration: Indicates whether the invoice item is prorated., defaults to None
    :type proration: bool, optional
    :param quantity: Indicates the number of units charged as a single invoice item. Integer., defaults to None
    :type quantity: float, optional
    :param subscription: ID of the subscription this invoice item is assigned to. By default, the invoice item is assigned to the customer's subscription whose current billing cycle ends first. Relevant when `invoice` is not set., defaults to None
    :type subscription: str, optional
    :param unit_amount: Per-unit price of the product or service, adjusted as defined in the plan. Decimal., defaults to None
    :type unit_amount: float, optional
    """

    def __init__(
        self,
        id_: str = None,
        amount: float = None,
        currency: str = None,
        customer: str = None,
        date_: str = None,
        description: str = None,
        discountable: bool = None,
        invoice_item: str = None,
        invoice: str = None,
        metadata: dict = None,
        period: InvoiceItemResponsePeriod = None,
        plan: Plan = None,
        proration: bool = None,
        quantity: float = None,
        subscription: str = None,
        unit_amount: float = None,
    ):
        """Invoice item

        :param id_: ID of the invoice item. String starting with **ii_**., defaults to None
        :type id_: str, optional
        :param amount: The amount of the total charge or credit for this item. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015.\<BR\> This is `quantity` times `unit_amount`. A credit is indicated by a negative number., defaults to None
        :type amount: float, optional
        :param currency: Three-letter ISO 4217 code for the currency used in the `amount` field., defaults to None
        :type currency: str, optional
        :param customer: ID of the customer. String starting with **cus_**., defaults to None
        :type customer: str, optional
        :param date_: The time of the charge or credit, in Unix time., defaults to None
        :type date_: str, optional
        :param description: item description, defaults to None
        :type description: str, optional
        :param discountable: Determines whether this invoice item is subject to the discount defined in the coupon that is assigned to the customer or subscription., defaults to None
        :type discountable: bool, optional
        :param invoice_item: ID of the invoice item. String starting with **ii_**., defaults to None
        :type invoice_item: str, optional
        :param invoice: ID of the invoice that this invoice item is assigned to. Relevant when `subscription` is not set., defaults to None
        :type invoice: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param period: Defines the start and end of the time period that this invoice item refers to. Relevant when the invoice item refers to more than one day. Contains the following fields:, defaults to None
        :type period: InvoiceItemResponsePeriod, optional
        :param plan: Describes the pricing structure for the invoice item. For details of the fields in the `plan` object, see 'Create Plan'., defaults to None
        :type plan: Plan, optional
        :param proration: Indicates whether the invoice item is prorated., defaults to None
        :type proration: bool, optional
        :param quantity: Indicates the number of units charged as a single invoice item. Integer., defaults to None
        :type quantity: float, optional
        :param subscription: ID of the subscription this invoice item is assigned to. By default, the invoice item is assigned to the customer's subscription whose current billing cycle ends first. Relevant when `invoice` is not set., defaults to None
        :type subscription: str, optional
        :param unit_amount: Per-unit price of the product or service, adjusted as defined in the plan. Decimal., defaults to None
        :type unit_amount: float, optional
        """
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.amount = self._define_number("amount", amount, nullable=True)
        self.currency = self._define_str("currency", currency, nullable=True)
        self.customer = self._define_str("customer", customer, nullable=True)
        self.date_ = self._define_str("date_", date_, nullable=True)
        self.description = self._define_str("description", description, nullable=True)
        self.discountable = discountable
        self.invoice_item = self._define_str(
            "invoice_item", invoice_item, nullable=True
        )
        self.invoice = self._define_str("invoice", invoice, nullable=True)
        self.metadata = metadata
        self.period = self._define_object(period, InvoiceItemResponsePeriod)
        self.plan = self._define_object(plan, Plan)
        self.proration = proration
        self.quantity = self._define_number("quantity", quantity, nullable=True)
        self.subscription = self._define_str(
            "subscription", subscription, nullable=True
        )
        self.unit_amount = self._define_number(
            "unit_amount", unit_amount, nullable=True
        )
