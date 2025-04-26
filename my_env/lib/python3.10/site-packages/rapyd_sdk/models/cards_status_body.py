from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardsStatusBody(BaseModel):
    """CardsStatusBody

    :param blocked_reason: Reason for blocking the card. Relevant when the value of status is block., defaults to None
    :type blocked_reason: str, optional
    :param card: The card token, which is a string starting with **card_**. If the client is PCI-certified, you can use the actual card number.
    :type card: str
    :param status: Status of the card. One of the following, block/unblock
    :type status: str
    """

    def __init__(self, card: str, status: str, blocked_reason: str = None):
        """CardsStatusBody

        :param blocked_reason: Reason for blocking the card. Relevant when the value of status is block., defaults to None
        :type blocked_reason: str, optional
        :param card: The card token, which is a string starting with **card_**. If the client is PCI-certified, you can use the actual card number.
        :type card: str
        :param status: Status of the card. One of the following, block/unblock
        :type status: str
        """
        self.blocked_reason = self._define_str(
            "blocked_reason", blocked_reason, nullable=True
        )
        self.card = card
        self.status = status
