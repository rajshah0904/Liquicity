from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class InvoiceItemsInvoiceItemBody(BaseModel):
    """InvoiceItemsInvoiceItemBody

    :param days_until_due: Number of days the customer has for paying this invoice. Integer., defaults to None
    :type days_until_due: float, optional
    :param description: Description of the invoice., defaults to None
    :type description: str, optional
    :param due_date: The date payment is due on this invoice. This value is calculated from the date the invoice is created, plus the number of days specified in the `days_until_due` field. Relevant when `billing` is **send_invoice**. Format is in Unix time., defaults to None
    :type due_date: float, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param payment_fields: Additional `payment_options`., defaults to None
    :type payment_fields: dict, optional
    :param statement_descriptor: Description of the invoice for the customer's credit card statement. Limited to 22 characters., defaults to None
    :type statement_descriptor: str, optional
    :param tax_percent: The percentage tax rate that is applied to the subtotal of the invoice, after subtracting all discounts. Decimal, up to four decimal places. Range: 0-100, defaults to None
    :type tax_percent: float, optional
    """

    def __init__(
        self,
        days_until_due: float = None,
        description: str = None,
        due_date: float = None,
        metadata: dict = None,
        payment_fields: dict = None,
        statement_descriptor: str = None,
        tax_percent: float = None,
    ):
        """InvoiceItemsInvoiceItemBody

        :param days_until_due: Number of days the customer has for paying this invoice. Integer., defaults to None
        :type days_until_due: float, optional
        :param description: Description of the invoice., defaults to None
        :type description: str, optional
        :param due_date: The date payment is due on this invoice. This value is calculated from the date the invoice is created, plus the number of days specified in the `days_until_due` field. Relevant when `billing` is **send_invoice**. Format is in Unix time., defaults to None
        :type due_date: float, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param payment_fields: Additional `payment_options`., defaults to None
        :type payment_fields: dict, optional
        :param statement_descriptor: Description of the invoice for the customer's credit card statement. Limited to 22 characters., defaults to None
        :type statement_descriptor: str, optional
        :param tax_percent: The percentage tax rate that is applied to the subtotal of the invoice, after subtracting all discounts. Decimal, up to four decimal places. Range: 0-100, defaults to None
        :type tax_percent: float, optional
        """
        self.days_until_due = self._define_number(
            "days_until_due", days_until_due, nullable=True
        )
        self.description = self._define_str("description", description, nullable=True)
        self.due_date = self._define_number("due_date", due_date, nullable=True)
        self.metadata = metadata
        self.payment_fields = payment_fields
        self.statement_descriptor = self._define_str(
            "statement_descriptor", statement_descriptor, nullable=True
        )
        self.tax_percent = self._define_number(
            "tax_percent", tax_percent, nullable=True
        )
