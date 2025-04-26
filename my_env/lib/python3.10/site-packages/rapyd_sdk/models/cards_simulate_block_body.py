from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardsSimulateBlockBody(BaseModel):
    """CardsSimulateBlockBody

    :param blocked_reason: Reason for blocking the card., defaults to None
    :type blocked_reason: str, optional
    :param card_id: ID of the card. String starting with **card_**.
    :type card_id: str
    """

    def __init__(self, card_id: str, blocked_reason: str = None):
        """CardsSimulateBlockBody

        :param blocked_reason: Reason for blocking the card., defaults to None
        :type blocked_reason: str, optional
        :param card_id: ID of the card. String starting with **card_**.
        :type card_id: str
        """
        self.blocked_reason = self._define_str(
            "blocked_reason", blocked_reason, nullable=True
        )
        self.card_id = card_id
