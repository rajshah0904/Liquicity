from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .inline_response_200_65_data import InlineResponse200_65Data


@JsonMap({})
class InlineResponse200_65(BaseModel):
    """InlineResponse200_65

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: data, defaults to None
    :type data: InlineResponse200_65Data, optional
    """

    def __init__(self, status: Status = None, data: InlineResponse200_65Data = None):
        """InlineResponse200_65

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: data, defaults to None
        :type data: InlineResponse200_65Data, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, InlineResponse200_65Data)
