from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({"type_": "type"})
class BinDetails(BaseModel):
    """Bank Identification Number (BIN) details. Read-only. Object containing the following fields - * bin_number - BIN number * country - The two-letter ISO 3166-1 ALPHA-2 code for the country. Uppercase. * funding - Type of card funding. One of the following [credit, debit, prepaid, unknown] * bank - Name of the issuing bank. Relevant to cards

    :param brand: brand, defaults to None
    :type brand: str, optional
    :param bin_number: bin_number, defaults to None
    :type bin_number: str, optional
    :param type_: type_, defaults to None
    :type type_: str, optional
    :param issuer: issuer, defaults to None
    :type issuer: str, optional
    :param country: country, defaults to None
    :type country: str, optional
    :param level: level, defaults to None
    :type level: str, optional
    """

    def __init__(
        self,
        brand: str = None,
        bin_number: str = None,
        type_: str = None,
        issuer: str = None,
        country: str = None,
        level: str = None,
    ):
        """Bank Identification Number (BIN) details. Read-only. Object containing the following fields - * bin_number - BIN number * country - The two-letter ISO 3166-1 ALPHA-2 code for the country. Uppercase. * funding - Type of card funding. One of the following [credit, debit, prepaid, unknown] * bank - Name of the issuing bank. Relevant to cards

        :param brand: brand, defaults to None
        :type brand: str, optional
        :param bin_number: bin_number, defaults to None
        :type bin_number: str, optional
        :param type_: type_, defaults to None
        :type type_: str, optional
        :param issuer: issuer, defaults to None
        :type issuer: str, optional
        :param country: country, defaults to None
        :type country: str, optional
        :param level: level, defaults to None
        :type level: str, optional
        """
        self.brand = self._define_str("brand", brand, nullable=True)
        self.bin_number = self._define_str("bin_number", bin_number, nullable=True)
        self.type_ = self._define_str("type_", type_, nullable=True)
        self.issuer = self._define_str("issuer", issuer, nullable=True)
        self.country = self._define_str(
            "country",
            country,
            nullable=True,
            pattern="Name of the country. Two-letter ISO 3166-1 alpha-2 code.",
        )
        self.level = self._define_str("level", level, nullable=True)
