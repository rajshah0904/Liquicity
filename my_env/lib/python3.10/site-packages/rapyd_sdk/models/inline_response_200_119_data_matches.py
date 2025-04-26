from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class CardNetwork(Enum):
    """An enumeration representing different categories.

    :cvar MASTERCARD: "MASTERCARD"
    :vartype MASTERCARD: str
    :cvar VISA: "VISA"
    :vartype VISA: str
    """

    MASTERCARD = "MASTERCARD"
    VISA = "VISA"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, CardNetwork._member_map_.values()))


@JsonMap({})
class InlineResponse200_119DataMatches(BaseModel):
    """Describes the results of the query.

    :param card_network: Name of the card network termination database with a match., defaults to None
    :type card_network: CardNetwork, optional
    :param exact_match: List of the data points that match this query exactly. Array of strings., defaults to None
    :type exact_match: dict, optional
    :param match_type: Type of match. One of the following:\<BR\>* **query match** - This merchant query matches elements of a previous merchant query in the card network termination database.\<BR\>This means that the queried merchant shares data with a merchant that was previously searched for.\<BR\>* **registered match** - This merchant query matches elements of a merchant termination registration in the card network termination database. This means that an acquirer terminated the contract of a merchant that shares data with the queried merchant., defaults to None
    :type match_type: str, optional
    :param partial_match: List of the data points that partly match the query. Array of strings., defaults to None
    :type partial_match: dict, optional
    """

    def __init__(
        self,
        card_network: CardNetwork = None,
        exact_match: dict = None,
        match_type: str = None,
        partial_match: dict = None,
    ):
        """Describes the results of the query.

        :param card_network: Name of the card network termination database with a match., defaults to None
        :type card_network: CardNetwork, optional
        :param exact_match: List of the data points that match this query exactly. Array of strings., defaults to None
        :type exact_match: dict, optional
        :param match_type: Type of match. One of the following:\<BR\>* **query match** - This merchant query matches elements of a previous merchant query in the card network termination database.\<BR\>This means that the queried merchant shares data with a merchant that was previously searched for.\<BR\>* **registered match** - This merchant query matches elements of a merchant termination registration in the card network termination database. This means that an acquirer terminated the contract of a merchant that shares data with the queried merchant., defaults to None
        :type match_type: str, optional
        :param partial_match: List of the data points that partly match the query. Array of strings., defaults to None
        :type partial_match: dict, optional
        """
        self.card_network = (
            self._enum_matching(card_network, CardNetwork.list(), "card_network")
            if card_network
            else None
        )
        self.exact_match = exact_match
        self.match_type = self._define_str("match_type", match_type, nullable=True)
        self.partial_match = partial_match
