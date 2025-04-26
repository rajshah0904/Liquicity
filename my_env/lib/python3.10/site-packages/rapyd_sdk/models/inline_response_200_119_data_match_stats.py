from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class InlineResponse200_119DataMatchStats(BaseModel):
    """Statistics about the query.

    :param query_match_count: Number of previous queries to the card network termination database that match elements of this merchant query. Does not indicate a registered match. Mastercard only., defaults to None
    :type query_match_count: float, optional
    :param registered_match_count: Total number of registered matches in the card network termination databases with elements shared with this merchant query., defaults to None
    :type registered_match_count: float, optional
    """

    def __init__(
        self, query_match_count: float = None, registered_match_count: float = None
    ):
        """Statistics about the query.

        :param query_match_count: Number of previous queries to the card network termination database that match elements of this merchant query. Does not indicate a registered match. Mastercard only., defaults to None
        :type query_match_count: float, optional
        :param registered_match_count: Total number of registered matches in the card network termination databases with elements shared with this merchant query., defaults to None
        :type registered_match_count: float, optional
        """
        self.query_match_count = self._define_number(
            "query_match_count", query_match_count, nullable=True
        )
        self.registered_match_count = self._define_number(
            "registered_match_count", registered_match_count, nullable=True
        )
