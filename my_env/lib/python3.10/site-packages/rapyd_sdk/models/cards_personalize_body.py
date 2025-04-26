from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardsPersonalizeBody(BaseModel):
    """CardsPersonalizeBody

    :param card: The card token, which is a string starting with **card_**. If the client is PCI-certified, you can use the actual card number.
    :type card: str
    :param ewallet_contact: ID of the wallet contact that the card is issued to. String starting with **cont_**.
    :type ewallet_contact: str
    """

    def __init__(self, card: str, ewallet_contact: str):
        """CardsPersonalizeBody

        :param card: The card token, which is a string starting with **card_**. If the client is PCI-certified, you can use the actual card number.
        :type card: str
        :param ewallet_contact: ID of the wallet contact that the card is issued to. String starting with **cont_**.
        :type ewallet_contact: str
        """
        self.card = card
        self.ewallet_contact = ewallet_contact
