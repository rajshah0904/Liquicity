from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class PaymentsCompletePaymentBody(BaseModel):
    """PaymentsCompletePaymentBody

    :param token: ID of the payment to complete. String starting with **payment_**., defaults to None
    :type token: str, optional
    :param param1: Depends on the type of payment method. \<BR\> * bank_redirect - **rapyd** \<BR\>* bank_transfer - The value returned in the code field of the `textual_codes` object. You can find this field in the response to the 'Create Payment' request. If the `code` field is empty, `param1` is not required.\<BR\>* cash - Not required.\<BR\>* ewallet - Not required., defaults to None
    :type param1: str, optional
    :param param2: Depends on the type of payment method. \<BR\> * bank_redirect - **success** \<BR\>* bank_transfer -  Original payment amount. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015.\<BR\>* cash - Not required.\<BR\>* ewallet - Not required., defaults to None
    :type param2: str, optional
    """

    def __init__(self, token: str = None, param1: str = None, param2: str = None):
        """PaymentsCompletePaymentBody

        :param token: ID of the payment to complete. String starting with **payment_**., defaults to None
        :type token: str, optional
        :param param1: Depends on the type of payment method. \<BR\> * bank_redirect - **rapyd** \<BR\>* bank_transfer - The value returned in the code field of the `textual_codes` object. You can find this field in the response to the 'Create Payment' request. If the `code` field is empty, `param1` is not required.\<BR\>* cash - Not required.\<BR\>* ewallet - Not required., defaults to None
        :type param1: str, optional
        :param param2: Depends on the type of payment method. \<BR\> * bank_redirect - **success** \<BR\>* bank_transfer -  Original payment amount. Decimal, including the correct number of decimal places for the currency exponent, as defined in ISO 2417:2015.\<BR\>* cash - Not required.\<BR\>* ewallet - Not required., defaults to None
        :type param2: str, optional
        """
        self.token = self._define_str("token", token, nullable=True)
        self.param1 = self._define_str("param1", param1, nullable=True)
        self.param2 = self._define_str("param2", param2, nullable=True)
