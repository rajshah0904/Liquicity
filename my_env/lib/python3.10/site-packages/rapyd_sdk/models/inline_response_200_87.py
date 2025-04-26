from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .simulate_card_transaction_authorization_request_eea import (
    SimulateCardTransactionAuthorizationRequestEea,
)


@JsonMap({})
class InlineResponse200_87(BaseModel):
    """InlineResponse200_87

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: SimulateCardTransactionAuthorizationRequestEea, optional
    """

    def __init__(
        self,
        status: Status1 = None,
        data: SimulateCardTransactionAuthorizationRequestEea = None,
    ):
        """InlineResponse200_87

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: SimulateCardTransactionAuthorizationRequestEea, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(
            data, SimulateCardTransactionAuthorizationRequestEea
        )
