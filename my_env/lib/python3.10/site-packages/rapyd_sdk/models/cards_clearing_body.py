from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardsClearingBody(BaseModel):
    """CardsClearingBody

    :param amount: The amount of the authorization, in units of the `currency` defined in currency. Decimal.
    :type amount: float
    :param authorization_id: ID of the authorization. String starting with **cardauth_**. Use the value of `id` in the response to Simulate a Card Transaction Authorization Request - EEA.
    :type authorization_id: str
    :param card_id: ID of the card. String starting with **card_**.
    :type card_id: str
    :param category: Type of charge: **ATM**. Required when `fee_amount` is set., defaults to None
    :type category: str, optional
    :param currency: Defines the currency for the transaction. Three-letter ISO 4217 code.
    :type currency: str
    :param fee_amount: The amount of the fee charged for the transaction, in units of the currency defined in `currency`. Decimal. Required when `category` is set., defaults to None
    :type fee_amount: str, optional
    """

    def __init__(
        self,
        amount: float,
        authorization_id: str,
        card_id: str,
        currency: str,
        category: str = None,
        fee_amount: str = None,
    ):
        """CardsClearingBody

        :param amount: The amount of the authorization, in units of the `currency` defined in currency. Decimal.
        :type amount: float
        :param authorization_id: ID of the authorization. String starting with **cardauth_**. Use the value of `id` in the response to Simulate a Card Transaction Authorization Request - EEA.
        :type authorization_id: str
        :param card_id: ID of the card. String starting with **card_**.
        :type card_id: str
        :param category: Type of charge: **ATM**. Required when `fee_amount` is set., defaults to None
        :type category: str, optional
        :param currency: Defines the currency for the transaction. Three-letter ISO 4217 code.
        :type currency: str
        :param fee_amount: The amount of the fee charged for the transaction, in units of the currency defined in `currency`. Decimal. Required when `category` is set., defaults to None
        :type fee_amount: str, optional
        """
        self.amount = amount
        self.authorization_id = authorization_id
        self.card_id = card_id
        self.category = self._define_str("category", category, nullable=True)
        self.currency = currency
        self.fee_amount = self._define_str("fee_amount", fee_amount, nullable=True)
