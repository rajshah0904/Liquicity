from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    Customer,
    InlineResponse200_2,
    InlineResponse200_3,
    PaymentIdCaptureBody,
    PaymentsCompletePaymentBody,
    PaymentsPaymentIdBody,
    V1PaymentsBody,
)


class PaymentService(BaseService):

    @cast_models
    def list_payments(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        created_after: str = None,
        created_before: str = None,
        customer: Customer = None,
        destination_card: str = None,
        ending_before: str = None,
        ewallet: str = None,
        group: bool = None,
        invoice: str = None,
        limit: str = None,
        payment_method: str = None,
        order: str = None,
        starting_after: str = None,
        subscription: str = None,
        merchant_reference_id: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_2:
        """Retrieve a list of all payments that you have created. Filter the list with query parameters.

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
        :param created_after: The ID of the payment created before the first payment you want to retrieve. String starting with **payment_**., defaults to None
        :type created_after: str, optional
        :param created_before: The ID of the payment created after the last payment you want to retrieve. String starting with **payment_**., defaults to None
        :type created_before: str, optional
        :param customer: Filters the list for payments related to the specified customer., defaults to None
        :type customer: Customer, optional
        :param destination_card: Filters the list for payments related to the specified destination card., defaults to None
        :type destination_card: str, optional
        :param ending_before: The ID of the payment created after the last payment you want to retrieve. String starting with payment_. Deprecated., defaults to None
        :type ending_before: str, optional
        :param ewallet: Filters the list for payments related to the specified wallet., defaults to None
        :type ewallet: str, optional
        :param group: When true, includes only group payments in the response. When false, excludes group payments from the response. Default is false., defaults to None
        :type group: bool, optional
        :param invoice: Filters according to the invoice. String starting with invoice_., defaults to None
        :type invoice: str, optional
        :param limit: The maximum number of payments to return. Range, 1-100. Default is 10., defaults to None
        :type limit: str, optional
        :param payment_method: Filters the list for payments related to the specified payment method., defaults to None
        :type payment_method: str, optional
        :param order: Filters the list for payments related to the specified order., defaults to None
        :type order: str, optional
        :param starting_after: The ID of a payment in the list. The list begins with the payment that was created next after the payment with this ID. Use this filter to get the next page of results. Relevant when ending_before is not used. String starting with payment_., defaults to None
        :type starting_after: str, optional
        :param subscription: Filters the list for payments related to the specified subscription., defaults to None
        :type subscription: str, optional
        :param merchant_reference_id: Merchant-defined ID., defaults to None
        :type merchant_reference_id: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Payments Fetched successfully
        :rtype: InlineResponse200_2
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(created_after)
        Validator(str).is_optional().validate(created_before)
        Validator(Customer).is_optional().validate(customer)
        Validator(str).is_optional().validate(destination_card)
        Validator(str).is_optional().validate(ending_before)
        Validator(str).is_optional().validate(ewallet)
        Validator(bool).is_optional().validate(group)
        Validator(str).is_optional().validate(invoice)
        Validator(str).is_optional().validate(limit)
        Validator(str).is_optional().validate(payment_method)
        Validator(str).is_optional().validate(order)
        Validator(str).is_optional().validate(starting_after)
        Validator(str).is_optional().validate(subscription)
        Validator(str).is_optional().validate(merchant_reference_id)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/payments", self.get_default_headers())
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("created_after", created_after)
            .add_query("created_before", created_before)
            .add_query("customer", customer)
            .add_query("destination_card", destination_card)
            .add_query("ending_before", ending_before)
            .add_query("ewallet", ewallet)
            .add_query("group", group)
            .add_query("invoice", invoice)
            .add_query("limit", limit)
            .add_query("payment_method", payment_method)
            .add_query("order", order)
            .add_query("starting_after", starting_after)
            .add_query("subscription", subscription)
            .add_query("merchant_reference_id", merchant_reference_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_2._unmap(response)

    @cast_models
    def create_payment(
        self,
        request_body: V1PaymentsBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_3:
        """Create a payment

        :param request_body: The request body.
        :type request_body: V1PaymentsBody
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
        :return: Payment was created
        :rtype: InlineResponse200_3
        """

        Validator(V1PaymentsBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/payments", self.get_default_headers())
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
        return InlineResponse200_3._unmap(response)

    @cast_models
    def retrieve_payment(
        self,
        payment_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_3:
        """Retrieve details of a payment

        :param payment_id: ID of the payment. String starting with **payment_**.
        :type payment_id: str
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
        :return: Payment object
        :rtype: InlineResponse200_3
        """

        Validator(str).validate(payment_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/{{paymentId}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("paymentId", payment_id, explode=True)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_3._unmap(response)

    @cast_models
    def update_payment(
        self,
        request_body: PaymentsPaymentIdBody,
        payment_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_3:
        """Change or modify a payment when the status of the payment is ACT (active). You can update additional fields if they are listed under payment_options in the response from Get Payment Method Required Fields and is_updateable is set to true

        :param request_body: The request body.
        :type request_body: PaymentsPaymentIdBody
        :param payment_id: ID of the payment. String starting with payment_.
        :type payment_id: str
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
        :return: payment updated successfully
        :rtype: InlineResponse200_3
        """

        Validator(PaymentsPaymentIdBody).validate(request_body)
        Validator(str).validate(payment_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/{{paymentId}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("paymentId", payment_id, explode=True)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_3._unmap(response)

    @cast_models
    def cancel_payment(
        self,
        payment_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_3:
        """Cancel a payment where the status of the payment is ACT. Relevant to payment methods where is_cancelable = true in the response to List Payment Methods by Country. This method triggers the Payment Canceled webhook. This webhook contains the same information as the response. NOTE: If the status is CLO, use the Create Refund method.

        :param payment_id: ID of the payment. String starting with payment_.
        :type payment_id: str
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
        :return: payment canceled successfully
        :rtype: InlineResponse200_3
        """

        Validator(str).validate(payment_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/{{paymentId}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("paymentId", payment_id, explode=True)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_3._unmap(response)

    @cast_models
    def capture_payment(
        self,
        payment_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: PaymentIdCaptureBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_3:
        """Capture some or all of a card payment that was previously authorized with `capture` set to **false**.<BR>This method changes the `payment` object status to **CLO** and triggers 'Payment Captured Webhook'. This webhook contains the same information as the response. This method also triggers 'Payment Completed Webhook'. The capture operation is also known as clearing or completion.<BR>The scope of the capture operation depends on the client's pre-authorization permissions. To change these permissions, contact Rapyd Client Support.

        :param request_body: The request body., defaults to None
        :type request_body: PaymentIdCaptureBody, optional
        :param payment_id: ID of the payment. String starting with **payment_**.
        :type payment_id: str
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
        :return: payment captured successfully
        :rtype: InlineResponse200_3
        """

        Validator(PaymentIdCaptureBody).is_optional().validate(request_body)
        Validator(str).validate(payment_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/{{paymentId}}/capture",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("paymentId", payment_id, explode=True)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_3._unmap(response)

    @cast_models
    def complete_payment(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: PaymentsCompletePaymentBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_3:
        """To simulate the completion of a payment by the action of a third party, use this method in the sandbox.<BR> This method changes the payment status to **CLO** (closed), and applies to the **cash**, **bank_redirect**, **bank_transfer**, or **ewallet** payment method types.<BR> This method also returns the 'Payment Completed' Webhook. This webhook contains the same information as the response.<BR> For a card payment:<BR> * Capture after authorization only - Use 'Capture Payment'.<BR> * Simulate 3-D Secure (3DS) verification - See Simulating 3DS Authentication.<BR> **Prerequisites**:<BR> * Create Payment

        :param request_body: The request body., defaults to None
        :type request_body: PaymentsCompletePaymentBody, optional
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
        :return: payment completed successfully
        :rtype: InlineResponse200_3
        """

        Validator(PaymentsCompletePaymentBody).is_optional().validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payments/completePayment",
                self.get_default_headers(),
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
        return InlineResponse200_3._unmap(response)
