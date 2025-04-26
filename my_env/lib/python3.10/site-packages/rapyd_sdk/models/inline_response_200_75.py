from __future__ import annotations
from typing import Union
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.one_of_base_model import OneOfBaseModel
from .status_1 import Status1
from .card_issuing import CardIssuing
from .card_issuing_masked import CardIssuingMasked


class InlineResponse200_75DataGuard(OneOfBaseModel):
    class_list = {"CardIssuing": CardIssuing, "CardIssuingMasked": CardIssuingMasked}


InlineResponse200_75Data = Union[CardIssuing, CardIssuingMasked]


@JsonMap({})
class InlineResponse200_75(BaseModel):
    """InlineResponse200_75

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: List[InlineResponse200_75Data], optional
    """

    def __init__(
        self, status: Status1 = None, data: List[InlineResponse200_75Data] = None
    ):
        """InlineResponse200_75

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: List[InlineResponse200_75Data], optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_list(data, InlineResponse200_75Data)
