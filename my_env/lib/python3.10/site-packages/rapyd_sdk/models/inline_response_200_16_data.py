from __future__ import annotations
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .inline_response_200_16_data_compliance_levels import (
    InlineResponse200_16DataComplianceLevels,
)


@JsonMap({})
class InlineResponse200_16Data(BaseModel):
    """InlineResponse200_16Data

    :param compliance_levels: compliance_levels, defaults to None
    :type compliance_levels: List[InlineResponse200_16DataComplianceLevels], optional
    """

    def __init__(
        self, compliance_levels: List[InlineResponse200_16DataComplianceLevels] = None
    ):
        """InlineResponse200_16Data

        :param compliance_levels: compliance_levels, defaults to None
        :type compliance_levels: List[InlineResponse200_16DataComplianceLevels], optional
        """
        self.compliance_levels = self._define_list(
            compliance_levels, InlineResponse200_16DataComplianceLevels
        )
