from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    CardsAdjustmentBody,
    CardsAuthorizationBody,
    CardsClearingBody,
    CardsRefundBody,
    CardsReversalBody,
    CardsSimulateBlockBody,
    InlineResponse200_86,
    InlineResponse200_87,
    InlineResponse200_88,
    InlineResponse200_89,
)


class IssuingSimulationsService(BaseService):

    @cast_models
    def simulate_block_card(
        self,
        request_body: CardsSimulateBlockBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_86:
        """Simulate a third-party stop notice for an issued card.<BR>Relevant to the sandbox.<BR>Rapyd sets the card status to **BLO** (blocked) and sends you the Card Issuing Blocked Webhook.<BR> To unblock the card, see Update Card Status.<BR>**Prerequisites**:<BR> * Issue Card <BR> * Activate Issued Card Using API

        :param request_body: The request body.
        :type request_body: CardsSimulateBlockBody
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
        :return: Returns card details.
        :rtype: InlineResponse200_86
        """

        Validator(CardsSimulateBlockBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/issuing/cards/simulate_block",
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
        return InlineResponse200_86._unmap(response)

    @cast_models
    def simulate_card_transaction_authorization_request_eea(
        self,
        request_body: CardsAuthorizationBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_87:
        """Simulate Rapyd’s request to your authorization server.<BR> If you have implemented Remote Authorization, Rapyd sends authorization requests to your remote authorization server when the card network requests approval of a transaction on a card issued to a Rapyd Wallet. Use this method in the sandbox.<BR>The response contains all the fields you must send to Rapyd when you receive an authorization request in production. See also Remote Authorization.<BR> When `financial_impact` is set to **credit**, this method triggers 'Card Issuing Credit Webhook'.   When `financial_impact` is set to debit, this method triggers 'Card Issuing Authorization Approved' Webhook. Funds in the wallet move from **available balance** to **on-hold balance**. <BR> To simulate deducting the funds from the wallet, run 'Simulate Clearing a Card Transaction - EEA'.<BR> This method applies to cards issued in the European Economic Area (EEA). For cards issued outside the EEA, see Simulate a Card Transaction Authorization Request - Non-EEA.<BR>**Prerequisites**<BR> * A **company** wallet with a **personal** contact. Run 'Create Wallet' and then 'Add Contact to Wallet'<BR>* Issue Card<BR> * Activate Issued Card Using API<BR> * Add Funds to Wallet Account

        :param request_body: The request body.
        :type request_body: CardsAuthorizationBody
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
        :return: Returns card and transaction details.
        :rtype: InlineResponse200_87
        """

        Validator(CardsAuthorizationBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/issuing/cards/authorization",
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
        return InlineResponse200_87._unmap(response)

    @cast_models
    def simulate_card_transaction_authorization_reversal_eea(
        self,
        request_body: CardsReversalBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_88:
        """Simulate a retail location’s reversal of a card authorization.<BR>The retail location where a card was used for a purchase can send a reversal through the card network to cancel a previous authorization request. This can occur when the transaction is not completed within the time required by the card issuer. When Rapyd receives a request for reversal from the card network, it reverses the transaction and sends you a webhook. Use this method in the sandbox.<BR>This method triggers Card Issuing Reversal Webhook . This method moves the reversed funds in the wallet from **on-hold** balance to **available balance**. <BR>This method applies to cards issued in the European Economic Area (EEA). For cards issued outside the EEA, see 'Simulate a Card Transaction Authorization Reversal - Non-EEA' in Rapyd's online API reference.<BR>**Prerequisites:**<BR> * Issue Card<BR> * Activate Issued Card Using API<BR> * Simulate a Card Transaction Authorization Request - EEA

        :param request_body: The request body.
        :type request_body: CardsReversalBody
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
        :return: Returns card and transaction details.
        :rtype: InlineResponse200_88
        """

        Validator(CardsReversalBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/issuing/cards/reversal", self.get_default_headers()
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
        return InlineResponse200_88._unmap(response)

    @cast_models
    def simulate_clearing_card_transaction_eea(
        self,
        request_body: CardsClearingBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_89:
        """Simulate clearing a debit transaction.<BR>This method triggers Webhook - Card Issuing Sale. When a fee is charged for an ATM transaction, this method also triggers Webhook - Card Issuing ATM Fee. Use this method in the sandbox.<BR>This method deducts funds from the **on-hold** balance in the wallet.<BR>**Prerequisites:**<BR> * Issue Card<BR> * Activate Issued Card Using API<BR> * Simulate a Card Transaction Authorization Request - EEA

        :param request_body: The request body.
        :type request_body: CardsClearingBody
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
        :return: Returns card clearing and transaction details.
        :rtype: InlineResponse200_89
        """

        Validator(CardsClearingBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/issuing/cards/clearing", self.get_default_headers()
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
        return InlineResponse200_89._unmap(response)

    @cast_models
    def simulate_card_refund_eea(
        self,
        request_body: CardsRefundBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_89:
        """Simulate a retail location making a refund to an issued card.<BR> This method triggers Card Issuing Refund Webhook. This method credits the **available balance** of the wallet with the refunded amount. See 'Wallet Balance Types' in online API reference. Use this method in the sandbox.<BR> This method applies to cards issued in the European Economic Area (EEA). For cards issued outside the EEA, see 'Simulate a Card Refund - Non-EEA'  in online API reference. <BR>**Prerequisites:**<BR>* An issued card. See 'Issue Card'.<BR>* Activate the card via API or by using a Hosted Page.<BR>* Authorization of a card transaction. See 'Simulate a Card Transaction Authorization Request - EEA'.

        :param request_body: The request body.
        :type request_body: CardsRefundBody
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
        :return: Returns card refund and transaction details.
        :rtype: InlineResponse200_89
        """

        Validator(CardsRefundBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/issuing/cards/refund", self.get_default_headers()
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
        return InlineResponse200_89._unmap(response)

    @cast_models
    def simulate_card_transaction_adjustment_eea(
        self,
        request_body: CardsAdjustmentBody,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_89:
        """Use this method in the sandbox to simulate an adjustment to a card transaction. A retail location can adjust the amount of a transaction made by an issued card. The adjustment is either a credit or a debit. This method triggers Card Issuing Adjustment Webhook. This method updates the **available balance** of the wallet with the credit or deduction. See 'Wallet Balance Types' in online API Reference. This method applies to cards issued in the European Economic Area (EEA). <BR>**Prerequisites:**<BR>* Issue card<BR>* Activate the card via API <BR>* Simulate a Card Transaction Authorization Request - EEA

        :param request_body: The request body.
        :type request_body: CardsAdjustmentBody
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
        :return: Returns card adjustment and transaction details.
        :rtype: InlineResponse200_89
        """

        Validator(CardsAdjustmentBody).validate(request_body)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/issuing/cards/adjustment",
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
        return InlineResponse200_89._unmap(response)
