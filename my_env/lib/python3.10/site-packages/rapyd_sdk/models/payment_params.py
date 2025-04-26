from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class PaymentParams(BaseModel):
    """PaymentParams

    :param complete_payment_url: URL where the customer is redirected after successfully completing an operation on a hosted page. Does not support localhost URLs., defaults to None
    :type complete_payment_url: str, optional
    :param error_payment_url: URL where the customer is redirected if an error occurs during or after an operation on a hosted page. Does not support localhost URLs., defaults to None
    :type error_payment_url: str, optional
    """

    def __init__(self, complete_payment_url: str = None, error_payment_url: str = None):
        """PaymentParams

        :param complete_payment_url: URL where the customer is redirected after successfully completing an operation on a hosted page. Does not support localhost URLs., defaults to None
        :type complete_payment_url: str, optional
        :param error_payment_url: URL where the customer is redirected if an error occurs during or after an operation on a hosted page. Does not support localhost URLs., defaults to None
        :type error_payment_url: str, optional
        """
        self.complete_payment_url = self._define_str(
            "complete_payment_url", complete_payment_url, nullable=True
        )
        self.error_payment_url = self._define_str(
            "error_payment_url", error_payment_url, nullable=True
        )
