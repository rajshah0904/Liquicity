from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class InlineResponse200_118DataStatus(Enum):
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
                lambda x: x.value, InlineResponse200_118DataStatus._member_map_.values()
            )
        )


@JsonMap({})
class InlineResponse200_118Data(BaseModel):
    """InlineResponse200_118Data

    :param operation_id: ID of the query request operation. UUID., defaults to None
    :type operation_id: str, optional
    :param partner_merchant_reference: ID of the merchant, defined by the partner.., defaults to None
    :type partner_merchant_reference: str, optional
    :param partner_query_reference: Unique ID of the query request, defined by the partner., defaults to None
    :type partner_query_reference: str, optional
    :param status: Status of the Card Network Lookup Service query. One of the following:\<BR\>* **ERROR** - The query failed.\<BR\>* **IN_PROGRESS** - The query is being processed. Results are not available.\<BR\>* **PARTIAL** - The query process is partially complete. Some results are available.\<BR\>* **PROCESSED** - The query process is complete. All results are available.The two-letter ISO 3166-1 ALPHA-2 code for the country of the identification document., defaults to None
    :type status: InlineResponse200_118DataStatus, optional
    """

    def __init__(
        self,
        operation_id: str = None,
        partner_merchant_reference: str = None,
        partner_query_reference: str = None,
        status: InlineResponse200_118DataStatus = None,
    ):
        """InlineResponse200_118Data

        :param operation_id: ID of the query request operation. UUID., defaults to None
        :type operation_id: str, optional
        :param partner_merchant_reference: ID of the merchant, defined by the partner.., defaults to None
        :type partner_merchant_reference: str, optional
        :param partner_query_reference: Unique ID of the query request, defined by the partner., defaults to None
        :type partner_query_reference: str, optional
        :param status: Status of the Card Network Lookup Service query. One of the following:\<BR\>* **ERROR** - The query failed.\<BR\>* **IN_PROGRESS** - The query is being processed. Results are not available.\<BR\>* **PARTIAL** - The query process is partially complete. Some results are available.\<BR\>* **PROCESSED** - The query process is complete. All results are available.The two-letter ISO 3166-1 ALPHA-2 code for the country of the identification document., defaults to None
        :type status: InlineResponse200_118DataStatus, optional
        """
        self.operation_id = self._define_str(
            "operation_id", operation_id, nullable=True
        )
        self.partner_merchant_reference = self._define_str(
            "partner_merchant_reference", partner_merchant_reference, nullable=True
        )
        self.partner_query_reference = self._define_str(
            "partner_query_reference", partner_query_reference, nullable=True
        )
        self.status = (
            self._enum_matching(
                status, InlineResponse200_118DataStatus.list(), "status"
            )
            if status
            else None
        )
