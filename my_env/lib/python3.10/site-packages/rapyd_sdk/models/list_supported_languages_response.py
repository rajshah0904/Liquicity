from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .list_supported_languages_response_languages import (
    ListSupportedLanguagesResponseLanguages,
)


@JsonMap({})
class ListSupportedLanguagesResponse(BaseModel):
    """ListSupportedLanguagesResponse

    :param languages: List of the languages supported for hosted pages., defaults to None
    :type languages: ListSupportedLanguagesResponseLanguages, optional
    """

    def __init__(self, languages: ListSupportedLanguagesResponseLanguages = None):
        """ListSupportedLanguagesResponse

        :param languages: List of the languages supported for hosted pages., defaults to None
        :type languages: ListSupportedLanguagesResponseLanguages, optional
        """
        self.languages = self._define_object(
            languages, ListSupportedLanguagesResponseLanguages
        )
