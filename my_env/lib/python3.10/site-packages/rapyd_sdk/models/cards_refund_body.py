from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardsRefundBody(BaseModel):
    """CardsRefundBody

    :param amount: The amount of the refund, in units of the `currency` defined in currency. Decimal.
    :type amount: float
    :param authorization_id: ID of the authorization. String starting with **cardauth_**. Use the value of `id` in the response to 'Simulate a Card Transaction Authorization Request - EEA'.
    :type authorization_id: str
    :param card_id: ID of the card. String starting with **card_**.
    :type card_id: str
    :param currency: The refund currency. Three-letter ISO 4217 code.
    :type currency: str
    """

    def __init__(
        self, amount: float, authorization_id: str, card_id: str, currency: str
    ):
        """CardsRefundBody

        :param amount: The amount of the refund, in units of the `currency` defined in currency. Decimal.
        :type amount: float
        :param authorization_id: ID of the authorization. String starting with **cardauth_**. Use the value of `id` in the response to 'Simulate a Card Transaction Authorization Request - EEA'.
        :type authorization_id: str
        :param card_id: ID of the card. String starting with **card_**.
        :type card_id: str
        :param currency: The refund currency. Three-letter ISO 4217 code.
        :type currency: str
        """
        self.amount = amount
        self.authorization_id = authorization_id
        self.card_id = card_id
        self.currency = currency
