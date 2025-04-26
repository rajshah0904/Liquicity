from __future__ import annotations
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .inline_response_200_16_data_elements import InlineResponse200_16DataElements


@JsonMap({})
class InlineResponse200_16DataComplianceLevels(BaseModel):
    """InlineResponse200_16DataComplianceLevels

    :param level: level, defaults to None
    :type level: float, optional
    :param elements: elements, defaults to None
    :type elements: List[InlineResponse200_16DataElements], optional
    """

    def __init__(
        self,
        level: float = None,
        elements: List[InlineResponse200_16DataElements] = None,
    ):
        """InlineResponse200_16DataComplianceLevels

        :param level: level, defaults to None
        :type level: float, optional
        :param elements: elements, defaults to None
        :type elements: List[InlineResponse200_16DataElements], optional
        """
        self.level = self._define_number("level", level, nullable=True)
        self.elements = self._define_list(elements, InlineResponse200_16DataElements)
