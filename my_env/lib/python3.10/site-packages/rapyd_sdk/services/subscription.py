from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    CheckoutSubscriptionsBody,
    InlineResponse200_20,
    InlineResponse200_5,
    InlineResponse200_6,
    InlineResponse200_7,
    InlineResponse200_8,
    InlineResponse200_9,
    PaymentsSubscriptionsBody,
    SubscriptionsSubscriptionIdBody,
)


class SubscriptionService(BaseService):

    @cast_models
    def get_subscription_list(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        billing: str = None,
        customer: str = None,
        status: str = None,
        product: str = None,
        starting_after: str = None,
        ending_before: str = None,
        limit: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_5:
        """Retrieve a list of subscriptions. You can filter the list with query parameters.

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
        :param billing: Method of billing. One of the following, pay_automatically, send_invoice., defaults to None
        :type billing: str, optional
        :param customer: ID of the customer. String starting with cus_, defaults to None
        :type customer: str, optional
        :param status: Status of the subscription. One of the following, active, canceled, trialing, defaults to None
        :type status: str, optional
        :param product: ID of a 'product' object. The product must have type set to service. String starting with product_. Filter for one product at a time., defaults to None
        :type product: str, optional
        :param starting_after: The ID of a record in the list. The list begins with the record that was created next after the record with this ID. Use this filter to get the next page of results. Relevant when ending_before is not used., defaults to None
        :type starting_after: str, optional
        :param ending_before: The ID of a record in the list. The list ends with the last record that was created before the record with this ID. Use this filter to get the previous page of results., defaults to None
        :type ending_before: str, optional
        :param limit: The maximum number of subscriptions to return. Range, 1-100. Default is 10., defaults to None
        :type limit: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: List of subscriptions,
        :rtype: InlineResponse200_5
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(billing)
        Validator(str).is_optional().validate(customer)
        Validator(str).is_optional().validate(status)
        Validator(str).is_optional().validate(product)
        Validator(str).is_optional().validate(starting_after)
        Validator(str).is_optional().validate(ending_before)
        Validator(str).is_optional().validate(limit)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/subscriptions", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("billing", billing, explode=False)
            .add_query("customer", customer, explode=False)
            .add_query("status", status, explode=False)
            .add_query("product", product, explode=False)
            .add_query("starting_after", starting_after, explode=False)
            .add_query("ending_before", ending_before, explode=False)
            .add_query("limit", limit, explode=False)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_5._unmap(response)

    @cast_models
    def create_subscription(
        self,
        request_body: PaymentsSubscriptionsBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_6:
        """Create a subscription for regular, automatic payments.

        :param request_body: The request body.
        :type request_body: PaymentsSubscriptionsBody
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
        :return: Create a subscription
        :rtype: InlineResponse200_6
        """

        Validator(PaymentsSubscriptionsBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/subscriptions", self.get_default_headers()
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
        return InlineResponse200_6._unmap(response)

    @cast_models
    def get_subscription(
        self,
        subscription_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_6:
        """Retrieve the details of a subscription.

        :param subscription_id: ID of the subscription. String starting with sub_.
        :type subscription_id: str
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
        :return: Get subscription details
        :rtype: InlineResponse200_6
        """

        Validator(str).validate(subscription_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/subscriptions/{{subscriptionId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionId", subscription_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_6._unmap(response)

    @cast_models
    def update_subscription(
        self,
        request_body: SubscriptionsSubscriptionIdBody,
        subscription_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_6:
        """Update the details of a subscription.

        :param request_body: The request body.
        :type request_body: SubscriptionsSubscriptionIdBody
        :param subscription_id: ID of the subscription. String starting with **sub_**.
        :type subscription_id: str
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
        :rtype: InlineResponse200_6
        """

        Validator(SubscriptionsSubscriptionIdBody).validate(request_body)
        Validator(str).validate(subscription_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/subscriptions/{{subscriptionId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionId", subscription_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_6._unmap(response)

    @cast_models
    def cancel_subscription(
        self,
        subscription_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_6:
        """Cancel a subscription.

        :param subscription_id: ID of the subscription. String starting with **sub_**.
        :type subscription_id: str
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
        :return: The canceled subscription
        :rtype: InlineResponse200_6
        """

        Validator(str).validate(subscription_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/subscriptions/{{subscriptionId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionId", subscription_id)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_6._unmap(response)

    @cast_models
    def delete_subscription_discount(
        self,
        subscription_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_7:
        """Delete the discount that was assigned to a subscription. This method does not affect the coupon that the discount was derived from.

        :param subscription_id: ID of the subscription. String starting with **sub_**.
        :type subscription_id: str
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
        :return: discount was deleted
        :rtype: InlineResponse200_7
        """

        Validator(str).validate(subscription_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/subscriptions/{{subscriptionId}}/discount",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("subscriptionId", subscription_id)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_7._unmap(response)

    @cast_models
    def create_subscription_by_hosted_page(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: CheckoutSubscriptionsBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_8:
        """Create a subscription using a hosted page. Relevant to card payments.

        :param request_body: The request body., defaults to None
        :type request_body: CheckoutSubscriptionsBody, optional
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
        :return: Subscription hosted Page was created.
        :rtype: InlineResponse200_8
        """

        Validator(CheckoutSubscriptionsBody).is_optional().validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/checkout/subscriptions", self.get_default_headers()
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
        return InlineResponse200_8._unmap(response)

    @cast_models
    def complete_subscription_cycle(self, subscription_id: str) -> InlineResponse200_9:
        """Cancel the subscription and create an invoice. This method is for testing purposes and runs only in the sandbox.

        :param subscription_id: ID of the subscription. String starting with sub_.
        :type subscription_id: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The subscription
        :rtype: InlineResponse200_9
        """

        Validator(str).validate(subscription_id)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/subscriptions/{{subscriptionId}}/complete_cycle",
                self.get_default_headers(),
            )
            .add_path("subscriptionId", subscription_id)
            .serialize()
            .set_method("POST")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_9._unmap(response)

    @cast_models
    def simulate_start_new_cycle(self, subscription_id: str) -> InlineResponse200_9:
        """End a subscription cycle, create an invoice and move the subscription to the next cycle. This method is for testing purposes and runs only in the sandbox.

        :param subscription_id: ID of the subscription. String starting with sub_.
        :type subscription_id: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Subscription details
        :rtype: InlineResponse200_9
        """

        Validator(str).validate(subscription_id)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/subscriptions/{{subscriptionId}}/start_new_cycle",
                self.get_default_headers(),
            )
            .add_path("subscriptionId", subscription_id)
            .serialize()
            .set_method("POST")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_9._unmap(response)

    @cast_models
    def get_subscription_discount_by_id(
        self,
        discount_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_20:
        """Retrieve a discount for a subscription.

        :param discount_id: discount Id
        :type discount_id: str
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
        :return: Get discount details of a subscription by Discount Id.
        :rtype: InlineResponse200_20
        """

        Validator(str).validate(discount_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/subscriptions/discount/{{discountId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("discountId", discount_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_20._unmap(response)
