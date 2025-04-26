from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class IssuingCardsBody(BaseModel):
    """IssuingCardsBody

    :param card_program: ID of the card program that the card is issued from. String starting with **cardprog_**.
    :type card_program: str
    :param country: Two-letter ISO 3166-1 ALPHA-2 code for the country., defaults to None
    :type country: str, optional
    :param ewallet_contact: ID of the wallet contact that the card is assigned to. String starting with **cont_**.
    :type ewallet_contact: str
    :param expiration_month: Expiration month of the card., defaults to None
    :type expiration_month: str, optional
    :param expiration_year: Expiration year of the card., defaults to None
    :type expiration_year: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    """

    def __init__(
        self,
        card_program: str,
        ewallet_contact: str,
        country: str = None,
        expiration_month: str = None,
        expiration_year: str = None,
        metadata: dict = None,
    ):
        """IssuingCardsBody

        :param card_program: ID of the card program that the card is issued from. String starting with **cardprog_**.
        :type card_program: str
        :param country: Two-letter ISO 3166-1 ALPHA-2 code for the country., defaults to None
        :type country: str, optional
        :param ewallet_contact: ID of the wallet contact that the card is assigned to. String starting with **cont_**.
        :type ewallet_contact: str
        :param expiration_month: Expiration month of the card., defaults to None
        :type expiration_month: str, optional
        :param expiration_year: Expiration year of the card., defaults to None
        :type expiration_year: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        """
        self.card_program = card_program
        self.country = self._define_str("country", country, nullable=True)
        self.ewallet_contact = ewallet_contact
        self.expiration_month = self._define_str(
            "expiration_month", expiration_month, nullable=True
        )
        self.expiration_year = self._define_str(
            "expiration_year", expiration_year, nullable=True
        )
        self.metadata = metadata
