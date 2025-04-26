from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .subscription_hosted_page_reponse import SubscriptionHostedPageReponse


@JsonMap({})
class InlineResponse200_8(BaseModel):
    """InlineResponse200_8

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: SubscriptionHostedPageReponse, optional
    """

    def __init__(
        self, status: Status1 = None, data: SubscriptionHostedPageReponse = None
    ):
        """InlineResponse200_8

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: SubscriptionHostedPageReponse, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(data, SubscriptionHostedPageReponse)
