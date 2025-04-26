from __future__ import annotations
from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .inline_response_200_119_data_match_stats import (
    InlineResponse200_119DataMatchStats,
)
from .inline_response_200_119_data_matches import InlineResponse200_119DataMatches
from .inline_response_200_119_data_query_info import InlineResponse200_119DataQueryInfo
from .v1cnltermination_query_search_criteria import V1cnlterminationQuerySearchCriteria
from .inline_response_200_119_data_principals import InlineResponse200_119DataPrincipals
from .inline_response_200_119_data_matched_merchant import (
    InlineResponse200_119DataMatchedMerchant,
)
from .inline_response_200_119_data_registration_info import (
    InlineResponse200_119DataRegistrationInfo,
)


class InlineResponse200_119DataStatus(Enum):
    """An enumeration representing different categories.

    :cvar INPROGRESS: "IN_PROGRESS"
    :vartype INPROGRESS: str
    :cvar ERROR: "ERROR"
    :vartype ERROR: str
    :cvar INPROGRESS1: "IN_PROGRESS"
    :vartype INPROGRESS1: str
    :cvar PARTIAL: "PARTIAL"
    :vartype PARTIAL: str
    :cvar PROCESSED: "PROCESSED"
    :vartype PROCESSED: str
    """

    INPROGRESS = "IN_PROGRESS"
    ERROR = "ERROR"
    INPROGRESS1 = "IN_PROGRESS"
    PARTIAL = "PARTIAL"
    PROCESSED = "PROCESSED"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value, InlineResponse200_119DataStatus._member_map_.values()
            )
        )


@JsonMap({})
class InlineResponse200_119Data(BaseModel):
    """InlineResponse200_119Data

    :param match_stats: Statistics about the query., defaults to None
    :type match_stats: InlineResponse200_119DataMatchStats, optional
    :param matches: Describes the results of the query., defaults to None
    :type matches: InlineResponse200_119DataMatches, optional
    :param query_info: asd, defaults to None
    :type query_info: InlineResponse200_119DataQueryInfo, optional
    :param search_criteria: Specifies search criteria for the query., defaults to None
    :type search_criteria: V1cnlterminationQuerySearchCriteria, optional
    :param principals: Details of the registered principal owners of the merchant.\<BR\> Maximum - 3., defaults to None
    :type principals: InlineResponse200_119DataPrincipals, optional
    :param status: Status of the Card Network Lookup Service query. One of the following:\<BR\>* **ERROR** - The query failed.\<BR\>* **IN_PROGRESS** - The query is being processed. Results are not available.\<BR\>* **PARTIAL** - The query process is partially complete. Some results are available.\<BR\>* **PROCESSED** - The query process is complete. All results are available.The two-letter ISO 3166-1 ALPHA-2 code for the country of the identification document., defaults to None
    :type status: InlineResponse200_119DataStatus, optional
    :param matched_merchant: Data about the merchant on file in the database., defaults to None
    :type matched_merchant: InlineResponse200_119DataMatchedMerchant, optional
    :param registration_info: Registration information in the card network's termination database about the merchant and the acquirer that listed the merchant., defaults to None
    :type registration_info: InlineResponse200_119DataRegistrationInfo, optional
    """

    def __init__(
        self,
        match_stats: InlineResponse200_119DataMatchStats = None,
        matches: InlineResponse200_119DataMatches = None,
        query_info: InlineResponse200_119DataQueryInfo = None,
        search_criteria: V1cnlterminationQuerySearchCriteria = None,
        principals: InlineResponse200_119DataPrincipals = None,
        status: InlineResponse200_119DataStatus = None,
        matched_merchant: InlineResponse200_119DataMatchedMerchant = None,
        registration_info: InlineResponse200_119DataRegistrationInfo = None,
    ):
        """InlineResponse200_119Data

        :param match_stats: Statistics about the query., defaults to None
        :type match_stats: InlineResponse200_119DataMatchStats, optional
        :param matches: Describes the results of the query., defaults to None
        :type matches: InlineResponse200_119DataMatches, optional
        :param query_info: asd, defaults to None
        :type query_info: InlineResponse200_119DataQueryInfo, optional
        :param search_criteria: Specifies search criteria for the query., defaults to None
        :type search_criteria: V1cnlterminationQuerySearchCriteria, optional
        :param principals: Details of the registered principal owners of the merchant.\<BR\> Maximum - 3., defaults to None
        :type principals: InlineResponse200_119DataPrincipals, optional
        :param status: Status of the Card Network Lookup Service query. One of the following:\<BR\>* **ERROR** - The query failed.\<BR\>* **IN_PROGRESS** - The query is being processed. Results are not available.\<BR\>* **PARTIAL** - The query process is partially complete. Some results are available.\<BR\>* **PROCESSED** - The query process is complete. All results are available.The two-letter ISO 3166-1 ALPHA-2 code for the country of the identification document., defaults to None
        :type status: InlineResponse200_119DataStatus, optional
        :param matched_merchant: Data about the merchant on file in the database., defaults to None
        :type matched_merchant: InlineResponse200_119DataMatchedMerchant, optional
        :param registration_info: Registration information in the card network's termination database about the merchant and the acquirer that listed the merchant., defaults to None
        :type registration_info: InlineResponse200_119DataRegistrationInfo, optional
        """
        self.match_stats = self._define_object(
            match_stats, InlineResponse200_119DataMatchStats
        )
        self.matches = self._define_object(matches, InlineResponse200_119DataMatches)
        self.query_info = self._define_object(
            query_info, InlineResponse200_119DataQueryInfo
        )
        self.search_criteria = self._define_object(
            search_criteria, V1cnlterminationQuerySearchCriteria
        )
        self.principals = self._define_object(
            principals, InlineResponse200_119DataPrincipals
        )
        self.status = (
            self._enum_matching(
                status, InlineResponse200_119DataStatus.list(), "status"
            )
            if status
            else None
        )
        self.matched_merchant = self._define_object(
            matched_merchant, InlineResponse200_119DataMatchedMerchant
        )
        self.registration_info = self._define_object(
            registration_info, InlineResponse200_119DataRegistrationInfo
        )
