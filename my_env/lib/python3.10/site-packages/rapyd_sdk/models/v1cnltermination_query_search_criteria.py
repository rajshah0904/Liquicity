from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class SearchArea(Enum):
    """An enumeration representing different categories.

    :cvar GLOBAL: "global"
    :vartype GLOBAL: str
    :cvar LOCAL: "local"
    :vartype LOCAL: str
    :cvar REGIONAL: "regional"
    :vartype REGIONAL: str
    """

    GLOBAL = "global"
    LOCAL = "local"
    REGIONAL = "regional"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, SearchArea._member_map_.values()))


@JsonMap({})
class V1cnlterminationQuerySearchCriteria(BaseModel):
    """Specifies search criteria for the query.

    :param search_area: The geographic range of the query. One of the following:\<BR\>* **global** - The query is geographically unlimited.\<BR\>* **local** - The query is limited to the merchant's country.\<BR\>* **regional** - The query is limited to the merchant's region, such as APAC., defaults to None
    :type search_area: SearchArea, optional
    """

    def __init__(self, search_area: SearchArea = None):
        """Specifies search criteria for the query.

        :param search_area: The geographic range of the query. One of the following:\<BR\>* **global** - The query is geographically unlimited.\<BR\>* **local** - The query is limited to the merchant's country.\<BR\>* **regional** - The query is limited to the merchant's region, such as APAC., defaults to None
        :type search_area: SearchArea, optional
        """
        self.search_area = (
            self._enum_matching(search_area, SearchArea.list(), "search_area")
            if search_area
            else None
        )
