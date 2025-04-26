from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .hosted_page_card_pin_response import HostedPageCardPinResponse


@JsonMap({})
class InlineResponse200_80(BaseModel):
    """InlineResponse200_80

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: HostedPageCardPinResponse, optional
    """

    def __init__(self, status: Status1 = None, data: HostedPageCardPinResponse = None):
        """InlineResponse200_80

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: HostedPageCardPinResponse, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(data, HostedPageCardPinResponse)
