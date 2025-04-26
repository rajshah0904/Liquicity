from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    EscrowEscrowReleasesBody,
    InlineResponse200_28,
    InlineResponse200_29,
)


class EscrowService(BaseService):

    @cast_models
    def list_escrow_releases(
        self,
        payment: str,
        escrow: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_28:
        """Retrieve a list of all releases of funds from a specified escrow.

        :param payment: ID of the payment. String starting with **payment_**.
        :type payment: str
        :param escrow: ID of the escrow. String starting with **escrow_**.
        :type escrow: str
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
        :return: Escrow details after specifying it.
        :rtype: InlineResponse200_28
        """

        Validator(str).validate(payment)
        Validator(str).validate(escrow)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/{{payment}}/escrows/{{escrow}}/escrow_releases",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("payment", payment)
            .add_path("escrow", escrow)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_28._unmap(response)

    @cast_models
    def release_funds_from_escrow(
        self,
        payment: str,
        escrow: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: EscrowEscrowReleasesBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_29:
        """Retrieve a list of all releases of funds from a specified escrow.

        :param request_body: The request body., defaults to None
        :type request_body: EscrowEscrowReleasesBody, optional
        :param payment: ID of the payment. String starting with **payment_**.
        :type payment: str
        :param escrow: ID of the escrow. String starting with **escrow_**.
        :type escrow: str
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
        :return: Escrow details after creating it.
        :rtype: InlineResponse200_29
        """

        Validator(EscrowEscrowReleasesBody).is_optional().validate(request_body)
        Validator(str).validate(payment)
        Validator(str).validate(escrow)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/{{payment}}/escrows/{{escrow}}/escrow_releases",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("payment", payment)
            .add_path("escrow", escrow)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_29._unmap(response)

    @cast_models
    def get_escrow(
        self,
        payment: str,
        escrow: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_28:
        """Retrieve details of the escrow for a payment.

        :param payment: ID of the payment. String starting with **payment_**.
        :type payment: str
        :param escrow: ID of the escrow. String starting with **escrow_**.
        :type escrow: str
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
        :return: Escrow details after specifying it.
        :rtype: InlineResponse200_28
        """

        Validator(str).validate(payment)
        Validator(str).validate(escrow)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/{{payment}}/escrows/{{escrow}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("payment", payment)
            .add_path("escrow", escrow)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_28._unmap(response)
