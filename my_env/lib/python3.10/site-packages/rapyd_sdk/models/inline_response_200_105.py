from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .resend_webhook_response import ResendWebhookResponse


@JsonMap({})
class InlineResponse200_105(BaseModel):
    """InlineResponse200_105

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: data, defaults to None
    :type data: ResendWebhookResponse, optional
    """

    def __init__(self, status: Status = None, data: ResendWebhookResponse = None):
        """InlineResponse200_105

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: data, defaults to None
        :type data: ResendWebhookResponse, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, ResendWebhookResponse)
