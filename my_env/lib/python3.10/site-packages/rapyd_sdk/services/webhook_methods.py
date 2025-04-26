from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import InlineResponse200_105, InlineResponse200_106


class WebhookMethodsService(BaseService):

    @cast_models
    def get_webhook(
        self,
        webhook: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_105:
        """Retrieve a webhook. Use 'List Webhooks' to find the IDs of webhooks.

        :param webhook: The webhook ID. String starting with **wh_**.
        :type webhook: str
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
        :return: Retrieves webhook
        :rtype: InlineResponse200_105
        """

        Validator(str).validate(webhook)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/webhooks/{{webhook}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("webhook", webhook, explode=True)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_105._unmap(response)

    @cast_models
    def resend_webhook(
        self,
        webhook: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_105:
        """Resend a webhook that was not sent successfully. Use 'List Webhooks' to find the IDs of webhooks. You can resend a webhook that is in status **ERR**.

        :param webhook: The webhook ID. String starting with **wh_**.
        :type webhook: str
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
        :return: Resends webhook
        :rtype: InlineResponse200_105
        """

        Validator(str).validate(webhook)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/webhooks/{{webhook}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("webhook", webhook, explode=True)
            .serialize()
            .set_method("POST")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_105._unmap(response)

    @cast_models
    def list_webhooks(
        self,
        from_created_at: str = None,
        limit: float = None,
        page: str = None,
        status: str = None,
        type_: str = None,
        to_created_at: float = None,
    ) -> InlineResponse200_106:
        """Retrieve a list of all webhooks that were sent. You can filter the list with query parameters.

        :param from_created_at: The earliest date and time when the object was created, in Unix time (seconds)., defaults to None
        :type from_created_at: str, optional
        :param limit: The maximum number of objects to return. Range: 1-1000., defaults to None
        :type limit: float, optional
        :param page: Page number for pagination., defaults to None
        :type page: str, optional
        :param status: Status of the webhook. One of the following: <BR> * **NEW** (new) - The webhook was created and has not yet been sent successfully. <BR> * **CLO** (closed) - The webhook was sent successfully.<BR> * **ERR** (error) - Attempts were made to send the webhook, but the maximum number of retries was  reached. The automatic retry process failed. The webhook was not sent. <BR> * **RET** (retried) - The webhook was resent., defaults to None
        :type status: str, optional
        :param type_: The type of webhook., defaults to None
        :type type_: str, optional
        :param to_created_at: The latest date and time when the object was created, in Unix time (seconds)., defaults to None
        :type to_created_at: float, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Resends webhook
        :rtype: InlineResponse200_106
        """

        Validator(str).is_optional().validate(from_created_at)
        Validator(float).is_optional().validate(limit)
        Validator(str).is_optional().validate(page)
        Validator(str).is_optional().validate(status)
        Validator(str).is_optional().validate(type_)
        Validator(float).is_optional().validate(to_created_at)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/webhooks", self.get_default_headers())
            .add_query("from_created_at", from_created_at)
            .add_query("limit", limit)
            .add_query("page", page)
            .add_query("status", status)
            .add_query("type", type_)
            .add_query("to_created_at", to_created_at)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_106._unmap(response)
