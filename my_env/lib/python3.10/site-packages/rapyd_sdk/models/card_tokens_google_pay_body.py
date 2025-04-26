from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class CardTokensGooglePayBody(BaseModel):
    """CardTokensGooglePayBody

    :param client_device_id: Stable device identification set by the wallet provider. Could be a computer identifier or an ID tied to hardware such as TEE_ID or SE_ID.
    :type client_device_id: str
    :param client_wallet_provider: The token requester’s Id (TRID).
    :type client_wallet_provider: str
    :param client_wallet_account_id: Client provided consumer ID that identifies the wallet account holder entity.
    :type client_wallet_account_id: str
    """

    def __init__(
        self,
        client_device_id: str,
        client_wallet_provider: str,
        client_wallet_account_id: str,
    ):
        """CardTokensGooglePayBody

        :param client_device_id: Stable device identification set by the wallet provider. Could be a computer identifier or an ID tied to hardware such as TEE_ID or SE_ID.
        :type client_device_id: str
        :param client_wallet_provider: The token requester’s Id (TRID).
        :type client_wallet_provider: str
        :param client_wallet_account_id: Client provided consumer ID that identifies the wallet account holder entity.
        :type client_wallet_account_id: str
        """
        self.client_device_id = client_device_id
        self.client_wallet_provider = client_wallet_provider
        self.client_wallet_account_id = client_wallet_account_id
