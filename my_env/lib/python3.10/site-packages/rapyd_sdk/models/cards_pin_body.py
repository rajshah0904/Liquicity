from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardsPinBody(BaseModel):
    """CardsPinBody

    :param card: Card number or card ID.
    :type card: str
    :param new_pin: PIN code. Numeric string.
    :type new_pin: str
    """

    def __init__(self, card: str, new_pin: str):
        """CardsPinBody

        :param card: Card number or card ID.
        :type card: str
        :param new_pin: PIN code. Numeric string.
        :type new_pin: str
        """
        self.card = card
        self.new_pin = new_pin
