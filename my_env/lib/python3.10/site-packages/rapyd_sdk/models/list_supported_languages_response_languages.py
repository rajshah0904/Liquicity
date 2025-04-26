from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class ListSupportedLanguagesResponseLanguages(BaseModel):
    """List of the languages supported for hosted pages.

    :param name: Name of the language in English., defaults to None
    :type name: str, optional
    :param iso_alpha2: ISO 639-1 code for the language. 2 letters, with suffix where relevant., defaults to None
    :type iso_alpha2: str, optional
    """

    def __init__(self, name: str = None, iso_alpha2: str = None):
        """List of the languages supported for hosted pages.

        :param name: Name of the language in English., defaults to None
        :type name: str, optional
        :param iso_alpha2: ISO 639-1 code for the language. 2 letters, with suffix where relevant., defaults to None
        :type iso_alpha2: str, optional
        """
        self.name = self._define_str("name", name, nullable=True)
        self.iso_alpha2 = self._define_str("iso_alpha2", iso_alpha2, nullable=True)
