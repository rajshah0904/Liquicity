from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    Customer,
    InlineResponse200_21,
    InlineResponse200_22,
    InlineResponse200_23,
    InvoiceIdPayBody,
    InvoicesInvoiceIdBody,
    V1InvoicesBody,
)


class SubscriptionInvoiceService(BaseService):

    @cast_models
    def list_invoices(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        customer: Customer = None,
        date_: str = None,
        due_date: str = None,
        ending_before: str = None,
        limit: str = None,
        starting_after: str = None,
        subscription: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_21:
        """Retrieve the basic data of an invoice, with individual invoice lines.

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
        :param customer: ID of the customer. String starting with **cus_**., defaults to None
        :type customer: Customer, optional
        :param date_: Date that the invoice was created., defaults to None
        :type date_: str, optional
        :param due_date: The date payment is due on this invoice. This value is calculated from the date the invoice is created, plus the number of days specified in the days_until_due field. Format is in Unix time., defaults to None
        :type due_date: str, optional
        :param ending_before: The ID of the invoice created after the last invoice you want to retrieve. card., defaults to None
        :type ending_before: str, optional
        :param limit: The maximum number of invoices to return. Range 1-100. Default is 10., defaults to None
        :type limit: str, optional
        :param starting_after: The ID of the invoice created before the first invoice you want to retrieve., defaults to None
        :type starting_after: str, optional
        :param subscription: ID of the subscription. String starting with sub_., defaults to None
        :type subscription: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Invoices Fetched successfully
        :rtype: InlineResponse200_21
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(Customer).is_optional().validate(customer)
        Validator(str).is_optional().validate(date_)
        Validator(str).is_optional().validate(due_date)
        Validator(str).is_optional().validate(ending_before)
        Validator(str).is_optional().validate(limit)
        Validator(str).is_optional().validate(starting_after)
        Validator(str).is_optional().validate(subscription)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/invoices", self.get_default_headers())
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("customer", customer)
            .add_query("date", date_)
            .add_query("due_date", due_date)
            .add_query("ending_before", ending_before)
            .add_query("limit", limit)
            .add_query("starting_after", starting_after)
            .add_query("subscription", subscription)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_21._unmap(response)

    @cast_models
    def create_invoice(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: V1InvoicesBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_21:
        """Create an invoice to add a one-time charge to a subscription.<BR>After you create the invoice with this method, create invoice items and assign them to the invoice with Create Invoice Item. <BR> This method triggers the Invoice Created Webhook. This webhook contains the same information as the response. <BR> The following asynchronous webhook provides information about later changes to the Invoice object:Retrieve the basic data of an invoice, with individual invoice lines.<BR> * Invoice Payment Succeeded Webhook <BR>* Invoice Updated Webhook

        :param request_body: The request body., defaults to None
        :type request_body: V1InvoicesBody, optional
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
        :return: Invoice created successfully
        :rtype: InlineResponse200_21
        """

        Validator(V1InvoicesBody).is_optional().validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/invoices", self.get_default_headers())
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
        return InlineResponse200_21._unmap(response)

    @cast_models
    def retrieve_invoice(
        self,
        invoice_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Retrieve the basic data of an invoice, with individual invoice lines.

        :param invoice_id: The ID of the invoice that you want to retrieve.
        :type invoice_id: str
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
        :return: Invoice Fetched successfully
        :rtype: InlineResponse200_22
        """

        Validator(str).validate(invoice_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/{{invoiceId}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceId", invoice_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)

    @cast_models
    def update_invoice(
        self,
        invoice_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: InvoicesInvoiceIdBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Change or modify an invoice. You can modify the invoice when its status is draft.

        :param request_body: The request body., defaults to None
        :type request_body: InvoicesInvoiceIdBody, optional
        :param invoice_id: The ID of the invoice that you want to updated.
        :type invoice_id: str
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
        :return: Invoice updated successfully
        :rtype: InlineResponse200_22
        """

        Validator(InvoicesInvoiceIdBody).is_optional().validate(request_body)
        Validator(str).validate(invoice_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/{{invoiceId}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceId", invoice_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)

    @cast_models
    def delete_invoice(
        self,
        invoice_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_23:
        """Delete an invoice. You can delete an invoice when status is draft.

        :param invoice_id: The ID of the invoice that you want to delete.
        :type invoice_id: str
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
        :return: Invoice deleted successfully
        :rtype: InlineResponse200_23
        """

        Validator(str).validate(invoice_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/{{invoiceId}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceId", invoice_id)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_23._unmap(response)

    @cast_models
    def void_invoice(
        self,
        invoice_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Set an invoice to **void** status. <BR> Void invoices are similar to deleted invoices, but their records are kept for accounting purposes.Retrieve the basic data of an invoice, with individual invoice lines.

        :param invoice_id: The ID of the invoice that you want to void.
        :type invoice_id: str
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
        :return: Invoice successfully set to void
        :rtype: InlineResponse200_22
        """

        Validator(str).validate(invoice_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/{{invoiceId}}/void",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceId", invoice_id)
            .serialize()
            .set_method("POST")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)

    @cast_models
    def finalize_invoice(
        self,
        invoice_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Finalize an invoice.Invoices are initially created with a draft status, and this is the only state in which an invoice can be finalized. When an invoice is ready to be paid, finalize it. This sets its status to open. Subscriptions automatically create draft invoices during each billing cycle, which are then automatically finalized. When an invoice is finalized, it can no longer be deleted and its final status can be one of the following - Paid Uncollectible* Void. An invoice can be finalized only one time.

        :param invoice_id: ID of the invoice you want to pay.
        :type invoice_id: str
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
        :return: Finalized Invoice,
        :rtype: InlineResponse200_22
        """

        Validator(str).validate(invoice_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/{{invoiceId}}/finalize",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceId", invoice_id)
            .serialize()
            .set_method("POST")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)

    @cast_models
    def pay_invoice(
        self,
        invoice_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: InvoiceIdPayBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Make a payment against an invoice.

        :param request_body: The request body., defaults to None
        :type request_body: InvoiceIdPayBody, optional
        :param invoice_id: ID of the invoice you want to pay.
        :type invoice_id: str
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
        :return: The Invoice was paid.
        :rtype: InlineResponse200_22
        """

        Validator(InvoiceIdPayBody).is_optional().validate(request_body)
        Validator(str).validate(invoice_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/{{invoiceId}}/pay",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceId", invoice_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)

    @cast_models
    def mark_invoice_uncollectible(
        self,
        invoice_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Set an invoice to **uncollectible** status. <BR> This status indicates that the invoice cannot be paid by the customer.

        :param invoice_id: ID of the invoice you want to mark uncollectible. String starting with **invoice_**.
        :type invoice_id: str
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
        :return: The Invoice was marked as uncollectible.
        :rtype: InlineResponse200_22
        """

        Validator(str).validate(invoice_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/{{invoiceId}}/mark_uncollectible",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceId", invoice_id)
            .serialize()
            .set_method("POST")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)

    @cast_models
    def get_invoice_lines(
        self,
        invoice_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Retrieve invoice lines from an invoice. <BR>Invoice lines are subscription items or invoice items.

        :param invoice_id: ID of the invoice. String starting with **invoice_**.
        :type invoice_id: str
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
        :return: The invoice lines were retrieved.
        :rtype: InlineResponse200_22
        """

        Validator(str).validate(invoice_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/{{invoiceId}}/lines",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceId", invoice_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)

    @cast_models
    def get_upcoming_invoice(
        self,
        customer: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        currency: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Retrieve a preview of the basic data of the upcoming invoice for a customer, with individual invoice lines.<BR> To get the invoice lines of the invoice, use 'Retrieve Invoice Lines from Invoice'.<BR> The response generated cannot be used to generate a payment authorization.

        :param customer: ID of the customer whose invoice you want to retrieve.
        :type customer: str
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
        :param currency: Three-letter ISO 4217 code for the currency. Required when the invoice is not linked to a specific subscription., defaults to None
        :type currency: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The upcoming invoice was retrieved.
        :rtype: InlineResponse200_22
        """

        Validator(str).validate(customer)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(currency)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/upcoming", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("customer", customer, explode=False)
            .add_query("currency", currency, explode=False)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)

    @cast_models
    def get_invoice_lines_upcoming_invoice(
        self,
        customer: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        currency: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_22:
        """Retrieve invoice lines from the upcoming invoice for a customer. <BR> If a customer has more than one subscription, this method retrieves the invoice lines of the invoice that is due first.<BR> This method is relevant to invoices that are automatically generated out of subscriptions.

        :param customer: ID of the customer whose invoice you want to retrieve.
        :type customer: str
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
        :param currency: Three-letter ISO 4217 code for the currency. Required when the invoice is not linked to a specific subscription., defaults to None
        :type currency: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The lines from the upcoming invoice were retrieved.
        :rtype: InlineResponse200_22
        """

        Validator(str).validate(customer)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(currency)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoices/upcoming/lines",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("customer", customer, explode=False)
            .add_query("currency", currency, explode=False)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_22._unmap(response)
