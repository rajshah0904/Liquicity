from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .list_currencies_response import ListCurrenciesResponse


@JsonMap({})
class InlineResponse200_122(BaseModel):
    """InlineResponse200_122

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: data, defaults to None
    :type data: ListCurrenciesResponse, optional
    """

    def __init__(self, status: Status = None, data: ListCurrenciesResponse = None):
        """InlineResponse200_122

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: data, defaults to None
        :type data: ListCurrenciesResponse, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, ListCurrenciesResponse)
