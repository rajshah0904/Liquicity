from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardDetailsCardTokenBody(BaseModel):
    """CardDetailsCardTokenBody

    :param card_color: The color of the card, specified by one of the following formats: `hexadecimal value`  `CSS color name` `RGB` `RGBA`  `black`, defaults to None
    :type card_color: str, optional
    :param language: Determines the default language of the hosted page. When this parameter is null, the language of the user's browser is used. If the language of the user's browser cannot be determined, the default language is English, defaults to None
    :type language: str, optional
    :param logo: The URL of the logo image that appears on the card. If the logo is not specified, the name of the merchant appears., defaults to None
    :type logo: str, optional
    :param logo_orientation: The orientation of the logo on the card:   `landscape`  `square` `portrait`      Default value: `landscape` , defaults to None
    :type logo_orientation: str, optional
    """

    def __init__(
        self,
        card_color: str = None,
        language: str = None,
        logo: str = None,
        logo_orientation: str = None,
    ):
        """CardDetailsCardTokenBody

        :param card_color: The color of the card, specified by one of the following formats: `hexadecimal value`  `CSS color name` `RGB` `RGBA`  `black`, defaults to None
        :type card_color: str, optional
        :param language: Determines the default language of the hosted page. When this parameter is null, the language of the user's browser is used. If the language of the user's browser cannot be determined, the default language is English, defaults to None
        :type language: str, optional
        :param logo: The URL of the logo image that appears on the card. If the logo is not specified, the name of the merchant appears., defaults to None
        :type logo: str, optional
        :param logo_orientation: The orientation of the logo on the card:   `landscape`  `square` `portrait`      Default value: `landscape` , defaults to None
        :type logo_orientation: str, optional
        """
        self.card_color = self._define_str("card_color", card_color, nullable=True)
        self.language = self._define_str("language", language, nullable=True)
        self.logo = self._define_str("logo", logo, nullable=True)
        self.logo_orientation = self._define_str(
            "logo_orientation", logo_orientation, nullable=True
        )
