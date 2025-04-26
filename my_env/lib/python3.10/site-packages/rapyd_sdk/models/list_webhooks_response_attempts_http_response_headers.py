from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap(
    {
        "content_length": "content-length",
        "content_type": "content-type",
        "date_": "date",
    }
)
class ListWebhooksResponseAttemptsHttpResponseHeaders(BaseModel):
    """Headers of the HTTP response from the configured webhook destination, with the value received.

    :param connection: Control options for the connection., defaults to None
    :type connection: str, optional
    :param content_length: Length of the content in bytes.ook destination., defaults to None
    :type content_length: float, optional
    :param content_type: MIME type of the content., defaults to None
    :type content_type: str, optional
    :param date_: Timestamp of the response in HTTP-date format (RFC 9110)., defaults to None
    :type date_: str, optional
    :param server: Name of the server., defaults to None
    :type server: str, optional
    """

    def __init__(
        self,
        connection: str = None,
        content_length: float = None,
        content_type: str = None,
        date_: str = None,
        server: str = None,
    ):
        """Headers of the HTTP response from the configured webhook destination, with the value received.

        :param connection: Control options for the connection., defaults to None
        :type connection: str, optional
        :param content_length: Length of the content in bytes.ook destination., defaults to None
        :type content_length: float, optional
        :param content_type: MIME type of the content., defaults to None
        :type content_type: str, optional
        :param date_: Timestamp of the response in HTTP-date format (RFC 9110)., defaults to None
        :type date_: str, optional
        :param server: Name of the server., defaults to None
        :type server: str, optional
        """
        self.connection = self._define_str("connection", connection, nullable=True)
        self.content_length = self._define_number(
            "content_length", content_length, nullable=True
        )
        self.content_type = self._define_str(
            "content_type", content_type, nullable=True
        )
        self.date_ = self._define_str("date_", date_, nullable=True)
        self.server = self._define_str("server", server, nullable=True)
