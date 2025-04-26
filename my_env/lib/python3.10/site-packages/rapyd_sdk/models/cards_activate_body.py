from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardsActivateBody(BaseModel):
    """CardsActivateBody

    :param card: The card token, which is a string starting with 'card_'. If the client is PCI-certified, you can use the actual card number.
    :type card: str
    """

    def __init__(self, card: str):
        """CardsActivateBody

        :param card: The card token, which is a string starting with 'card_'. If the client is PCI-certified, you can use the actual card number.
        :type card: str
        """
        self.card = card
