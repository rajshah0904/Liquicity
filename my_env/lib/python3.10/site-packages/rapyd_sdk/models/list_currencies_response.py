from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class ListCurrenciesResponse(BaseModel):
    """ListCurrenciesResponse

    :param code: Three-letter ISO 4217 alphabetic code for the currency., defaults to None
    :type code: str, optional
    :param digits_after_decimal_separator: Number of digits for the minor currency unit., defaults to None
    :type digits_after_decimal_separator: str, optional
    :param name: Name of the currency in English., defaults to None
    :type name: str, optional
    :param numeric_code: ISO 4217 numeric code for the currency., defaults to None
    :type numeric_code: str, optional
    :param symbol: Unicode symbol for the currency. If there is no official Unicode symbol, this field contains the string **undefined**., defaults to None
    :type symbol: str, optional
    """

    def __init__(
        self,
        code: str = None,
        digits_after_decimal_separator: str = None,
        name: str = None,
        numeric_code: str = None,
        symbol: str = None,
    ):
        """ListCurrenciesResponse

        :param code: Three-letter ISO 4217 alphabetic code for the currency., defaults to None
        :type code: str, optional
        :param digits_after_decimal_separator: Number of digits for the minor currency unit., defaults to None
        :type digits_after_decimal_separator: str, optional
        :param name: Name of the currency in English., defaults to None
        :type name: str, optional
        :param numeric_code: ISO 4217 numeric code for the currency., defaults to None
        :type numeric_code: str, optional
        :param symbol: Unicode symbol for the currency. If there is no official Unicode symbol, this field contains the string **undefined**., defaults to None
        :type symbol: str, optional
        """
        self.code = self._define_str("code", code, nullable=True)
        self.digits_after_decimal_separator = self._define_str(
            "digits_after_decimal_separator",
            digits_after_decimal_separator,
            nullable=True,
        )
        self.name = self._define_str("name", name, nullable=True)
        self.numeric_code = self._define_str(
            "numeric_code", numeric_code, nullable=True
        )
        self.symbol = self._define_str("symbol", symbol, nullable=True)
