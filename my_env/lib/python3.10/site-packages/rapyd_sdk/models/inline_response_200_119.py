from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .inline_response_200_119_data import InlineResponse200_119Data


@JsonMap({})
class InlineResponse200_119(BaseModel):
    """InlineResponse200_119

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: InlineResponse200_119Data, optional
    """

    def __init__(self, status: Status1 = None, data: InlineResponse200_119Data = None):
        """InlineResponse200_119

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: InlineResponse200_119Data, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(data, InlineResponse200_119Data)
