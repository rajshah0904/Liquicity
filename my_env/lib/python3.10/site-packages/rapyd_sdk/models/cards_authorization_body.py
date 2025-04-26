from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class FinancialImpact(Enum):
    """An enumeration representing different categories.

    :cvar CREDIT: "credit"
    :vartype CREDIT: str
    :cvar DEBIT: "debit"
    :vartype DEBIT: str
    """

    CREDIT = "credit"
    DEBIT = "debit"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, FinancialImpact._member_map_.values()))


@JsonMap({})
class CardsAuthorizationBody(BaseModel):
    """CardsAuthorizationBody

    :param amount: The amount of the authorization, in units of the `currency` defined in currency. Decimal.
    :type amount: float
    :param card_id: ID of the card. String starting with **card_**.
    :type card_id: str
    :param currency: The currency supported by the card. Three-letter ISO 4217 code.
    :type currency: str
    :param financial_impact: Indicates the financial impact of the transaction.
    :type financial_impact: FinancialImpact
    """

    def __init__(
        self,
        amount: float,
        card_id: str,
        currency: str,
        financial_impact: FinancialImpact,
    ):
        """CardsAuthorizationBody

        :param amount: The amount of the authorization, in units of the `currency` defined in currency. Decimal.
        :type amount: float
        :param card_id: ID of the card. String starting with **card_**.
        :type card_id: str
        :param currency: The currency supported by the card. Three-letter ISO 4217 code.
        :type currency: str
        :param financial_impact: Indicates the financial impact of the transaction.
        :type financial_impact: FinancialImpact
        """
        self.amount = amount
        self.card_id = card_id
        self.currency = currency
        self.financial_impact = self._enum_matching(
            financial_impact, FinancialImpact.list(), "financial_impact"
        )
