from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .put_funds_on_hold_response import PutFundsOnHoldResponse


@JsonMap({})
class InlineResponse200_69(BaseModel):
    """InlineResponse200_69

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: data, defaults to None
    :type data: PutFundsOnHoldResponse, optional
    """

    def __init__(self, status: Status = None, data: PutFundsOnHoldResponse = None):
        """InlineResponse200_69

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: data, defaults to None
        :type data: PutFundsOnHoldResponse, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, PutFundsOnHoldResponse)
