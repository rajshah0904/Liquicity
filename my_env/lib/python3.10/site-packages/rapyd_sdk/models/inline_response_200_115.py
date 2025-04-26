from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .verify_hosted_app_response import VerifyHostedAppResponse


@JsonMap({})
class InlineResponse200_115(BaseModel):
    """InlineResponse200_115

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: VerifyHostedAppResponse, optional
    """

    def __init__(self, status: Status1 = None, data: VerifyHostedAppResponse = None):
        """InlineResponse200_115

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: VerifyHostedAppResponse, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(data, VerifyHostedAppResponse)
