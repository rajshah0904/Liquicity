from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class SimulateBlockCardResponseBlockedReason(Enum):
    """An enumeration representing different categories.

    :cvar BLOCKEDREVERSIBLE: "blocked_reversible"
    :vartype BLOCKEDREVERSIBLE: str
    :cvar CANCELED: "canceled"
    :vartype CANCELED: str
    :cvar COMPLIANCE: "compliance"
    :vartype COMPLIANCE: str
    :cvar LOCKEDINCORRECTPIN: "locked_incorrect_pin"
    :vartype LOCKEDINCORRECTPIN: str
    :cvar MIGRATED: "migrated"
    :vartype MIGRATED: str
    :cvar NONE: "none"
    :vartype NONE: str
    :cvar OTHER: "other"
    :vartype OTHER: str
    :cvar REISSUED: "reissued"
    :vartype REISSUED: str
    :cvar SUSPECTEDFRAUD: "suspected_fraud"
    :vartype SUSPECTEDFRAUD: str
    """

    BLOCKEDREVERSIBLE = "blocked_reversible"
    CANCELED = "canceled"
    COMPLIANCE = "compliance"
    LOCKEDINCORRECTPIN = "locked_incorrect_pin"
    MIGRATED = "migrated"
    NONE = "none"
    OTHER = "other"
    REISSUED = "reissued"
    SUSPECTEDFRAUD = "suspected_fraud"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                SimulateBlockCardResponseBlockedReason._member_map_.values(),
            )
        )


class SimulateBlockCardResponseStatus(Enum):
    """An enumeration representing different categories.

    :cvar ACT: "ACT"
    :vartype ACT: str
    :cvar BLO: "BLO"
    :vartype BLO: str
    :cvar IMP: "IMP"
    :vartype IMP: str
    :cvar INA: "INA"
    :vartype INA: str
    """

    ACT = "ACT"
    BLO = "BLO"
    IMP = "IMP"
    INA = "INA"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value, SimulateBlockCardResponseStatus._member_map_.values()
            )
        )


@JsonMap({"id_": "id"})
class SimulateBlockCardResponse(BaseModel):
    """SimulateBlockCardResponse

    :param activated_at: Time that the card was activated, in Unix time., defaults to None
    :type activated_at: float, optional
    :param assigned_at: Time that the card was assigned to a cardholder, in Unix time., defaults to None
    :type assigned_at: float, optional
    :param blocked_reason: Reason for blocking the card., defaults to None
    :type blocked_reason: SimulateBlockCardResponseBlockedReason, optional
    :param card_id: ID of the card. String starting with **card_**., defaults to None
    :type card_id: str, optional
    :param country_iso_alpha_2: The country where the card is issued. Two-letter ISO 3166-1 ALPHA-2 code., defaults to None
    :type country_iso_alpha_2: str, optional
    :param created_at: Time of creation of the issued card object, in Unix time. only., defaults to None
    :type created_at: float, optional
    :param ewallet_contact: Describes the wallet contact that the card is assigned to. String starting with **cont_**. For details about the fields of the 'contact' object, see 'Add Contact to Wallet'., defaults to None
    :type ewallet_contact: str, optional
    :param id_: ID of the issued card object. String starting with **ci_**., defaults to None
    :type id_: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: str, optional
    :param status: Status of the card. One of the following:\<BR\>* **ACT** - Active.\<BR\> * **BLO** - Blocked.\<BR\>* **IMP** - Imported in bulk, but not yet personalized.\<BR\>* **INA** - Inactive.\<BR\>, defaults to None
    :type status: SimulateBlockCardResponseStatus, optional
    """

    def __init__(
        self,
        activated_at: float = None,
        assigned_at: float = None,
        blocked_reason: SimulateBlockCardResponseBlockedReason = None,
        card_id: str = None,
        country_iso_alpha_2: str = None,
        created_at: float = None,
        ewallet_contact: str = None,
        id_: str = None,
        metadata: str = None,
        status: SimulateBlockCardResponseStatus = None,
    ):
        """SimulateBlockCardResponse

        :param activated_at: Time that the card was activated, in Unix time., defaults to None
        :type activated_at: float, optional
        :param assigned_at: Time that the card was assigned to a cardholder, in Unix time., defaults to None
        :type assigned_at: float, optional
        :param blocked_reason: Reason for blocking the card., defaults to None
        :type blocked_reason: SimulateBlockCardResponseBlockedReason, optional
        :param card_id: ID of the card. String starting with **card_**., defaults to None
        :type card_id: str, optional
        :param country_iso_alpha_2: The country where the card is issued. Two-letter ISO 3166-1 ALPHA-2 code., defaults to None
        :type country_iso_alpha_2: str, optional
        :param created_at: Time of creation of the issued card object, in Unix time. only., defaults to None
        :type created_at: float, optional
        :param ewallet_contact: Describes the wallet contact that the card is assigned to. String starting with **cont_**. For details about the fields of the 'contact' object, see 'Add Contact to Wallet'., defaults to None
        :type ewallet_contact: str, optional
        :param id_: ID of the issued card object. String starting with **ci_**., defaults to None
        :type id_: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: str, optional
        :param status: Status of the card. One of the following:\<BR\>* **ACT** - Active.\<BR\> * **BLO** - Blocked.\<BR\>* **IMP** - Imported in bulk, but not yet personalized.\<BR\>* **INA** - Inactive.\<BR\>, defaults to None
        :type status: SimulateBlockCardResponseStatus, optional
        """
        self.activated_at = self._define_number(
            "activated_at", activated_at, nullable=True
        )
        self.assigned_at = self._define_number(
            "assigned_at", assigned_at, nullable=True
        )
        self.blocked_reason = (
            self._enum_matching(
                blocked_reason,
                SimulateBlockCardResponseBlockedReason.list(),
                "blocked_reason",
            )
            if blocked_reason
            else None
        )
        self.card_id = self._define_str("card_id", card_id, nullable=True)
        self.country_iso_alpha_2 = self._define_str(
            "country_iso_alpha_2", country_iso_alpha_2, nullable=True
        )
        self.created_at = self._define_number("created_at", created_at, nullable=True)
        self.ewallet_contact = self._define_str(
            "ewallet_contact", ewallet_contact, nullable=True
        )
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.metadata = self._define_str("metadata", metadata, nullable=True)
        self.status = (
            self._enum_matching(
                status, SimulateBlockCardResponseStatus.list(), "status"
            )
            if status
            else None
        )
