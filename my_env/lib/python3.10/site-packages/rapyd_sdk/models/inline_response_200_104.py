from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .daily_rate import DailyRate


@JsonMap({})
class InlineResponse200_104(BaseModel):
    """InlineResponse200_104

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: Describes currency conversion for payments and payouts. Rapyd uses a snapshot of daily foreign exchange rates fetched at 9 PM UTC. The rate returned includes the FX markup fees., defaults to None
    :type data: DailyRate, optional
    """

    def __init__(self, status: Status = None, data: DailyRate = None):
        """InlineResponse200_104

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: Describes currency conversion for payments and payouts. Rapyd uses a snapshot of daily foreign exchange rates fetched at 9 PM UTC. The rate returned includes the FX markup fees., defaults to None
        :type data: DailyRate, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, DailyRate)
