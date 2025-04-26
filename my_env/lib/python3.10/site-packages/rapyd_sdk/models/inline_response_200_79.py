from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .hosted_page_activate_card_response import HostedPageActivateCardResponse


@JsonMap({})
class InlineResponse200_79(BaseModel):
    """InlineResponse200_79

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: HostedPageActivateCardResponse, optional
    """

    def __init__(
        self, status: Status1 = None, data: HostedPageActivateCardResponse = None
    ):
        """InlineResponse200_79

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: HostedPageActivateCardResponse, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(data, HostedPageActivateCardResponse)
