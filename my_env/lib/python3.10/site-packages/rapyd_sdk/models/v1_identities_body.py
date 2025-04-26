from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class V1IdentitiesBody(BaseModel):
    """V1IdentitiesBody

    :param back_side_image: Base-64-encoded image of the back of the identity document., defaults to None
    :type back_side_image: str, optional
    :param back_side_image_mime_type: MIME type of the back side image of the identity document. Default is, defaults to None
    :type back_side_image_mime_type: str, optional
    :param contact: ID of a personal contact for a 'person' wallet., defaults to None
    :type contact: str, optional
    :param country: country
    :type country: str
    :param document_type: Type of the identification document. Two-letter code.
    :type document_type: str
    :param ewallet: ID of the Rapyd Wallet. String starting with ewallet_.
    :type ewallet: str
    :param face_image: Base-64-encoded image of the face.
    :type face_image: str
    :param face_image_mime_type: MIME type of the face image. Default is image/jpeg., defaults to None
    :type face_image_mime_type: str, optional
    :param front_side_image: Base-64-encoded image of the front of the identity document.
    :type front_side_image: str
    :param front_side_image_mime_type: MIME type of the front side image of the identity document. Default is image/jpeg., defaults to None
    :type front_side_image_mime_type: str, optional
    :param reference_id: ID of the identity verification request. Must be unique for each request. Defined by the client. Maximum length: 36 characters. In sandbox, to simulate success or failure, the string must contain one of the following values: success, failure For example: 12345678success
    :type reference_id: str
    :param request_type: Determines the action that is taken on the request., defaults to None
    :type request_type: str, optional
    :param send_callback: Determines whether a webhook is sent with the results of the verification request., defaults to None
    :type send_callback: str, optional
    """

    def __init__(
        self,
        country: str,
        document_type: str,
        ewallet: str,
        face_image: str,
        front_side_image: str,
        reference_id: str,
        back_side_image: str = None,
        back_side_image_mime_type: str = None,
        contact: str = None,
        face_image_mime_type: str = None,
        front_side_image_mime_type: str = None,
        request_type: str = None,
        send_callback: str = None,
    ):
        """V1IdentitiesBody

        :param back_side_image: Base-64-encoded image of the back of the identity document., defaults to None
        :type back_side_image: str, optional
        :param back_side_image_mime_type: MIME type of the back side image of the identity document. Default is, defaults to None
        :type back_side_image_mime_type: str, optional
        :param contact: ID of a personal contact for a 'person' wallet., defaults to None
        :type contact: str, optional
        :param country: country
        :type country: str
        :param document_type: Type of the identification document. Two-letter code.
        :type document_type: str
        :param ewallet: ID of the Rapyd Wallet. String starting with ewallet_.
        :type ewallet: str
        :param face_image: Base-64-encoded image of the face.
        :type face_image: str
        :param face_image_mime_type: MIME type of the face image. Default is image/jpeg., defaults to None
        :type face_image_mime_type: str, optional
        :param front_side_image: Base-64-encoded image of the front of the identity document.
        :type front_side_image: str
        :param front_side_image_mime_type: MIME type of the front side image of the identity document. Default is image/jpeg., defaults to None
        :type front_side_image_mime_type: str, optional
        :param reference_id: ID of the identity verification request. Must be unique for each request. Defined by the client. Maximum length: 36 characters. In sandbox, to simulate success or failure, the string must contain one of the following values: success, failure For example: 12345678success
        :type reference_id: str
        :param request_type: Determines the action that is taken on the request., defaults to None
        :type request_type: str, optional
        :param send_callback: Determines whether a webhook is sent with the results of the verification request., defaults to None
        :type send_callback: str, optional
        """
        self.back_side_image = self._define_str(
            "back_side_image", back_side_image, nullable=True
        )
        self.back_side_image_mime_type = self._define_str(
            "back_side_image_mime_type", back_side_image_mime_type, nullable=True
        )
        self.contact = self._define_str("contact", contact, nullable=True)
        self.country = self._define_str(
            "country",
            country,
            pattern="Name of the country. Two-letter ISO 3166-1 alpha-2 code.",
        )
        self.document_type = document_type
        self.ewallet = ewallet
        self.face_image = face_image
        self.face_image_mime_type = self._define_str(
            "face_image_mime_type", face_image_mime_type, nullable=True
        )
        self.front_side_image = front_side_image
        self.front_side_image_mime_type = self._define_str(
            "front_side_image_mime_type", front_side_image_mime_type, nullable=True
        )
        self.reference_id = reference_id
        self.request_type = self._define_str(
            "request_type", request_type, nullable=True
        )
        self.send_callback = self._define_str(
            "send_callback", send_callback, nullable=True
        )
