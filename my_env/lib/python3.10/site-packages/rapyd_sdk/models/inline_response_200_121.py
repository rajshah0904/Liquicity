from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .list_countries_response import ListCountriesResponse


@JsonMap({})
class InlineResponse200_121(BaseModel):
    """InlineResponse200_121

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: data, defaults to None
    :type data: ListCountriesResponse, optional
    """

    def __init__(self, status: Status = None, data: ListCountriesResponse = None):
        """InlineResponse200_121

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: data, defaults to None
        :type data: ListCountriesResponse, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, ListCountriesResponse)
