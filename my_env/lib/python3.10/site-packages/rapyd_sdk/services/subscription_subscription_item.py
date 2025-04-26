from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    InlineResponse200_15,
    InlineResponse200_16,
    InlineResponse200_17,
    InlineResponse200_18,
    InlineResponse200_19,
    SubscriptionItemIdUsageRecordsBody,
    SubscriptionItemsSubscriptionItemIdBody,
    V1SubscriptionItemsBody,
)


class SubscriptionSubscriptionItemService(BaseService):

    @cast_models
    def list_subscription_item(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        ending_before: float = None,
        limit: float = None,
        starting_after: str = None,
        subscription: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_15:
        """Retrieve a list of all subscription items for a subscription.

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
        :param ending_before: The ID of the subscription item created after the last subscription item you want to retrieve., defaults to None
        :type ending_before: float, optional
        :param limit: The maximum number of subscription items to return. Range 1-100. Default is 10., defaults to None
        :type limit: float, optional
        :param starting_after: The ID of the subscription item created before the first subscription item you want to retrieve., defaults to None
        :type starting_after: str, optional
        :param subscription: ID of the subscription., defaults to None
        :type subscription: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: List of subscriptions
        :rtype: InlineResponse200_15
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(float).is_optional().validate(ending_before)
        Validator(float).is_optional().validate(limit)
        Validator(str).is_optional().validate(starting_after)
        Validator(str).is_optional().validate(subscription)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/subscription_items", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("ending_before", ending_before, explode=False)
            .add_query("limit", limit, explode=False)
            .add_query("starting_after", starting_after, explode=False)
            .add_query("subscription", subscription, explode=False)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_15._unmap(response)

    @cast_models
    def create_subscription_item(
        self,
        request_body: V1SubscriptionItemsBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_16:
        """Create a subscription item and add it to an existing subscription for recurring payment.

        :param request_body: The request body.
        :type request_body: V1SubscriptionItemsBody
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
        :return: The created subscription
        :rtype: InlineResponse200_16
        """

        Validator(V1SubscriptionItemsBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/subscription_items", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_16._unmap(response)

    @cast_models
    def retrieve_subscription_item(
        self,
        subscription_item_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_16:
        """Retrieve the details of a subscription item.

        :param subscription_item_id: ID of the subscription item. String starting with **subi_**.
        :type subscription_item_id: str
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
        :return: The created subscription
        :rtype: InlineResponse200_16
        """

        Validator(str).validate(subscription_item_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/subscription_items/{{subscriptionItemId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionItemId", subscription_item_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_16._unmap(response)

    @cast_models
    def update_subscription_item(
        self,
        request_body: SubscriptionItemsSubscriptionItemIdBody,
        subscription_item_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_16:
        """Change or modify a subscription item.

        :param request_body: The request body.
        :type request_body: SubscriptionItemsSubscriptionItemIdBody
        :param subscription_item_id: ID of the subscription item. String starting with **subi_**.
        :type subscription_item_id: str
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
        :return: The created subscription
        :rtype: InlineResponse200_16
        """

        Validator(SubscriptionItemsSubscriptionItemIdBody).validate(request_body)
        Validator(str).validate(subscription_item_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/subscription_items/{{subscriptionItemId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionItemId", subscription_item_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_16._unmap(response)

    @cast_models
    def delete_subscription_item(
        self,
        subscription_item_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_17:
        """Delete a subscription item from the Rapyd platform.

        :param subscription_item_id: ID of the subscription item. String starting with **subi_**.
        :type subscription_item_id: str
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
        :return: The created subscription
        :rtype: InlineResponse200_17
        """

        Validator(str).validate(subscription_item_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/subscription_items/{{subscriptionItemId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionItemId", subscription_item_id)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_17._unmap(response)

    @cast_models
    def usage_record_summaries(
        self,
        subscription_item_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        limit: float = None,
        ending_before: float = None,
        starting_after: float = None,
        idempotency: str = None,
    ) -> InlineResponse200_18:
        """Retrieve a list of usage records for a subscription item

        :param subscription_item_id: ID of the subscription item. String starting with **subi_**.
        :type subscription_item_id: str
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
        :param limit: The maximum number of usage records that are returned. Range is 1-100. Default is 10., defaults to None
        :type limit: float, optional
        :param ending_before: The latest date and time of the returned usage records. Format is in Unix time., defaults to None
        :type ending_before: float, optional
        :param starting_after: The earliest date and time of the returned usage records. Format is in Unix time., defaults to None
        :type starting_after: float, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The subscription after updated
        :rtype: InlineResponse200_18
        """

        Validator(str).validate(subscription_item_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(float).is_optional().validate(limit)
        Validator(float).is_optional().validate(ending_before)
        Validator(float).is_optional().validate(starting_after)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/subscription_items/{{subscriptionItemId}}/usage_record_summaries",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionItemId", subscription_item_id)
            .add_query("limit", limit)
            .add_query("ending_before", ending_before)
            .add_query("starting_after", starting_after)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_18._unmap(response)

    @cast_models
    def create_subscription_item_usage_record(
        self,
        request_body: SubscriptionItemIdUsageRecordsBody,
        subscription_item_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_19:
        """Create a usage record or update an existing usage record where its unique identifier is composed of timestamp and subscription_item

        :param request_body: The request body.
        :type request_body: SubscriptionItemIdUsageRecordsBody
        :param subscription_item_id: ID of the subscription item. String starting with **subi_**.
        :type subscription_item_id: str
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
        :return: The subscription after updated
        :rtype: InlineResponse200_19
        """

        Validator(SubscriptionItemIdUsageRecordsBody).validate(request_body)
        Validator(str).validate(subscription_item_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/subscription_items/{{subscriptionItemId}}/usage_records",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionItemId", subscription_item_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_19._unmap(response)
