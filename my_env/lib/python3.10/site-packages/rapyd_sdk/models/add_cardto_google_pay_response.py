from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .add_cardto_google_pay_response_user_address import (
    AddCardtoGooglePayResponseUserAddress,
)


@JsonMap(
    {"payment_instrument_data": "PaymentInstrumentData", "user_address": "UserAddress"}
)
class AddCardtoGooglePayResponse(BaseModel):
    """AddCardtoGooglePayResponse

    :param payment_instrument_data: The base64 encoded string that contains the encrypted object for Push Provisioning. Required for adding the card to the Google Pay wallet by using the Google Pay `pushTokenizeRequest` method. For more information refer to the Google Pay Provisioning developer documentation .Details of an account funding transaction (AFT), which transfers funds from a card to a cardholder's wallet., defaults to None
    :type payment_instrument_data: str, optional
    :param user_address: The base64 encoded string that contains the encrypted object for Push Provisioning. Required for adding the card to the Google Pay wallet by using the Google Pay `pushTokenizeRequest` method. For more information refer to the Google Pay Provisioning developer documentation .Details of an account funding transaction (AFT), which transfers funds from a card to a cardholder's wallet., defaults to None
    :type user_address: AddCardtoGooglePayResponseUserAddress, optional
    """

    def __init__(
        self,
        payment_instrument_data: str = None,
        user_address: AddCardtoGooglePayResponseUserAddress = None,
    ):
        """AddCardtoGooglePayResponse

        :param payment_instrument_data: The base64 encoded string that contains the encrypted object for Push Provisioning. Required for adding the card to the Google Pay wallet by using the Google Pay `pushTokenizeRequest` method. For more information refer to the Google Pay Provisioning developer documentation .Details of an account funding transaction (AFT), which transfers funds from a card to a cardholder's wallet., defaults to None
        :type payment_instrument_data: str, optional
        :param user_address: The base64 encoded string that contains the encrypted object for Push Provisioning. Required for adding the card to the Google Pay wallet by using the Google Pay `pushTokenizeRequest` method. For more information refer to the Google Pay Provisioning developer documentation .Details of an account funding transaction (AFT), which transfers funds from a card to a cardholder's wallet., defaults to None
        :type user_address: AddCardtoGooglePayResponseUserAddress, optional
        """
        self.payment_instrument_data = self._define_str(
            "payment_instrument_data", payment_instrument_data, nullable=True
        )
        self.user_address = self._define_object(
            user_address, AddCardtoGooglePayResponseUserAddress
        )
