from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class InlineResponse200_119DataRegistrationInfo(BaseModel):
    """Registration information in the card network's termination database about the merchant and the acquirer that listed the merchant.

    :param contract_end_date: End date of the merchant's contract with the acquirer., defaults to None
    :type contract_end_date: float, optional
    :param contract_start_date: start date of the merchant's contract with the acquirer., defaults to None
    :type contract_start_date: float, optional
    :param primary_registration_reason: Reason that the merchant's contract with the acquirer was terminated., defaults to None
    :type primary_registration_reason: str, optional
    :param registered_by_acquirer_id: ID of the acquirer that listed the merchant., defaults to None
    :type registered_by_acquirer_id: str, optional
    :param registered_by_acquirer_name: Name of the acquirer that listed the merchant., defaults to None
    :type registered_by_acquirer_name: str, optional
    :param registered_by_acquirer_region: Region of the acquirer that listed the merchant., defaults to None
    :type registered_by_acquirer_region: str, optional
    """

    def __init__(
        self,
        contract_end_date: float = None,
        contract_start_date: float = None,
        primary_registration_reason: str = None,
        registered_by_acquirer_id: str = None,
        registered_by_acquirer_name: str = None,
        registered_by_acquirer_region: str = None,
    ):
        """Registration information in the card network's termination database about the merchant and the acquirer that listed the merchant.

        :param contract_end_date: End date of the merchant's contract with the acquirer., defaults to None
        :type contract_end_date: float, optional
        :param contract_start_date: start date of the merchant's contract with the acquirer., defaults to None
        :type contract_start_date: float, optional
        :param primary_registration_reason: Reason that the merchant's contract with the acquirer was terminated., defaults to None
        :type primary_registration_reason: str, optional
        :param registered_by_acquirer_id: ID of the acquirer that listed the merchant., defaults to None
        :type registered_by_acquirer_id: str, optional
        :param registered_by_acquirer_name: Name of the acquirer that listed the merchant., defaults to None
        :type registered_by_acquirer_name: str, optional
        :param registered_by_acquirer_region: Region of the acquirer that listed the merchant., defaults to None
        :type registered_by_acquirer_region: str, optional
        """
        self.contract_end_date = self._define_number(
            "contract_end_date", contract_end_date, nullable=True
        )
        self.contract_start_date = self._define_number(
            "contract_start_date", contract_start_date, nullable=True
        )
        self.primary_registration_reason = self._define_str(
            "primary_registration_reason", primary_registration_reason, nullable=True
        )
        self.registered_by_acquirer_id = self._define_str(
            "registered_by_acquirer_id", registered_by_acquirer_id, nullable=True
        )
        self.registered_by_acquirer_name = self._define_str(
            "registered_by_acquirer_name", registered_by_acquirer_name, nullable=True
        )
        self.registered_by_acquirer_region = self._define_str(
            "registered_by_acquirer_region",
            registered_by_acquirer_region,
            nullable=True,
        )
