from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .hosted_beneficiary_token_response import HostedBeneficiaryTokenResponse
from .status import Status


@JsonMap({})
class InlineResponse200_60(BaseModel):
    """InlineResponse200_60

    :param data: data, defaults to None
    :type data: HostedBeneficiaryTokenResponse, optional
    :param status: status, defaults to None
    :type status: Status, optional
    """

    def __init__(
        self, data: HostedBeneficiaryTokenResponse = None, status: Status = None
    ):
        """InlineResponse200_60

        :param data: data, defaults to None
        :type data: HostedBeneficiaryTokenResponse, optional
        :param status: status, defaults to None
        :type status: Status, optional
        """
        self.data = self._define_object(data, HostedBeneficiaryTokenResponse)
        self.status = self._define_object(status, Status)
