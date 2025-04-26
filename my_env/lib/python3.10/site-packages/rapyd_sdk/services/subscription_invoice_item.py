from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    InlineResponse200_24,
    InlineResponse200_25,
    InvoiceItemsInvoiceItemBody,
    V1InvoiceItemsBody,
)


class SubscriptionInvoiceItemService(BaseService):

    @cast_models
    def list_invoice_items(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        created: str = None,
        customer: str = None,
        invoice: str = None,
        limit: str = None,
        ending_before: str = None,
        starting_after: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_24:
        """Retrieve a list of all invoice items. <BR> You can filter the list with query parameters.

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
        :param created: Date of creation of the invoice items., defaults to None
        :type created: str, optional
        :param customer: ID of the customer., defaults to None
        :type customer: str, optional
        :param invoice: ID of the invoice., defaults to None
        :type invoice: str, optional
        :param limit: The maximum number of invoice items to return. Range: 1-100. Default is 10., defaults to None
        :type limit: str, optional
        :param ending_before: The ID of the invoice item created after the last invoice item you want to retrieve., defaults to None
        :type ending_before: str, optional
        :param starting_after: The ID of the invoice item created before the first invoice item you want to retrieve., defaults to None
        :type starting_after: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Invoice items listed successfully
        :rtype: InlineResponse200_24
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(created)
        Validator(str).is_optional().validate(customer)
        Validator(str).is_optional().validate(invoice)
        Validator(str).is_optional().validate(limit)
        Validator(str).is_optional().validate(ending_before)
        Validator(str).is_optional().validate(starting_after)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/invoice_items", self.get_default_headers())
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("created", created, explode=False)
            .add_query("customer", customer, explode=False)
            .add_query("invoice", invoice, explode=False)
            .add_query("limit", limit, explode=False)
            .add_query("ending_before", ending_before, explode=False)
            .add_query("starting_after", starting_after, explode=False)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_24._unmap(response)

    @cast_models
    def create_invoice_item(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: V1InvoiceItemsBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_24:
        """Create an invoice item and add it to an invoice or subscription.<BR>**Note**: If you create an invoice item without specifying the invoice ID or subscription ID, it is attached to the customer’s next invoice that has the same currency.<BR> This method triggers the following webhooks:<BR> * **Invoice Item Created** - This webhook contains the same information as the response. <BR>* Invoice Updated Webhook

        :param request_body: The request body., defaults to None
        :type request_body: V1InvoiceItemsBody, optional
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
        :return: Invoice item created successfully
        :rtype: InlineResponse200_24
        """

        Validator(V1InvoiceItemsBody).is_optional().validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/invoice_items", self.get_default_headers())
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
        return InlineResponse200_24._unmap(response)

    @cast_models
    def get_invoice_item(
        self,
        invoice_item: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_24:
        """Retrieve the details of an invoice item.

        :param invoice_item: Unique access key provided by Rapyd for each authorized user.
        :type invoice_item: str
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
        :return: Invoice item retrieved successfully
        :rtype: InlineResponse200_24
        """

        Validator(str).validate(invoice_item)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoice_items/{{invoiceItem}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceItem", invoice_item)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_24._unmap(response)

    @cast_models
    def update_invoice_item(
        self,
        invoice_item: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: InvoiceItemsInvoiceItemBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_24:
        """Change or modify an invoice item.<BR> You can update an invoice item at any time before the corresponding subscription generates an invoice.<BR> This method triggers the **Invoice Item Updated** webhook. This webhook contains the same information as the response.

        :param request_body: The request body., defaults to None
        :type request_body: InvoiceItemsInvoiceItemBody, optional
        :param invoice_item: Unique access key provided by Rapyd for each authorized user.
        :type invoice_item: str
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
        :return: Invoice item updated successfully
        :rtype: InlineResponse200_24
        """

        Validator(InvoiceItemsInvoiceItemBody).is_optional().validate(request_body)
        Validator(str).validate(invoice_item)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoice_items/{{invoiceItem}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceItem", invoice_item)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_24._unmap(response)

    @cast_models
    def delete_invoice_item(
        self,
        invoice_item: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_25:
        """Delete an invoice item from the upcoming invoice.<BR> Use this method in the following situations:<BR> * The invoice item is attached to an invoice.<BR> * The invoice item is not attached to an invoice.<BR> This method triggers the **Invoice Item Deleted webhook**. This webhook contains the same information as the response.Retrieve the details of an invoice item.

        :param invoice_item: Unique access key provided by Rapyd for each authorized user.
        :type invoice_item: str
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
        :return: Invoice item deleted successfully.
        :rtype: InlineResponse200_25
        """

        Validator(str).validate(invoice_item)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/invoice_items/{{invoiceItem}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("invoiceItem", invoice_item)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_25._unmap(response)
