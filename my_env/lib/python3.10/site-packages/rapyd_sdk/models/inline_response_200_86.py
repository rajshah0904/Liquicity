from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status_1 import Status1
from .simulate_block_card_response import SimulateBlockCardResponse


@JsonMap({})
class InlineResponse200_86(BaseModel):
    """InlineResponse200_86

    :param status: status, defaults to None
    :type status: Status1, optional
    :param data: data, defaults to None
    :type data: SimulateBlockCardResponse, optional
    """

    def __init__(self, status: Status1 = None, data: SimulateBlockCardResponse = None):
        """InlineResponse200_86

        :param status: status, defaults to None
        :type status: Status1, optional
        :param data: data, defaults to None
        :type data: SimulateBlockCardResponse, optional
        """
        self.status = self._define_object(status, Status1)
        self.data = self._define_object(data, SimulateBlockCardResponse)
