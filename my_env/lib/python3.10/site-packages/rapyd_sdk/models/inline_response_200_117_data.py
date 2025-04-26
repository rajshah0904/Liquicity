from __future__ import annotations
from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .inline_response_200_117_data_merchant_customer_support import (
    InlineResponse200_117DataMerchantCustomerSupport,
)


class InlineResponse200_117DataRequestType(Enum):
    """An enumeration representing different categories.

    :cvar STORE: "store"
    :vartype STORE: str
    :cvar VERIFY: "verify"
    :vartype VERIFY: str
    """

    STORE = "store"
    VERIFY = "verify"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                InlineResponse200_117DataRequestType._member_map_.values(),
            )
        )


class InlineResponse200_117DataStatus(Enum):
    """An enumeration representing different categories.

    :cvar NEW: "NEW"
    :vartype NEW: str
    :cvar DON: "DON"
    :vartype DON: str
    :cvar EXP: "EXP"
    :vartype EXP: str
    """

    NEW = "NEW"
    DON = "DON"
    EXP = "EXP"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value, InlineResponse200_117DataStatus._member_map_.values()
            )
        )


@JsonMap({"id_": "id"})
class InlineResponse200_117Data(BaseModel):
    """Retrieve the Rapyd ID and merchant reference ID.

    :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type cancel_url: str, optional
    :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type complete_url: str, optional
    :param contact: ID of the wallet contact. String starting with **cont_**., defaults to None
    :type contact: str, optional
    :param country: The two-letter ISO 3166-1 ALPHA-2 code for the country of the identification document., defaults to None
    :type country: str, optional
    :param id_: ID of the Hosted Page Identity Verification object, a string starting with **hp_idv_**., defaults to None
    :type id_: str, optional
    :param language: Determines the default language of the hosted page. For a list of values, see [List Supported Languages](https://docs.rapyd.net/en/list-supported-languages.html). \<BR\> * When this parameter is null, the language of the user's browser is used. \<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param merchant_alias: Client's name., defaults to None
    :type merchant_alias: str, optional
    :param merchant_color: Color of the call-to-action (CTA) button on the hosted page.\<BR\> To configure this field, use the Client Portal., defaults to None
    :type merchant_color: str, optional
    :param merchant_customer_support: Contains details of the client’s customer support. To configure these fields, use the Client Portal., defaults to None
    :type merchant_customer_support: InlineResponse200_117DataMerchantCustomerSupport, optional
    :param merchant_logo: URL for the image of the client's logo.\<BR\> To configure this field, use the Client Portal., defaults to None
    :type merchant_logo: str, optional
    :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers.\<BR\>To configure this field, use the Client Portal., defaults to None
    :type merchant_privacy_policy: str, optional
    :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Porta, defaults to None
    :type merchant_terms: str, optional
    :param merchant_website: The URL where the customer is redirected after exiting the hosted page. Relevant when `cancel_url`, `complete_url` or both fields are not set. To configure this field, use the Client Portal., defaults to None
    :type merchant_website: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
    :type redirect_url: str, optional
    :param reference_id: ID of the identity verification request. Must be unique for each request. Defined by the client., defaults to None
    :type reference_id: str, optional
    :param request_type: Determines the action that is taken on the request. One of the following:\<BR\>* **store** - Store the images on the Rapyd platform.\<BR\>* **verify** - Verify the identity of the person in the images., defaults to None
    :type request_type: InlineResponse200_117DataRequestType, optional
    :param status: Status of the hosted page. One of the following:\<BR\>* **NEW** - The hosted page was created.\<BR\>* **DON** - Done. The identity verification request was submitted.\<BR\>* **EXP** - Expired. The hosted page expired., defaults to None
    :type status: InlineResponse200_117DataStatus, optional
    """

    def __init__(
        self,
        cancel_url: str = None,
        complete_url: str = None,
        contact: str = None,
        country: str = None,
        id_: str = None,
        language: str = None,
        merchant_alias: str = None,
        merchant_color: str = None,
        merchant_customer_support: InlineResponse200_117DataMerchantCustomerSupport = None,
        merchant_logo: str = None,
        merchant_privacy_policy: str = None,
        merchant_terms: str = None,
        merchant_website: str = None,
        page_expiration: float = None,
        redirect_url: str = None,
        reference_id: str = None,
        request_type: InlineResponse200_117DataRequestType = None,
        status: InlineResponse200_117DataStatus = None,
    ):
        """Retrieve the Rapyd ID and merchant reference ID.

        :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type cancel_url: str, optional
        :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type complete_url: str, optional
        :param contact: ID of the wallet contact. String starting with **cont_**., defaults to None
        :type contact: str, optional
        :param country: The two-letter ISO 3166-1 ALPHA-2 code for the country of the identification document., defaults to None
        :type country: str, optional
        :param id_: ID of the Hosted Page Identity Verification object, a string starting with **hp_idv_**., defaults to None
        :type id_: str, optional
        :param language: Determines the default language of the hosted page. For a list of values, see [List Supported Languages](https://docs.rapyd.net/en/list-supported-languages.html). \<BR\> * When this parameter is null, the language of the user's browser is used. \<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param merchant_alias: Client's name., defaults to None
        :type merchant_alias: str, optional
        :param merchant_color: Color of the call-to-action (CTA) button on the hosted page.\<BR\> To configure this field, use the Client Portal., defaults to None
        :type merchant_color: str, optional
        :param merchant_customer_support: Contains details of the client’s customer support. To configure these fields, use the Client Portal., defaults to None
        :type merchant_customer_support: InlineResponse200_117DataMerchantCustomerSupport, optional
        :param merchant_logo: URL for the image of the client's logo.\<BR\> To configure this field, use the Client Portal., defaults to None
        :type merchant_logo: str, optional
        :param merchant_privacy_policy: URL for the terms and conditions of the agreement between the client and the client’s customers.\<BR\>To configure this field, use the Client Portal., defaults to None
        :type merchant_privacy_policy: str, optional
        :param merchant_terms: URL for the client's terms and conditions. To configure this field, use the Client Porta, defaults to None
        :type merchant_terms: str, optional
        :param merchant_website: The URL where the customer is redirected after exiting the hosted page. Relevant when `cancel_url`, `complete_url` or both fields are not set. To configure this field, use the Client Portal., defaults to None
        :type merchant_website: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
        :type redirect_url: str, optional
        :param reference_id: ID of the identity verification request. Must be unique for each request. Defined by the client., defaults to None
        :type reference_id: str, optional
        :param request_type: Determines the action that is taken on the request. One of the following:\<BR\>* **store** - Store the images on the Rapyd platform.\<BR\>* **verify** - Verify the identity of the person in the images., defaults to None
        :type request_type: InlineResponse200_117DataRequestType, optional
        :param status: Status of the hosted page. One of the following:\<BR\>* **NEW** - The hosted page was created.\<BR\>* **DON** - Done. The identity verification request was submitted.\<BR\>* **EXP** - Expired. The hosted page expired., defaults to None
        :type status: InlineResponse200_117DataStatus, optional
        """
        self.cancel_url = self._define_str("cancel_url", cancel_url, nullable=True)
        self.complete_url = self._define_str(
            "complete_url", complete_url, nullable=True
        )
        self.contact = self._define_str("contact", contact, nullable=True)
        self.country = self._define_str("country", country, nullable=True)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.language = self._define_str("language", language, nullable=True)
        self.merchant_alias = self._define_str(
            "merchant_alias", merchant_alias, nullable=True
        )
        self.merchant_color = self._define_str(
            "merchant_color", merchant_color, nullable=True
        )
        self.merchant_customer_support = self._define_object(
            merchant_customer_support, InlineResponse200_117DataMerchantCustomerSupport
        )
        self.merchant_logo = self._define_str(
            "merchant_logo", merchant_logo, nullable=True
        )
        self.merchant_privacy_policy = self._define_str(
            "merchant_privacy_policy", merchant_privacy_policy, nullable=True
        )
        self.merchant_terms = self._define_str(
            "merchant_terms", merchant_terms, nullable=True
        )
        self.merchant_website = self._define_str(
            "merchant_website", merchant_website, nullable=True
        )
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.redirect_url = self._define_str(
            "redirect_url", redirect_url, nullable=True
        )
        self.reference_id = self._define_str(
            "reference_id", reference_id, nullable=True
        )
        self.request_type = (
            self._enum_matching(
                request_type,
                InlineResponse200_117DataRequestType.list(),
                "request_type",
            )
            if request_type
            else None
        )
        self.status = (
            self._enum_matching(
                status, InlineResponse200_117DataStatus.list(), "status"
            )
            if status
            else None
        )
