from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .list_webhooks_response_attempts import ListWebhooksResponseAttempts


@JsonMap({"type_": "type"})
class ListWebhooksResponse(BaseModel):
    """ListWebhooksResponse

    :param attempts: List of attempts at sending the webhook. Array of objects that contain the following fields:, defaults to None
    :type attempts: ListWebhooksResponseAttempts, optional
    :param created_at: Timestamp for the creation of the webhook. Unix time., defaults to None
    :type created_at: float, optional
    :param data: The data section of the webhook itself., defaults to None
    :type data: dict, optional
    :param last_attempt_at: Timestamp of the last attempt at sending the webhook. Unix time., defaults to None
    :type last_attempt_at: float, optional
    :param next_attempt_at: Timestamp of the next attempt at sending the webhook. Unix time., defaults to None
    :type next_attempt_at: float, optional
    :param status: Status of the webhook. One of the following: \<BR\> * **NEW** (new) - The webhook was created and has not yet been sent successfully. \<BR\> * **CLO** (closed) - The webhook was sent successfully.\<BR\> * **ERR** (error) - Attempts were made to send the webhook, but the maximum number of retries was reached. The automatic retry process failed. The webhook was not sent. \<BR\> * **RET** (retried) - The webhook was resent., defaults to None
    :type status: str, optional
    :param token: ID of the webhook. String starting with **wh_**., defaults to None
    :type token: str, optional
    :param type_: Internal name of the webhook type., defaults to None
    :type type_: float, optional
    """

    def __init__(
        self,
        attempts: ListWebhooksResponseAttempts = None,
        created_at: float = None,
        data: dict = None,
        last_attempt_at: float = None,
        next_attempt_at: float = None,
        status: str = None,
        token: str = None,
        type_: float = None,
    ):
        """ListWebhooksResponse

        :param attempts: List of attempts at sending the webhook. Array of objects that contain the following fields:, defaults to None
        :type attempts: ListWebhooksResponseAttempts, optional
        :param created_at: Timestamp for the creation of the webhook. Unix time., defaults to None
        :type created_at: float, optional
        :param data: The data section of the webhook itself., defaults to None
        :type data: dict, optional
        :param last_attempt_at: Timestamp of the last attempt at sending the webhook. Unix time., defaults to None
        :type last_attempt_at: float, optional
        :param next_attempt_at: Timestamp of the next attempt at sending the webhook. Unix time., defaults to None
        :type next_attempt_at: float, optional
        :param status: Status of the webhook. One of the following: \<BR\> * **NEW** (new) - The webhook was created and has not yet been sent successfully. \<BR\> * **CLO** (closed) - The webhook was sent successfully.\<BR\> * **ERR** (error) - Attempts were made to send the webhook, but the maximum number of retries was reached. The automatic retry process failed. The webhook was not sent. \<BR\> * **RET** (retried) - The webhook was resent., defaults to None
        :type status: str, optional
        :param token: ID of the webhook. String starting with **wh_**., defaults to None
        :type token: str, optional
        :param type_: Internal name of the webhook type., defaults to None
        :type type_: float, optional
        """
        self.attempts = self._define_object(attempts, ListWebhooksResponseAttempts)
        self.created_at = self._define_number("created_at", created_at, nullable=True)
        self.data = data
        self.last_attempt_at = self._define_number(
            "last_attempt_at", last_attempt_at, nullable=True
        )
        self.next_attempt_at = self._define_number(
            "next_attempt_at", next_attempt_at, nullable=True
        )
        self.status = self._define_str("status", status, nullable=True)
        self.token = self._define_str("token", token, nullable=True)
        self.type_ = self._define_number("type_", type_, nullable=True)
