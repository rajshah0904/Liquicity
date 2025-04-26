from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .mass_payout_response import MassPayoutResponse


@JsonMap({})
class InlineResponse200_56(BaseModel):
    """InlineResponse200_56

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: data, defaults to None
    :type data: MassPayoutResponse, optional
    """

    def __init__(self, status: Status = None, data: MassPayoutResponse = None):
        """InlineResponse200_56

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: data, defaults to None
        :type data: MassPayoutResponse, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, MassPayoutResponse)
