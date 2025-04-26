from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .simulate_clearing_card_transaction_eea import SimulateClearingCardTransactionEea


@JsonMap({})
class InlineResponse200_89(BaseModel):
    """InlineResponse200_89

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: SimulateClearingCardTransactionEea, optional
    """

    def __init__(
        self, status: Status1 = None, data: SimulateClearingCardTransactionEea = None
    ):
        """InlineResponse200_89

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: SimulateClearingCardTransactionEea, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(data, SimulateClearingCardTransactionEea)
