from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .simulate_card_transaction_authorization_reversal_eea import (
    SimulateCardTransactionAuthorizationReversalEea,
)


@JsonMap({})
class InlineResponse200_88(BaseModel):
    """InlineResponse200_88

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: SimulateCardTransactionAuthorizationReversalEea, optional
    """

    def __init__(
        self,
        status: Status1 = None,
        data: SimulateCardTransactionAuthorizationReversalEea = None,
    ):
        """InlineResponse200_88

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: SimulateCardTransactionAuthorizationReversalEea, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(
            data, SimulateCardTransactionAuthorizationReversalEea
        )
