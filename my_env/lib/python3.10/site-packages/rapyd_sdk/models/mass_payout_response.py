from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({"id_": "id", "type_": "type"})
class MassPayoutResponse(BaseModel):
    """MassPayoutResponse

    :param created_at: Time of creation of the batch operation, in Unix time (seconds)., defaults to None
    :type created_at: float, optional
    :param id_: ID of the batch operation. String starting with **batch_**.Three-letter ISO 4217 code for the currency of an existing account., defaults to None
    :type id_: str, optional
    :param original_name: Filename of the uploaded batch file., defaults to None
    :type original_name: str, optional
    :param status: Status of the batch operation - "NEW"., defaults to None
    :type status: str, optional
    :param type_: Batch operation type - "mass_payout_pci"., defaults to None
    :type type_: str, optional
    """

    def __init__(
        self,
        created_at: float = None,
        id_: str = None,
        original_name: str = None,
        status: str = None,
        type_: str = None,
    ):
        """MassPayoutResponse

        :param created_at: Time of creation of the batch operation, in Unix time (seconds)., defaults to None
        :type created_at: float, optional
        :param id_: ID of the batch operation. String starting with **batch_**.Three-letter ISO 4217 code for the currency of an existing account., defaults to None
        :type id_: str, optional
        :param original_name: Filename of the uploaded batch file., defaults to None
        :type original_name: str, optional
        :param status: Status of the batch operation - "NEW"., defaults to None
        :type status: str, optional
        :param type_: Batch operation type - "mass_payout_pci"., defaults to None
        :type type_: str, optional
        """
        self.created_at = self._define_number("created_at", created_at, nullable=True)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.original_name = self._define_str(
            "original_name", original_name, nullable=True
        )
        self.status = self._define_str("status", status, nullable=True)
        self.type_ = self._define_str("type_", type_, nullable=True)
