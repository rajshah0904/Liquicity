from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class SimulateClearingCardTransactionEeaRemoteAuthResponse(BaseModel):
    """Response to a successful remote authorization request. Contains the following fields:

    :param authorization_id: ID of the authorization. String starting with **cardauth_**., defaults to None
    :type authorization_id: str, optional
    :param response_code: Code returned by the client in the response to the remote authorization., defaults to None
    :type response_code: str, optional
    :param auth_code: Authorization code returned by the client in the response to the remote authorization., defaults to None
    :type auth_code: str, optional
    """

    def __init__(
        self,
        authorization_id: str = None,
        response_code: str = None,
        auth_code: str = None,
    ):
        """Response to a successful remote authorization request. Contains the following fields:

        :param authorization_id: ID of the authorization. String starting with **cardauth_**., defaults to None
        :type authorization_id: str, optional
        :param response_code: Code returned by the client in the response to the remote authorization., defaults to None
        :type response_code: str, optional
        :param auth_code: Authorization code returned by the client in the response to the remote authorization., defaults to None
        :type auth_code: str, optional
        """
        self.authorization_id = self._define_str(
            "authorization_id", authorization_id, nullable=True
        )
        self.response_code = self._define_str(
            "response_code", response_code, nullable=True
        )
        self.auth_code = self._define_str("auth_code", auth_code, nullable=True)
