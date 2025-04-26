from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .inline_response_200_95_data import InlineResponse200_95Data


@JsonMap({})
class InlineResponse200_95(BaseModel):
    """InlineResponse200_95

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: data, defaults to None
    :type data: InlineResponse200_95Data, optional
    """

    def __init__(self, status: Status = None, data: InlineResponse200_95Data = None):
        """InlineResponse200_95

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: data, defaults to None
        :type data: InlineResponse200_95Data, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, InlineResponse200_95Data)
