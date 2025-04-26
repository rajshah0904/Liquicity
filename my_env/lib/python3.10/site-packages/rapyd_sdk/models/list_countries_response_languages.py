from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({"id_": "id"})
class ListCountriesResponseLanguages(BaseModel):
    """List of the supported countries.

    :param currency_code: Three-letter ISO 4217 code for the currency., defaults to None
    :type currency_code: str, optional
    :param currency_name: Name of the currency in English., defaults to None
    :type currency_name: str, optional
    :param currency_sign: Unicode symbol for the currency., defaults to None
    :type currency_sign: str, optional
    :param id_: ID of the country., defaults to None
    :type id_: str, optional
    :param iso_alpha2: 2-letter ISO 3166-1 alpha-2 code for the country., defaults to None
    :type iso_alpha2: str, optional
    :param iso_alpha3: 3-letter ISO 3166-1 alpha-2 code for the country. Informational only - not relevant to Rapyd API., defaults to None
    :type iso_alpha3: str, optional
    :param name: Name of the country in English., defaults to None
    :type name: str, optional
    :param phone_code: International telephone prefix for the country., defaults to None
    :type phone_code: str, optional
    """

    def __init__(
        self,
        currency_code: str = None,
        currency_name: str = None,
        currency_sign: str = None,
        id_: str = None,
        iso_alpha2: str = None,
        iso_alpha3: str = None,
        name: str = None,
        phone_code: str = None,
    ):
        """List of the supported countries.

        :param currency_code: Three-letter ISO 4217 code for the currency., defaults to None
        :type currency_code: str, optional
        :param currency_name: Name of the currency in English., defaults to None
        :type currency_name: str, optional
        :param currency_sign: Unicode symbol for the currency., defaults to None
        :type currency_sign: str, optional
        :param id_: ID of the country., defaults to None
        :type id_: str, optional
        :param iso_alpha2: 2-letter ISO 3166-1 alpha-2 code for the country., defaults to None
        :type iso_alpha2: str, optional
        :param iso_alpha3: 3-letter ISO 3166-1 alpha-2 code for the country. Informational only - not relevant to Rapyd API., defaults to None
        :type iso_alpha3: str, optional
        :param name: Name of the country in English., defaults to None
        :type name: str, optional
        :param phone_code: International telephone prefix for the country., defaults to None
        :type phone_code: str, optional
        """
        self.currency_code = self._define_str(
            "currency_code", currency_code, nullable=True
        )
        self.currency_name = self._define_str(
            "currency_name", currency_name, nullable=True
        )
        self.currency_sign = self._define_str(
            "currency_sign", currency_sign, nullable=True
        )
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.iso_alpha2 = self._define_str("iso_alpha2", iso_alpha2, nullable=True)
        self.iso_alpha3 = self._define_str("iso_alpha3", iso_alpha3, nullable=True)
        self.name = self._define_str("name", name, nullable=True)
        self.phone_code = self._define_str("phone_code", phone_code, nullable=True)
