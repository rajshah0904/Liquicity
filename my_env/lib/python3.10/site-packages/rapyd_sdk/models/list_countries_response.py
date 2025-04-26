from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .list_countries_response_languages import ListCountriesResponseLanguages


@JsonMap({})
class ListCountriesResponse(BaseModel):
    """ListCountriesResponse

    :param languages: List of the supported countries., defaults to None
    :type languages: ListCountriesResponseLanguages, optional
    """

    def __init__(self, languages: ListCountriesResponseLanguages = None):
        """ListCountriesResponse

        :param languages: List of the supported countries., defaults to None
        :type languages: ListCountriesResponseLanguages, optional
        """
        self.languages = self._define_object(languages, ListCountriesResponseLanguages)
