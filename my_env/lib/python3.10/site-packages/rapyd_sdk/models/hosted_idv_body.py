from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class HostedIdvBodyRequestType(Enum):
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
            map(lambda x: x.value, HostedIdvBodyRequestType._member_map_.values())
        )


@JsonMap({})
class HostedIdvBody(BaseModel):
    """HostedIdvBody

    :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type cancel_url: str, optional
    :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type complete_url: str, optional
    :param contact: ID of the wallet contact. String starting with **cont_**.
    :type contact: str
    :param country: The two-letter ISO 3166-1 ALPHA-2 code for the country of the identification document. Must match the wallet contact country.
    :type country: str
    :param document_type: Type of the identification document. Two-letter code.\<BR\>See also 'List Official Identification Documents'., defaults to None
    :type document_type: str, optional
    :param ewallet: ID of the Rapyd Wallet. String starting with **ewallet_**.
    :type ewallet: str
    :param force_camera: Requires the applicant to use the device's camera for a current face image, and prohibits uploading an existing image file. Default is **false**., defaults to None
    :type force_camera: bool, optional
    :param language: Determines the default language of the hosted page. For a list of values, see [List Supported Languages](https://docs.rapyd.net/en/list-supported-languages.html). \<BR\> * When this parameter is null, the language of the user's browser is used. \<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param reference_id: ID of the identity verification request. Must be unique for each request. Defined by the client.
    :type reference_id: str
    :param request_type: Determines the action that is taken on the request. One of the following:\<BR\>* **store** - Store the images on the Rapyd platform.\<BR\>* **verify** - Verify the identity of the person in the images., defaults to None
    :type request_type: HostedIdvBodyRequestType, optional
    """

    def __init__(
        self,
        contact: str,
        country: str,
        ewallet: str,
        reference_id: str,
        cancel_url: str = None,
        complete_url: str = None,
        document_type: str = None,
        force_camera: bool = None,
        language: str = None,
        page_expiration: float = None,
        request_type: HostedIdvBodyRequestType = None,
    ):
        """HostedIdvBody

        :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type cancel_url: str, optional
        :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type complete_url: str, optional
        :param contact: ID of the wallet contact. String starting with **cont_**.
        :type contact: str
        :param country: The two-letter ISO 3166-1 ALPHA-2 code for the country of the identification document. Must match the wallet contact country.
        :type country: str
        :param document_type: Type of the identification document. Two-letter code.\<BR\>See also 'List Official Identification Documents'., defaults to None
        :type document_type: str, optional
        :param ewallet: ID of the Rapyd Wallet. String starting with **ewallet_**.
        :type ewallet: str
        :param force_camera: Requires the applicant to use the device's camera for a current face image, and prohibits uploading an existing image file. Default is **false**., defaults to None
        :type force_camera: bool, optional
        :param language: Determines the default language of the hosted page. For a list of values, see [List Supported Languages](https://docs.rapyd.net/en/list-supported-languages.html). \<BR\> * When this parameter is null, the language of the user's browser is used. \<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation.\<BR\>**Range**: 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param reference_id: ID of the identity verification request. Must be unique for each request. Defined by the client.
        :type reference_id: str
        :param request_type: Determines the action that is taken on the request. One of the following:\<BR\>* **store** - Store the images on the Rapyd platform.\<BR\>* **verify** - Verify the identity of the person in the images., defaults to None
        :type request_type: HostedIdvBodyRequestType, optional
        """
        self.cancel_url = self._define_str("cancel_url", cancel_url, nullable=True)
        self.complete_url = self._define_str(
            "complete_url", complete_url, nullable=True
        )
        self.contact = contact
        self.country = country
        self.document_type = self._define_str(
            "document_type", document_type, nullable=True
        )
        self.ewallet = ewallet
        self.force_camera = force_camera
        self.language = self._define_str("language", language, nullable=True)
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.reference_id = reference_id
        self.request_type = (
            self._enum_matching(
                request_type, HostedIdvBodyRequestType.list(), "request_type"
            )
            if request_type
            else None
        )
