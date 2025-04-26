from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .inline_response_200_119_data_query_info_queried_merchant import (
    InlineResponse200_119DataQueryInfoQueriedMerchant,
)


@JsonMap({})
class InlineResponse200_119DataQueryInfo(BaseModel):
    """asd

    :param partner_merchant_reference: ID of the merchant, defined by the partner., defaults to None
    :type partner_merchant_reference: str, optional
    :param partner_query_reference: Unique ID of the query request, defined by the partner., defaults to None
    :type partner_query_reference: str, optional
    :param queried_merchant: Details of the merchant who is the subject of the query., defaults to None
    :type queried_merchant: InlineResponse200_119DataQueryInfoQueriedMerchant, optional
    """

    def __init__(
        self,
        partner_merchant_reference: str = None,
        partner_query_reference: str = None,
        queried_merchant: InlineResponse200_119DataQueryInfoQueriedMerchant = None,
    ):
        """asd

        :param partner_merchant_reference: ID of the merchant, defined by the partner., defaults to None
        :type partner_merchant_reference: str, optional
        :param partner_query_reference: Unique ID of the query request, defined by the partner., defaults to None
        :type partner_query_reference: str, optional
        :param queried_merchant: Details of the merchant who is the subject of the query., defaults to None
        :type queried_merchant: InlineResponse200_119DataQueryInfoQueriedMerchant, optional
        """
        self.partner_merchant_reference = self._define_str(
            "partner_merchant_reference", partner_merchant_reference, nullable=True
        )
        self.partner_query_reference = self._define_str(
            "partner_query_reference", partner_query_reference, nullable=True
        )
        self.queried_merchant = self._define_object(
            queried_merchant, InlineResponse200_119DataQueryInfoQueriedMerchant
        )
