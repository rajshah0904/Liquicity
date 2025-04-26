from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({"id_": "id"})
class InlineResponse200_68Data(BaseModel):
    """InlineResponse200_68Data

    :param account_id: ID of the Rapyd wallet account. UUID., defaults to None
    :type account_id: str, optional
    :param amount: Amount of the transfer, in units of the currency specified in `currency`., defaults to None
    :type amount: float, optional
    :param balance_type: Indicates the type of balance within the Rapyd wallet account., defaults to None
    :type balance_type: str, optional
    :param currency: The currency of the transfer. Three-letter ISO 4217 code., defaults to None
    :type currency: str, optional
    :param id_: ID of the funds transfer transaction. UUID., defaults to None
    :type id_: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: str, optional
    :param phone_number: Phone number of the Rapyd wallet., defaults to None
    :type phone_number: str, optional
    """

    def __init__(
        self,
        account_id: str = None,
        amount: float = None,
        balance_type: str = None,
        currency: str = None,
        id_: str = None,
        metadata: str = None,
        phone_number: str = None,
    ):
        """InlineResponse200_68Data

        :param account_id: ID of the Rapyd wallet account. UUID., defaults to None
        :type account_id: str, optional
        :param amount: Amount of the transfer, in units of the currency specified in `currency`., defaults to None
        :type amount: float, optional
        :param balance_type: Indicates the type of balance within the Rapyd wallet account., defaults to None
        :type balance_type: str, optional
        :param currency: The currency of the transfer. Three-letter ISO 4217 code., defaults to None
        :type currency: str, optional
        :param id_: ID of the funds transfer transaction. UUID., defaults to None
        :type id_: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: str, optional
        :param phone_number: Phone number of the Rapyd wallet., defaults to None
        :type phone_number: str, optional
        """
        self.account_id = self._define_str("account_id", account_id, nullable=True)
        self.amount = self._define_number("amount", amount, nullable=True)
        self.balance_type = self._define_str(
            "balance_type", balance_type, nullable=True
        )
        self.currency = self._define_str("currency", currency, nullable=True)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.metadata = self._define_str("metadata", metadata, nullable=True)
        self.phone_number = self._define_str(
            "phone_number", phone_number, nullable=True
        )
