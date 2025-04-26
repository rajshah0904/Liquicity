from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .inline_response_200_103_data_bank_accounts import (
    InlineResponse200_103DataBankAccounts,
)


@JsonMap({})
class InlineResponse200_103Data(BaseModel):
    """InlineResponse200_103Data

    :param bank_accounts: Array of objects with details of the virtual accounts. Each object contains the following fields, defaults to None
    :type bank_accounts: InlineResponse200_103DataBankAccounts, optional
    """

    def __init__(self, bank_accounts: InlineResponse200_103DataBankAccounts = None):
        """InlineResponse200_103Data

        :param bank_accounts: Array of objects with details of the virtual accounts. Each object contains the following fields, defaults to None
        :type bank_accounts: InlineResponse200_103DataBankAccounts, optional
        """
        self.bank_accounts = self._define_object(
            bank_accounts, InlineResponse200_103DataBankAccounts
        )
