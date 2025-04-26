from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import InlineResponse200_65, InlineResponse200_66


class DisburseUploadDocumentsService(BaseService):

    @cast_models
    def upload_documents_to_payout(
        self,
        payout: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        file: str,
        idempotency: str = None,
    ) -> InlineResponse200_65:
        """Upload one supporting document file or multiple document files to a specific payout. These documents include ID scans, company registrations, and all other documents that support the validity of the payout. A file can be uploaded only when the payout is in a **Created**, **Hold**, or **Pending** status.

        :param payout: ID of the payout. String starting with **payout_**.
        :type payout: str
        :param access_key: Unique access key provided by Rapyd for each authorized user.
        :type access_key: str
        :param content_type: Indicates that the data appears in JSON format. Set to **multipart/form-data**.
        :type content_type: str
        :param salt: Random string. Recommended length: 8-16 characters.
        :type salt: str
        :param signature: Signature calculated for each request individually. See [Request Signatures](https://docs.rapyd.net/en/request-signatures.html).
        :type signature: str
        :param timestamp: Timestamp for the request, in Unix time (seconds).
        :type timestamp: str
        :param file: Use the `-F` or `--form` parameter to define the path to the document file on your local machine. Supported file types include '*.pdf', '*.doc', '*.docx', '.*csv', '*.jpeg', '*.jpg', '*.gif', '*.png'. Format of input must follow the `multipart/form-data` protocol. Use the `files` parameter to upload multiple files.<BR>**Note**<BR> * Maximum number of files that can be uploaded in one request is 10.<BR>* Maximum size of files that can be uploaded in one request is 20 MB.<BR>* Document file name should be up to 200 characters long.
        :type file: str
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The following parameters are returned for each file that was uploaded.
        :rtype: InlineResponse200_65
        """

        Validator(str).validate(payout)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).validate(file)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/files/documents/payout/{{payout}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_header("file", file)
            .add_path("payout", payout)
            .serialize()
            .set_method("POST")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_65._unmap(response)

    @cast_models
    def list_documents_of_payout(
        self,
        payout: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_65:
        """Retrieve details of all supporting document files that were previously uploaded to a specific payout.

        :param payout: ID of the payout. String starting with **payout_**.
        :type payout: str
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
        :return: The following parameters are returned for each file that was uploaded.
        :rtype: InlineResponse200_65
        """

        Validator(str).validate(payout)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payouts/{{payout}}/documents/",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("payout", payout)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_65._unmap(response)

    @cast_models
    def delete_documents_of_payout(
        self,
        payout: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_66:
        """Delete all document files that were previously uploaded to a specific payout.

        :param payout: ID of the payout. String starting with **payout_**.
        :type payout: str
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
        :return: Returns a **SUCCESS** status.
        :rtype: InlineResponse200_66
        """

        Validator(str).validate(payout)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payouts/{{payout}}/documents/",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("payout", payout)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_66._unmap(response)

    @cast_models
    def get_document_of_payout(
        self,
        payout: str,
        file_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_65:
        """Retrieve details of all supporting document files that were previously uploaded to a specific payout.

        :param payout: ID of the payout. String starting with **payout_**.
        :type payout: str
        :param file_id: ID of the specific document file. UUID.
        :type file_id: str
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
        :return: The following parameters are returned for the file that was uploaded.
        :rtype: InlineResponse200_65
        """

        Validator(str).validate(payout)
        Validator(str).validate(file_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payouts/{{payout}}/documents/{{file_id}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("payout", payout)
            .add_path("file_id", file_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_65._unmap(response)

    @cast_models
    def delete_document_of_payout(
        self,
        payout: str,
        file_id: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_66:
        """Delete a document file that was previously uploaded to a specific payout.

        :param payout: ID of the payout. String starting with **payout_**.
        :type payout: str
        :param file_id: ID of the specific document file. UUID.
        :type file_id: str
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
        :return: Returns a **SUCCESS** status.
        :rtype: InlineResponse200_66
        """

        Validator(str).validate(payout)
        Validator(str).validate(file_id)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/payouts/{{payout}}/documents/{{file_id}}",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_path("payout", payout)
            .add_path("file_id", file_id)
            .serialize()
            .set_method("DELETE")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_66._unmap(response)
