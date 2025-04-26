from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .status import Status
from .list_supported_languages_response import ListSupportedLanguagesResponse


@JsonMap({})
class InlineResponse200_120(BaseModel):
    """InlineResponse200_120

    :param status: status, defaults to None
    :type status: Status, optional
    :param data: data, defaults to None
    :type data: ListSupportedLanguagesResponse, optional
    """

    def __init__(
        self, status: Status = None, data: ListSupportedLanguagesResponse = None
    ):
        """InlineResponse200_120

        :param status: status, defaults to None
        :type status: Status, optional
        :param data: data, defaults to None
        :type data: ListSupportedLanguagesResponse, optional
        """
        self.status = self._define_object(status, Status)
        self.data = self._define_object(data, ListSupportedLanguagesResponse)
