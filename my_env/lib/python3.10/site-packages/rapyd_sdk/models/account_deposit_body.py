from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class AccountDepositBody(BaseModel):
    """AccountDepositBody

    :param amount: Amount of the transaction. Decimal.
    :type amount: float
    :param currency: Three-letter ISO 4217 code for the currency used in the `amount` field.
    :type currency: str
    :param ewallet: ID of the Rapyd Wallet. String starting with **ewallet_**.
    :type ewallet: dict
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    """

    def __init__(
        self, amount: float, currency: str, ewallet: dict, metadata: dict = None
    ):
        """AccountDepositBody

        :param amount: Amount of the transaction. Decimal.
        :type amount: float
        :param currency: Three-letter ISO 4217 code for the currency used in the `amount` field.
        :type currency: str
        :param ewallet: ID of the Rapyd Wallet. String starting with **ewallet_**.
        :type ewallet: dict
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        """
        self.amount = amount
        self.currency = currency
        self.ewallet = ewallet
        self.metadata = metadata
