from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .card_transaction import CardTransaction
from .status_1 import Status1


@JsonMap({})
class InlineResponse200_82(BaseModel):
    """InlineResponse200_82

    :param data: data, defaults to None
    :type data: CardTransaction, optional
    :param status: status, defaults to None
    :type status: Status1, optional
    """

    def __init__(self, data: CardTransaction = None, status: Status1 = None):
        """InlineResponse200_82

        :param data: data, defaults to None
        :type data: CardTransaction, optional
        :param status: status, defaults to None
        :type status: Status1, optional
        """
        self.data = self._define_object(data, CardTransaction)
        self.status = self._define_object(status, Status1)
