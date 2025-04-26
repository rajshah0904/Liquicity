from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class BalanceHoldBody(BaseModel):
    """BalanceHoldBody

    :param amount: Amount of the transfer. Decimal.
    :type amount: float
    :param currency: Three-letter ISO 4217 code for the currency used in the `amount` field., defaults to None
    :type currency: str, optional
    :param ewallet: ID of the wallet associated with the contact. String starting with **ewallet_**., defaults to None
    :type ewallet: str, optional
    """

    def __init__(self, amount: float, currency: str = None, ewallet: str = None):
        """BalanceHoldBody

        :param amount: Amount of the transfer. Decimal.
        :type amount: float
        :param currency: Three-letter ISO 4217 code for the currency used in the `amount` field., defaults to None
        :type currency: str, optional
        :param ewallet: ID of the wallet associated with the contact. String starting with **ewallet_**., defaults to None
        :type ewallet: str, optional
        """
        self.amount = amount
        self.currency = self._define_str("currency", currency, nullable=True)
        self.ewallet = self._define_str("ewallet", ewallet, nullable=True)
