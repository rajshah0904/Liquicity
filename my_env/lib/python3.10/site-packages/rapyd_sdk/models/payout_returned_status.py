from enum import Enum


class PayoutReturnedStatus(Enum):
    """An enumeration representing different categories.

    :cvar RETURNED: "Returned"
    :vartype RETURNED: str
    :cvar CREATED: "Created"
    :vartype CREATED: str
    :cvar COMPLETED: "Completed"
    :vartype COMPLETED: str
    :cvar CANCELED: "Canceled"
    :vartype CANCELED: str
    :cvar REJECTED: "Rejected"
    :vartype REJECTED: str
    :cvar ERROR: "Error"
    :vartype ERROR: str
    :cvar CONFIRMATION: "Confirmation"
    :vartype CONFIRMATION: str
    :cvar EXPIRED: "Expired"
    :vartype EXPIRED: str
    """

    RETURNED = "Returned"
    CREATED = "Created"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
    REJECTED = "Rejected"
    ERROR = "Error"
    CONFIRMATION = "Confirmation"
    EXPIRED = "Expired"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(map(lambda x: x.value, PayoutReturnedStatus._member_map_.values()))
