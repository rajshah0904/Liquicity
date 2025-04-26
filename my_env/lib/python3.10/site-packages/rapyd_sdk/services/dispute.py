from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    GetDisputesListByOrgIdStatus,
    InlineResponse200_34,
    InlineResponse200_35,
)


class DisputeService(BaseService):

    @cast_models
    def get_disputes_list_by_org_id(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        starting_after: str = None,
        ending_before: str = None,
        limit: str = None,
        status: GetDisputesListByOrgIdStatus = None,
        payment: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_34:
        """Retrieve a detailed list of 'dispute' objects.

        :param access_key: Unique access key provided by Rapyd for each authorized user.
        :type access_key: str
        :param content_type: Indicates that the data appears in JSON format. Set to **application/json**.
        :type content_type: str
        :param salt: Random string. Recommended length: 8-16 characters.
        :type salt: str
        :param signature: Signature calculated for each request individually. See [Request Signatures](https://docs.rapyd.net/en/request-signatures.html).
        :type signature: str
        :param timestamp: Timestamp for the request, in Unix time (seconds).
        :type timestamp: str
        :param starting_after: The ID of the dispute created before the first dispute you want to retrieve. String starting with dispute_., defaults to None
        :type starting_after: str, optional
        :param ending_before: The ID of the dispute created after the last dispute you want to retrieve. String starting with dispute_., defaults to None
        :type ending_before: str, optional
        :param limit: The maximum number of disputes to return. Range is 1-100. Default is 10., defaults to None
        :type limit: str, optional
        :param status: Filters the list for disputes with the specified dispute status., defaults to None
        :type status: GetDisputesListByOrgIdStatus, optional
        :param payment: The ID of the payment that is linked to the dispute. String starting with payment_., defaults to None
        :type payment: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: disputes fetched successfully
        :rtype: InlineResponse200_34
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(starting_after)
        Validator(str).is_optional().validate(ending_before)
        Validator(str).is_optional().pattern("([1-9]|[1-9]\d|100)").validate(limit)
        Validator(GetDisputesListByOrgIdStatus).is_optional().validate(status)
        Validator(str).is_optional().validate(payment)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/disputes", self.get_default_headers())
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("starting_after", starting_after)
            .add_query("ending_before", ending_before)
            .add_query("limit", limit)
            .add_query("status", status)
            .add_query("payment", payment)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_34._unmap(response)

    @cast_models
    def get_dispute(
        self,
        dispute_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_35:
        """Retrieve the details of a dispute.

        :param dispute_id: ID of the dispute you want to retrieve. String starting with dispute_.
        :type dispute_id: str
        :param access_key: Unique access key provided by Rapyd for each authorized user.
        :type access_key: str
        :param content_type: Indicates that the data appears in JSON format. Set to **application/json**.
        :type content_type: str
        :param salt: Random string. Recommended length: 8-16 characters.
        :type salt: str
        :param signature: Signature calculated for each request individually. See [Request Signatures](https://docs.rapyd.net/en/request-signatures.html).
        :type signature: str
        :param timestamp: Timestamp for the request, in Unix time (seconds).
        :type timestamp: str
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Get dispute details by dispute ID.
        :rtype: InlineResponse200_35
        """

        Validator(str).validate(dispute_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/disputes/{{disputeId}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("disputeId", dispute_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_35._unmap(response)
