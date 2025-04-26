from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class InlineResponse200_98DataStatus(Enum):
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
            map(lambda x: x.value, InlineResponse200_98DataStatus._member_map_.values())
        )


@JsonMap({})
class InlineResponse200_98Data(BaseModel):
    """InlineResponse200_98Data

    :param status: status, defaults to None
    :type status: InlineResponse200_98DataStatus, optional
    """

    def __init__(self, status: InlineResponse200_98DataStatus = None):
        """InlineResponse200_98Data

        :param status: status, defaults to None
        :type status: InlineResponse200_98DataStatus, optional
        """
        self.status = (
            self._enum_matching(status, InlineResponse200_98DataStatus.list(), "status")
            if status
            else None
        )
