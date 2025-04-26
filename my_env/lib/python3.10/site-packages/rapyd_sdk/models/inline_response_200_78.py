from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .card_issuing import CardIssuing
from .status_1 import Status1


@JsonMap({})
class InlineResponse200_78(BaseModel):
    """InlineResponse200_78

    :param data: data, defaults to None
    :type data: CardIssuing, optional
    :param status: status, defaults to None
    :type status: Status1, optional
    """

    def __init__(self, data: CardIssuing = None, status: Status1 = None):
        """InlineResponse200_78

        :param data: data, defaults to None
        :type data: CardIssuing, optional
        :param status: status, defaults to None
        :type status: Status1, optional
        """
        self.data = self._define_object(data, CardIssuing)
        self.status = self._define_object(status, Status1)
