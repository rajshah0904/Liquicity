from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .add_cardto_google_pay_response import AddCardtoGooglePayResponse


@JsonMap({})
class InlineResponse200_84(BaseModel):
    """InlineResponse200_84

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: AddCardtoGooglePayResponse, optional
    """

    def __init__(self, status: Status1 = None, data: AddCardtoGooglePayResponse = None):
        """InlineResponse200_84

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: AddCardtoGooglePayResponse, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(data, AddCardtoGooglePayResponse)
