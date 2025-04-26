from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class PaymentIdCaptureBody(BaseModel):
    """PaymentIdCaptureBody

    :param amount: The amount to capture, in units of the currency defined in currency. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015., defaults to None
    :type amount: float, optional
    :param receipt_email: Email address that the receipt for this transaction is sent to., defaults to None
    :type receipt_email: str, optional
    :param statement_descriptor: A text description suitable for a customer's payment statement. Some payment methods truncate this string to a limited number of characters., defaults to None
    :type statement_descriptor: str, optional
    """

    def __init__(
        self,
        amount: float = None,
        receipt_email: str = None,
        statement_descriptor: str = None,
    ):
        """PaymentIdCaptureBody

        :param amount: The amount to capture, in units of the currency defined in currency. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015., defaults to None
        :type amount: float, optional
        :param receipt_email: Email address that the receipt for this transaction is sent to., defaults to None
        :type receipt_email: str, optional
        :param statement_descriptor: A text description suitable for a customer's payment statement. Some payment methods truncate this string to a limited number of characters., defaults to None
        :type statement_descriptor: str, optional
        """
        self.amount = self._define_number("amount", amount, nullable=True)
        self.receipt_email = self._define_str(
            "receipt_email", receipt_email, nullable=True
        )
        self.statement_descriptor = self._define_str(
            "statement_descriptor", statement_descriptor, nullable=True
        )
