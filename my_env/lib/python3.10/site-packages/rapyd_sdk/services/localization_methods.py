from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models import (
    InlineResponse200_104,
    InlineResponse200_120,
    InlineResponse200_121,
    InlineResponse200_122,
)


class LocalizationMethodsService(BaseService):

    @cast_models
    def get_fx_rate(
        self,
        action_type: str,
        buy_currency: str,
        sell_currency: str,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        amount: float = None,
        date_: str = None,
        fixed_side: str = None,
        idempotency: str = None,
    ) -> InlineResponse200_104:
        """Retrieve a daily rate for conversion of currencies in payments and payouts. Rapyd uses a snapshot of daily foreign exchange rates fetched at 9 PM UTC. The rate returned includes the FX markup fees.

        :param action_type: Determines the type of transaction that the currency exchange applies to. One of the following - **payment**, **payout**.
        :type action_type: str
        :param buy_currency: Defines the currency purchased in the currency exchange transaction. Three-letter ISO 4217 code in Uppercase.
        :type buy_currency: str
        :param sell_currency: Defines the currency sold in the currency exchange transaction. Three-letter ISO 4217 code in Uppercase.
        :type sell_currency: str
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
        :param amount: Amount of the currency exchange transaction, in units of the fixed-side currency in Decimal., defaults to None
        :type amount: float, optional
        :param date_: The date when the rate is applicable. Today or earlier. Format **YYYY-MM-DD**, defaults to None
        :type date_: str, optional
        :param fixed_side: Indicates whether the rate is fixed for the currency defined by buy_currency or sell_currency. One of the following - **buy**, **sell**., defaults to None
        :type fixed_side: str, optional
        :param idempotency: A unique key that prevents the platform from creating the same object twice., defaults to None
        :type idempotency: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Retrieves fixed daily rate
        :rtype: InlineResponse200_104
        """

        Validator(str).validate(action_type)
        Validator(str).validate(buy_currency)
        Validator(str).validate(sell_currency)
        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(float).is_optional().validate(amount)
        Validator(str).is_optional().validate(date_)
        Validator(str).is_optional().validate(fixed_side)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/fx_rates/", self.get_default_headers())
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .add_query("action_type", action_type)
            .add_query("amount", amount)
            .add_query("buy_currency", buy_currency)
            .add_query("date", date_)
            .add_query("fixed_side", fixed_side)
            .add_query("sell_currency", sell_currency)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_104._unmap(response)

    @cast_models
    def list_supported_languages(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_120:
        """Retrieve a list of the languages supported for hosted pages.<BR> A hosted page can appear in many foreign languages. The `language` (or `merchant_language`) field determines the default language of a hosted page. The field type is string. Use lower-case letters for the value.<BR> * If no value is specified, the language of the user's browser is used. <BR> * If the language of the user's browser cannot be determined, the default language is English. <BR> Relevant to: <BR>* Display Issued Card Details to Customer <BR> * Create Subscription by Hosted Page <BR> * Create Checkout Page <BR> * Create Payment Link <BR> * Create Beneficiary Tokenization Page <BR> * Create Card Token <BR> * Create Identity Verification Page <BR> * Activate Issued Card Using Hosted Page <BR> * Create Hosted Page for PIN Management

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
        :return: Retrieves fixed daily rate
        :rtype: InlineResponse200_120
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/hosted/config/supported_languages",
                self.get_default_headers(),
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_120._unmap(response)

    @cast_models
    def list_countries(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_121:
        """Retrieve a list of all countries.

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
        :return: List of supported countries.
        :rtype: InlineResponse200_121
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(f"{self.base_url}/v1/data/countries", self.get_default_headers())
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_121._unmap(response)

    @cast_models
    def list_currencies(
        self,
        access_key: str,
        content_type: str,
        salt: str,
        signature: str,
        timestamp: str,
        idempotency: str = None,
    ) -> InlineResponse200_122:
        """Retrieve a list of all currencies.

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
        :return: List of currencies.
        :rtype: InlineResponse200_122
        """

        Validator(str).validate(access_key)
        Validator(str).validate(content_type)
        Validator(str).validate(salt)
        Validator(str).validate(signature)
        Validator(str).validate(timestamp)
        Validator(str).is_optional().validate(idempotency)

        serialized_request = (
            Serializer(
                f"{self.base_url}/v1/data/currencies", self.get_default_headers()
            )
            .add_header("access_key", access_key)
            .add_header("Content-Type", content_type)
            .add_header("idempotency", idempotency)
            .add_header("salt", salt)
            .add_header("signature", signature)
            .add_header("timestamp", timestamp)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)
        return InlineResponse200_122._unmap(response)
