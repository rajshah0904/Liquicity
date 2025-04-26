from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    AccountDepositBody,
    AccountLimitsBody,
    AccountTransferBody,
    AccountWithdrawBody,
    BalanceHoldBody,
    Contact,
    EwalletIdContactsBody,
    EwalletsEwalletTokenBody,
    InlineResponse200_100,
    InlineResponse200_101,
    InlineResponse200_102,
    InlineResponse200_103,
    InlineResponse200_66,
    InlineResponse200_67,
    InlineResponse200_68,
    InlineResponse200_69,
    InlineResponse200_70,
    InlineResponse200_71,
    InlineResponse200_72,
    InlineResponse200_73,
    InlineResponse200_97,
    InlineResponse200_98,
    InlineResponse200_99,
    TransferResponseBody,
    UpdateEwalletStatusStatus,
    V1EwalletsBody,
)


class EWalletsService(BaseService):

    @cast_models
    def funds_transfer(
        self,
        request_body: AccountTransferBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_67:
        """Transfer funds between Rapyd Wallets.

        :param request_body: The request body.
        :type request_body: AccountTransferBody
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
        :return: Transacton properties
        :rtype: InlineResponse200_67
        """

        Validator(AccountTransferBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/account/transfer", self.get_default_headers()
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
        return InlineResponse200_67._unmap(response)

    @cast_models
    def set_funds_transfer_response(
        self,
        request_body: TransferResponseBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_67:
        """Respond to a funds transfer between wallets. The transferee uses this method to accept or decline the transfer.

        :param request_body: The request body.
        :type request_body: TransferResponseBody
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
        :return: Transaction properties
        :rtype: InlineResponse200_67
        """

        Validator(TransferResponseBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/account/transfer/response",
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
        return InlineResponse200_67._unmap(response)

    @cast_models
    def add_funds_to_wallet_account(
        self,
        request_body: AccountDepositBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_68:
        """Transfer virtual currency to a Rapyd Wallet account.<BR>If the account does not already exist for the indicated currency, it is created.<BR>Use this method in the sandbox for testing purposes.<BR>This method triggers the 'Funds Added Webhook'.

        :param request_body: The request body.
        :type request_body: AccountDepositBody
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
        :return: Returns details on the funds that were added to the account.
        :rtype: InlineResponse200_68
        """

        Validator(AccountDepositBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/account/deposit", self.get_default_headers()
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
        return InlineResponse200_68._unmap(response)

    @cast_models
    def details_of_add_fundsto_wallet_account(
        self,
        id_: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_68:
        """Retrieve details of a specific 'Add Funds to Wallet Account' request.<BR> Use this method in the sandbox for testing purposes.

        :param id_: ID of the 'Add Funds to Wallet Account' request, from the `id` field in the data object of the response. UUID.
        :type id_: str
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
        :return: Returns details of an 'Add Funds' Request.
        :rtype: InlineResponse200_68
        """

        Validator(str).validate(id_)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/account/deposit/{{id}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("id", id_)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_68._unmap(response)

    @cast_models
    def withdraw_funds_from_wallet_account(
        self,
        request_body: AccountWithdrawBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_68:
        """Remove virtual currency from a Rapyd Wallet account.<BR>If the account does not have sufficient funds in the indicated currency, the funds transfer fails.<BR>Use this method in the sandbox for testing purposes.<BR>This method triggers the 'Funds Removed' Webhook

        :param request_body: The request body.
        :type request_body: AccountWithdrawBody
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
        :return: Returns details on the funds that were removed from the account.
        :rtype: InlineResponse200_68
        """

        Validator(AccountWithdrawBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/account/withdraw", self.get_default_headers()
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
        return InlineResponse200_68._unmap(response)

    @cast_models
    def get_details_of_remove_funds_request(
        self,
        id_: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_68:
        """Retrieve details of a specific 'Remove Funds From Wallet Account' request.<BR>Use this method in the sandbox for testing purposes.

        :param id_: ID of the 'Remove Funds From Wallet Account' request, from the `id` field in the `data` object of the response. UUID.
        :type id_: str
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
        :return: Returns details on the funds that were removed from the account via a specific request.
        :rtype: InlineResponse200_68
        """

        Validator(str).validate(id_)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/account/withdraw{{id}}", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("id", id_)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_68._unmap(response)

    @cast_models
    def put_funds_on_hold(
        self,
        request_body: BalanceHoldBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_69:
        """Put a hold on funds in the wallet. Sandbox only.<BR> This action transfers funds from the available balance to the on-hold balance. If the wallet does not have enough funds in the available balance in the specified currency, the transfer fails.<BR>This method triggers the **Transfer Funds Between Balances** webhook. This webhook contains the same information as the response.<BR>The customer cannot move funds that are on hold until the client releases the hold.<BR>This method is relevant for **person** and **company** wallets.

        :param request_body: The request body.
        :type request_body: BalanceHoldBody
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
        :return: Funds put on hold.
        :rtype: InlineResponse200_69
        """

        Validator(BalanceHoldBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/accounts/balance/hold",
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
        return InlineResponse200_69._unmap(response)

    @cast_models
    def get_ewallet_contacts(
        self,
        ewallet_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_70:
        """Retrieve all contacts for a wallet.

        :param ewallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type ewallet_id: str
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
        :return: List Contacts for a Rapyd Wallet,
        :rtype: InlineResponse200_70
        """

        Validator(str).validate(ewallet_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletId}}/contacts",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletId", ewallet_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_70._unmap(response)

    @cast_models
    def create_ewallet_contact(
        self,
        request_body: EwalletIdContactsBody,
        ewallet_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_71:
        """Add a personal contact to a company wallet or client wallet.

        :param request_body: The request body.
        :type request_body: EwalletIdContactsBody
        :param ewallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type ewallet_id: str
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
        :return: List Contacts for a Rapyd Wallet,
        :rtype: InlineResponse200_71
        """

        Validator(EwalletIdContactsBody).validate(request_body)
        Validator(str).validate(ewallet_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletId}}/contacts",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletId", ewallet_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_71._unmap(response)

    @cast_models
    def get_ewallet_contact(
        self,
        ewallet_id: str,
        contact_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_71:
        """Retrieve a contact for an existing Rapyd Wallet.

        :param ewallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type ewallet_id: str
        :param contact_id: One of two values. either ID of the contact - String starting with the prefix **cont_** or Contact reference ID.
        :type contact_id: str
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
        :return: Retrieve a contact for an existing Rapyd Wallet.
        :rtype: InlineResponse200_71
        """

        Validator(str).validate(ewallet_id)
        Validator(str).validate(contact_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletId}}/contacts/{{contactId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletId", ewallet_id)
            .add_path("contactId", contact_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_71._unmap(response)

    @cast_models
    def update_ewallet_contact(
        self,
        request_body: Contact,
        ewallet_id: str,
        contact_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_71:
        """Update a contact for a Rapyd Wallet.

        :param request_body: The request body.
        :type request_body: Contact
        :param ewallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type ewallet_id: str
        :param contact_id: ID of the contact. String starting with the prefix **cont_**.
        :type contact_id: str
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
        :return: Retrieve a contact for an existing Rapyd Wallet.
        :rtype: InlineResponse200_71
        """

        Validator(Contact).validate(request_body)
        Validator(str).validate(ewallet_id)
        Validator(str).validate(contact_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletId}}/contacts/{{contactId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletId", ewallet_id)
            .add_path("contactId", contact_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_71._unmap(response)

    @cast_models
    def delete_ewallet_contact(
        self,
        ewallet_id: str,
        contact_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_72:
        """Delete a personal contact from a company wallet or client wallet.

        :param ewallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type ewallet_id: str
        :param contact_id: ID of the contact. String starting with the prefix **cont_**.
        :type contact_id: str
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
        :return: Retrieve a contact for an existing Rapyd Wallet.
        :rtype: InlineResponse200_72
        """

        Validator(str).validate(ewallet_id)
        Validator(str).validate(contact_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletId}}/contacts/{{contactId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletId", ewallet_id)
            .add_path("contactId", contact_id)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_72._unmap(response)

    @cast_models
    def get_ewallet_contact_compliance_levels(
        self,
        ewallet_id: str,
        contact_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_73:
        """Verify the compliance status of a personal contact.

        :param ewallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type ewallet_id: str
        :param contact_id: ID of the contact. String starting with **cont_**.
        :type contact_id: str
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
        :return: Verify the compliance status of a personal contact.
        :rtype: InlineResponse200_73
        """

        Validator(str).validate(ewallet_id)
        Validator(str).validate(contact_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletId}}/contacts/{{contactId}}/compliance_levels",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletId", ewallet_id)
            .add_path("contactId", contact_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_73._unmap(response)

    @cast_models
    def get_users(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        phone_number: str = None,
        email: str = None,
        ewallet_reference_id: str = None,
        page_number: float = None,
        page_size: float = None,
        type_: str = None,
        min_balance: float = None,
        currency: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_97:
        """Retrieve a list of Rapyd Wallets. You can filter the list with query parameters.

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
        :param phone_number: Phone number of the Rapyd Wallet in E.164 format., defaults to None
        :type phone_number: str, optional
        :param email: Email address of the wallet owner., defaults to None
        :type email: str, optional
        :param ewallet_reference_id: Wallet ID defined by the customer or end user., defaults to None
        :type ewallet_reference_id: str, optional
        :param page_number: Page number to retrieve. If `page_number` is not specified, page 1 is retrieved., defaults to None
        :type page_number: float, optional
        :param page_size: Number of results per page., defaults to None
        :type page_size: float, optional
        :param type_: Type of wallet - company, person, client., defaults to None
        :type type_: str, optional
        :param min_balance: min_balance, defaults to None
        :type min_balance: float, optional
        :param currency: currency, defaults to None
        :type currency: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: List of eWallets,
        :rtype: InlineResponse200_97
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(phone_number)
        Validator(str).is_optional().validate(email)
        Validator(str).is_optional().validate(ewallet_reference_id)
        Validator(float).is_optional().validate(page_number)
        Validator(float).is_optional().validate(page_size)
        Validator(str).is_optional().validate(type_)
        Validator(float).is_optional().validate(min_balance)
        Validator(str).is_optional().validate(currency)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/ewallets", self.get_default_headers())
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("phone_number", phone_number, explode=False)
            .add_query("email", email, explode=False)
            .add_query("ewallet_reference_id", ewallet_reference_id, explode=False)
            .add_query("page_number", page_number, explode=False)
            .add_query("page_size", page_size, explode=False)
            .add_query("type", type_, explode=False)
            .add_query("min_balance", min_balance, explode=False)
            .add_query("currency", currency, explode=False)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_97._unmap(response)

    @cast_models
    def create_user(
        self,
        request_body: V1EwalletsBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_98:
        """Create a Rapyd Wallet.

        :param request_body: The request body.
        :type request_body: V1EwalletsBody
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
        :return: Rapyd wallet created.
        :rtype: InlineResponse200_98
        """

        Validator(V1EwalletsBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/ewallets", self.get_default_headers())
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
        return InlineResponse200_98._unmap(response)

    @cast_models
    def get_user(
        self,
        ewallet_token: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_98:
        """Retrieve the details of a Rapyd Wallet.

        :param ewallet_token: ID of the wallet. String starting with **ewallet_**.
        :type ewallet_token: str
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
        :return: Retrieve the details of a Rapyd Wallet.
        :rtype: InlineResponse200_98
        """

        Validator(str).validate(ewallet_token)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletToken}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletToken", ewallet_token)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_98._unmap(response)

    @cast_models
    def updated_user(
        self,
        request_body: EwalletsEwalletTokenBody,
        ewallet_token: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_98:
        """Change or modify a Rapyd Wallet.

        :param request_body: The request body.
        :type request_body: EwalletsEwalletTokenBody
        :param ewallet_token: ID of the wallet. String starting with **ewallet_**.
        :type ewallet_token: str
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
        :return: Created Rapyd Wallet,
        :rtype: InlineResponse200_98
        """

        Validator(EwalletsEwalletTokenBody).validate(request_body)
        Validator(str).validate(ewallet_token)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletToken}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletToken", ewallet_token)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_98._unmap(response)

    @cast_models
    def delete_user(
        self,
        ewallet_token: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_66:
        """Delete a Rapyd Wallet. Use this method when the wallet has never been used. This method triggers the Wallet Deleted webhook. This webhook contains the same information as the response.

        :param ewallet_token: ID of the wallet. String starting with **ewallet_**.
        :type ewallet_token: str
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
        :return: Wallet was deleted.
        :rtype: InlineResponse200_66
        """

        Validator(str).validate(ewallet_token)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletToken}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletToken", ewallet_token)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_66._unmap(response)

    @cast_models
    def update_ewallet_status(
        self,
        ewallet_token: str,
        status: UpdateEwalletStatusStatus,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_66:
        """Change Wallet Status

        :param ewallet_token: ID of the Rapyd Wallet. String starting with **ewallet_**. Required when phone number is not used.
        :type ewallet_token: str
        :param status: Status of the wallet. One of the following: ACT - Active, DIS - Disabled, CLO - Close.
        :type status: UpdateEwalletStatusStatus
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
        :return: Operations status
        :rtype: InlineResponse200_66
        """

        Validator(str).validate(ewallet_token)
        Validator(UpdateEwalletStatusStatus).validate(status)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewalletToken}}/statuses/{{status}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewalletToken", ewallet_token)
            .add_path("status", status)
            .serialize()
            .set_method("POST")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_66._unmap(response)

    @cast_models
    def set_account_limit(
        self,
        wallet_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        request_body: AccountLimitsBody = None,
        idempotency: str = None,
    ) -> InlineResponse200_99:
        """Set the maximum balance limit or the minimum balance threshold for an existing wallet account.

        :param request_body: The request body., defaults to None
        :type request_body: AccountLimitsBody, optional
        :param wallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type wallet_id: str
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
        :return: List Contacts for Rapyd Wallet Accounts.
        :rtype: InlineResponse200_99
        """

        Validator(AccountLimitsBody).is_optional().validate(request_body)
        Validator(str).validate(wallet_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{walletId}}/account/limits",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("walletId", wallet_id)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_99._unmap(response)

    @cast_models
    def remove_account_limit(
        self,
        wallet_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_100:
        """Delete a limit on a wallet account.

        :param wallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type wallet_id: str
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
        :return: Coupon was deleted.
        :rtype: InlineResponse200_100
        """

        Validator(str).validate(wallet_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{walletId}}/account/limits",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("walletId", wallet_id)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_100._unmap(response)

    @cast_models
    def get_user_accounts(
        self,
        wallet_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_99:
        """Retrieve details of the balances in a Rapyd Wallet.

        :param wallet_id: ID of the Rapyd Wallet that this contact is associated with. String starting with **ewallet_**.
        :type wallet_id: str
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
        :return: List accounts related to the Rapyd Wallet,
        :rtype: InlineResponse200_99
        """

        Validator(str).validate(wallet_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{walletId}}/accounts",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("walletId", wallet_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_99._unmap(response)

    @cast_models
    def get_user_transactions(
        self,
        wallet_id: str,
        balance: float,
        page_size: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        currency: str = None,
        end_date: str = None,
        ending_before: str = None,
        page_number: str = None,
        start_date: str = None,
        starting_after: str = None,
        type_: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_101:
        """Retrieve a list of all transactions related to a wallet.

        :param wallet_id: ID of the wallet. String starting with **ewallet_**.
        :type wallet_id: str
        :param balance: The updated wallet balance after successful completion of the transaction.
        :type balance: float
        :param page_size: Number of results per page.
        :type page_size: str
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
        :param currency: Three-letter ISO 4217 code for the currency of the transactions. Uppercase., defaults to None
        :type currency: str, optional
        :param end_date: Timestamp of the last transaction or later, in Unix time., defaults to None
        :type end_date: str, optional
        :param ending_before: The ID of the wallet transaction created after the last wallet transaction you want to retrieve. String starting with **wt_**., defaults to None
        :type ending_before: str, optional
        :param page_number: Page number to retrieve., defaults to None
        :type page_number: str, optional
        :param start_date: Timestamp of the first transaction or earlier, in Unix time., defaults to None
        :type start_date: str, optional
        :param starting_after: The ID of the wallet transaction created before the first wallet transaction you want to retrieve. String starting with **wt_**., defaults to None
        :type starting_after: str, optional
        :param type_: Type of transaction., defaults to None
        :type type_: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: List of all transactions related to a wallet.
        :rtype: InlineResponse200_101
        """

        Validator(str).validate(wallet_id)
        Validator(float).validate(balance)
        Validator(str).validate(page_size)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(currency)
        Validator(str).is_optional().validate(end_date)
        Validator(str).is_optional().validate(ending_before)
        Validator(str).is_optional().validate(page_number)
        Validator(str).is_optional().validate(start_date)
        Validator(str).is_optional().validate(starting_after)
        Validator(str).is_optional().validate(type_)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{walletId}}/transactions",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("walletId", wallet_id)
            .add_query("balance", balance, explode=False)
            .add_query("currency", currency, explode=False)
            .add_query("end_date", end_date, explode=False)
            .add_query("ending_before", ending_before, explode=False)
            .add_query("page_number", page_number, explode=False)
            .add_query("page_size", page_size, explode=False)
            .add_query("start_date", start_date, explode=False)
            .add_query("starting_after", starting_after, explode=False)
            .add_query("type", type_, explode=False)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_101._unmap(response)

    @cast_models
    def get_user_transaction_details(
        self,
        wallet_id: str,
        transaction_id: float,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_102:
        """Retrieve the details of a wallet transaction.

        :param wallet_id: ID of the wallet. String starting with **ewallet_**.
        :type wallet_id: str
        :param transaction_id: ID of the transaction, from the response to List Wallet Transactions. String starting with wt_.
        :type transaction_id: float
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
        :return: Retrieve the details of a wallet transaction.
        :rtype: InlineResponse200_102
        """

        Validator(str).validate(wallet_id)
        Validator(float).validate(transaction_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{walletId}}/transactions/{{transactionId}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("walletId", wallet_id)
            .add_path("transactionId", transaction_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_102._unmap(response)

    @cast_models
    def virtual_accounts_by_rapyd_wallet(
        self,
        ewallet: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_103:
        """List the virtual accounts that are attached to a Rapyd Wallet.

        :param ewallet: ID of the Rapyd Wallet that the virtual accounts were issued to. String starting with **ewallet_**.
        :type ewallet: str
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
        :rtype: InlineResponse200_103
        """

        Validator(str).validate(ewallet)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/ewallets/{{ewallet}}/virtual_accounts",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("ewallet", ewallet)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_103._unmap(response)
