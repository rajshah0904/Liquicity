from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    InlineResponse200_90,
    InlineResponse200_91,
    InlineResponse200_92,
    InlineResponse200_93,
    InlineResponse200_94,
    InlineResponse200_95,
    V1VirtualAccountsBody,
    VirtualAccountsTransactionsBody,
    VirtualAccountsVirtualAccountIdBody,
)


class VirtualAccountsService(BaseService):

    @cast_models
    def create_virtual_account(
        self,
        request_body: V1VirtualAccountsBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_90:
        """Issue a virtual account number to an existing wallet.

        :param request_body: The request body.
        :type request_body: V1VirtualAccountsBody
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
        :return: Virtual Accounts
        :rtype: InlineResponse200_90
        """

        Validator(V1VirtualAccountsBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/virtual_accounts", self.get_default_headers()
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
        return InlineResponse200_90._unmap(response)

    @cast_models
    def simulate_bank_transfer_to_virtual_account(
        self,
        request_body: VirtualAccountsTransactionsBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_91:
        """Simulate a deposit to a virtual account number that was issued to a wallet. This method is relevant only for testing in the sandbox. The currency of the transfer must be supported by the specific virtual account. This method triggers the Deposit Completed webhook.

        :param request_body: The request body.
        :type request_body: VirtualAccountsTransactionsBody
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
        :return: Bank transfer details.
        :rtype: InlineResponse200_91
        """

        Validator(VirtualAccountsTransactionsBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/virtual_accounts/transactions",
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
        return InlineResponse200_91._unmap(response)

    @cast_models
    def retrieve_virtual_account(self, virtual_account_id: str) -> InlineResponse200_92:
        """Retrieve a Virtual Account Number object for a wallet.

        :param virtual_account_id: ID of the Virtual Account Number object. String starting with issuing_.
        :type virtual_account_id: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Virtual Accounts
        :rtype: InlineResponse200_92
        """

        Validator(str).validate(virtual_account_id)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/virtual_accounts/{{virtualAccountId}}",
                self.get_default_headers(),
            )
            .add_path("virtualAccountId", virtual_account_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_92._unmap(response)

    @cast_models
    def update_requested_currency(
        self,
        virtual_account_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: VirtualAccountsVirtualAccountIdBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_93:
        """Define, change, or cancel the currency to which funds received by a virtual account are converted.<BR>The status of the virtual account must be **ACT** (active) or **PEN** (pending).<BR>To cancel a previously defined currency conversion, set `requested_currency` to **null**.<BR> Prerequisites:<BR>* Create Wallet<BR>* Verify Identity<BR> * Issue Virtual Account to Wallet

        :param request_body: The request body., defaults to None
        :type request_body: VirtualAccountsVirtualAccountIdBody, optional
        :param virtual_account_id: ID of the Virtual Account Number object. String starting with **issuing_**.
        :type virtual_account_id: str
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
        :return: Returns the requested currency and bank account data.
        :rtype: InlineResponse200_93
        """

        Validator(VirtualAccountsVirtualAccountIdBody).is_optional().validate(
            request_body
        )
        Validator(str).validate(virtual_account_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/virtual_accounts/{{virtualAccountId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("virtualAccountId", virtual_account_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_93._unmap(response)

    @cast_models
    def close_issuing(
        self,
        virtual_account_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_94:
        """Delete a virtual account number of an existing wallet. In order to close a virtual account its status must be ACT.

        :param virtual_account_id: ID of the virtual account. String starting with issuing_.
        :type virtual_account_id: str
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
        :return: Virtual Account
        :rtype: InlineResponse200_94
        """

        Validator(str).validate(virtual_account_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/virtual_accounts/{{virtualAccountId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("virtualAccountId", virtual_account_id)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_94._unmap(response)

    @cast_models
    def capabilities_of_virtual_accounts(
        self,
        country: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_95:
        """Retrieve a list of the capabilities of virtual accounts you can issue to a Rapyd Wallet.<BR> The list is filtered by country.

        :param country: Two-letter ISO 3166-1 ALPHA-2 code of the country.
        :type country: str
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
        :return: Returns capabilities of virtual accounts.
        :rtype: InlineResponse200_95
        """

        Validator(str).validate(country)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/virtual_accounts/capabilities/{{country}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("country", country)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_95._unmap(response)
