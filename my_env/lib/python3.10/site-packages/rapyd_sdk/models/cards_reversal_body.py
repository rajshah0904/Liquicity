from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardsReversalBody(BaseModel):
    """CardsReversalBody

    :param amount: The amount of the authorization, in units of the `currency` defined in currency. Decimal., defaults to None
    :type amount: float, optional
    :param authorization_id: ID of the authorization. String starting with **cardauth_**. Use the value of `id` in the response to Simulate a Card Transaction Authorization Request - EEA.
    :type authorization_id: str
    :param card_id: ID of the card. String starting with **card_**.
    :type card_id: str
    :param currency: Defines the currency for the transaction. Three-letter ISO 4217 code.
    :type currency: str
    """

    def __init__(
        self, authorization_id: str, card_id: str, currency: str, amount: float = None
    ):
        """CardsReversalBody

        :param amount: The amount of the authorization, in units of the `currency` defined in currency. Decimal., defaults to None
        :type amount: float, optional
        :param authorization_id: ID of the authorization. String starting with **cardauth_**. Use the value of `id` in the response to Simulate a Card Transaction Authorization Request - EEA.
        :type authorization_id: str
        :param card_id: ID of the card. String starting with **card_**.
        :type card_id: str
        :param currency: Defines the currency for the transaction. Three-letter ISO 4217 code.
        :type currency: str
        """
        self.amount = self._define_number("amount", amount, nullable=True)
        self.authorization_id = authorization_id
        self.card_id = card_id
        self.currency = currency
