from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .customer_payment_method import CustomerPaymentMethod, CustomerPaymentMethodGuard


@JsonMap({})
class InlineResponse200_42(BaseModel):
    """InlineResponse200_42

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: CustomerPaymentMethod, optional
    """

    def __init__(self, status: Status1 = None, data: CustomerPaymentMethod = None):
        """InlineResponse200_42

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: CustomerPaymentMethod, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = CustomerPaymentMethodGuard.return_one_of(data)
