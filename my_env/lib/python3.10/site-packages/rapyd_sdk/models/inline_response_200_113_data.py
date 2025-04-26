from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .entity_type_verify import EntityTypeVerify


@JsonMap({})
class InlineResponse200_113Data(BaseModel):
    """InlineResponse200_113Data

    :param application_type: Code for the type of application. String starting with typ_., defaults to None
    :type application_type: str, optional
    :param country: country, defaults to None
    :type country: str, optional
    :param entity_type: entity_type, defaults to None
    :type entity_type: EntityTypeVerify, optional
    """

    def __init__(
        self,
        application_type: str = None,
        country: str = None,
        entity_type: EntityTypeVerify = None,
    ):
        """InlineResponse200_113Data

        :param application_type: Code for the type of application. String starting with typ_., defaults to None
        :type application_type: str, optional
        :param country: country, defaults to None
        :type country: str, optional
        :param entity_type: entity_type, defaults to None
        :type entity_type: EntityTypeVerify, optional
        """
        self.application_type = self._define_str(
            "application_type", application_type, nullable=True
        )
        self.country = self._define_str(
            "country",
            country,
            nullable=True,
            pattern="Name of the country. Two-letter ISO 3166-1 alpha-2 code.",
        )
        self.entity_type = (
            self._enum_matching(entity_type, EntityTypeVerify.list(), "entity_type")
            if entity_type
            else None
        )
