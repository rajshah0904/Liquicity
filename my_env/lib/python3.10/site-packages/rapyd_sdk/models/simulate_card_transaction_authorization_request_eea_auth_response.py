from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class SimulateCardTransactionAuthorizationRequestEeaAuthResponse(BaseModel):
    """Response related to an authorization. Contains the following fields:

    :param code: Indicates success or reason for failure., defaults to None
    :type code: str, optional
    :param message: Descriptive text., defaults to None
    :type message: str, optional
    """

    def __init__(self, code: str = None, message: str = None):
        """Response related to an authorization. Contains the following fields:

        :param code: Indicates success or reason for failure., defaults to None
        :type code: str, optional
        :param message: Descriptive text., defaults to None
        :type message: str, optional
        """
        self.code = self._define_str("code", code, nullable=True)
        self.message = self._define_str("message", message, nullable=True)
