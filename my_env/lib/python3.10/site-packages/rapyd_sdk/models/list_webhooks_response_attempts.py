from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .list_webhooks_response_attempts_http_response_headers import (
    ListWebhooksResponseAttemptsHttpResponseHeaders,
)


@JsonMap({})
class ListWebhooksResponseAttempts(BaseModel):
    """List of attempts at sending the webhook. Array of objects that contain the following fields:

    :param error: Error message received from the configured webhook destination., defaults to None
    :type error: str, optional
    :param http_status_code: HTTP status code returned by the configured webhook destination., defaults to None
    :type http_status_code: str, optional
    :param http_response_body: Body of the HTTP response from the configured webhook destination., defaults to None
    :type http_response_body: str, optional
    :param http_response_headers: Headers of the HTTP response from the configured webhook destination, with the value received., defaults to None
    :type http_response_headers: ListWebhooksResponseAttemptsHttpResponseHeaders, optional
    """

    def __init__(
        self,
        error: str = None,
        http_status_code: str = None,
        http_response_body: str = None,
        http_response_headers: ListWebhooksResponseAttemptsHttpResponseHeaders = None,
    ):
        """List of attempts at sending the webhook. Array of objects that contain the following fields:

        :param error: Error message received from the configured webhook destination., defaults to None
        :type error: str, optional
        :param http_status_code: HTTP status code returned by the configured webhook destination., defaults to None
        :type http_status_code: str, optional
        :param http_response_body: Body of the HTTP response from the configured webhook destination., defaults to None
        :type http_response_body: str, optional
        :param http_response_headers: Headers of the HTTP response from the configured webhook destination, with the value received., defaults to None
        :type http_response_headers: ListWebhooksResponseAttemptsHttpResponseHeaders, optional
        """
        self.error = self._define_str("error", error, nullable=True)
        self.http_status_code = self._define_str(
            "http_status_code", http_status_code, nullable=True
        )
        self.http_response_body = self._define_str(
            "http_response_body", http_response_body, nullable=True
        )
        self.http_response_headers = self._define_object(
            http_response_headers, ListWebhooksResponseAttemptsHttpResponseHeaders
        )
