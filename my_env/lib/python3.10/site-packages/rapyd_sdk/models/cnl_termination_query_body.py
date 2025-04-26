from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .v1cnltermination_query_search_criteria import V1cnlterminationQuerySearchCriteria
from .v1cnltermination_query_queried_merchant import (
    V1cnlterminationQueryQueriedMerchant,
)


@JsonMap({})
class CnlTerminationQueryBody(BaseModel):
    """CnlTerminationQueryBody

    :param partner_merchant_reference: ID of the merchant, defined by the partner.\<BR\>Length: 0-60
    :type partner_merchant_reference: str
    :param partner_query_reference: Unique ID of the query request, defined by the partner.\<BR\>Length: 0-60
    :type partner_query_reference: str
    :param search_criteria: Specifies search criteria for the query., defaults to None
    :type search_criteria: V1cnlterminationQuerySearchCriteria, optional
    :param queried_merchant: Information about the merchant who is the subject of the query.
    :type queried_merchant: V1cnlterminationQueryQueriedMerchant
    """

    def __init__(
        self,
        partner_merchant_reference: str,
        partner_query_reference: str,
        queried_merchant: V1cnlterminationQueryQueriedMerchant,
        search_criteria: V1cnlterminationQuerySearchCriteria = None,
    ):
        """CnlTerminationQueryBody

        :param partner_merchant_reference: ID of the merchant, defined by the partner.\<BR\>Length: 0-60
        :type partner_merchant_reference: str
        :param partner_query_reference: Unique ID of the query request, defined by the partner.\<BR\>Length: 0-60
        :type partner_query_reference: str
        :param search_criteria: Specifies search criteria for the query., defaults to None
        :type search_criteria: V1cnlterminationQuerySearchCriteria, optional
        :param queried_merchant: Information about the merchant who is the subject of the query.
        :type queried_merchant: V1cnlterminationQueryQueriedMerchant
        """
        self.partner_merchant_reference = partner_merchant_reference
        self.partner_query_reference = partner_query_reference
        self.search_criteria = self._define_object(
            search_criteria, V1cnlterminationQuerySearchCriteria
        )
        self.queried_merchant = self._define_object(
            queried_merchant, V1cnlterminationQueryQueriedMerchant
        )
