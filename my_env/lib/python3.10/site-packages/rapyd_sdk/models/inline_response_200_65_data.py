from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class InlineResponse200_65Data(BaseModel):
    """InlineResponse200_65Data

    :param payout_token: ID of the payout. String starting with **payout_**., defaults to None
    :type payout_token: str, optional
    :param file_id: ID of the uploaded file. UUID., defaults to None
    :type file_id: str, optional
    :param file_name: The name of the document file., defaults to None
    :type file_name: str, optional
    :param file_extension: The uploaded file's extension., defaults to None
    :type file_extension: str, optional
    :param created_at: The date and time when the file was successfully uploaded. Format is **YYYY-MM-DD HH:MM:SS**., defaults to None
    :type created_at: str, optional
    """

    def __init__(
        self,
        payout_token: str = None,
        file_id: str = None,
        file_name: str = None,
        file_extension: str = None,
        created_at: str = None,
    ):
        """InlineResponse200_65Data

        :param payout_token: ID of the payout. String starting with **payout_**., defaults to None
        :type payout_token: str, optional
        :param file_id: ID of the uploaded file. UUID., defaults to None
        :type file_id: str, optional
        :param file_name: The name of the document file., defaults to None
        :type file_name: str, optional
        :param file_extension: The uploaded file's extension., defaults to None
        :type file_extension: str, optional
        :param created_at: The date and time when the file was successfully uploaded. Format is **YYYY-MM-DD HH:MM:SS**., defaults to None
        :type created_at: str, optional
        """
        self.payout_token = self._define_str(
            "payout_token", payout_token, nullable=True
        )
        self.file_id = self._define_str("file_id", file_id, nullable=True)
        self.file_name = self._define_str("file_name", file_name, nullable=True)
        self.file_extension = self._define_str(
            "file_extension", file_extension, nullable=True
        )
        self.created_at = self._define_str("created_at", created_at, nullable=True)
