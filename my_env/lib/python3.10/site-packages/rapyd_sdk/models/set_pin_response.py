from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class SetPinResponseBlockedReason(Enum):
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
            map(lambda x: x.value, SetPinResponseBlockedReason._member_map_.values())
        )


class SetPinResponseStatus(Enum):
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
        return list(map(lambda x: x.value, SetPinResponseStatus._member_map_.values()))


@JsonMap({"id_": "id"})
class SetPinResponse(BaseModel):
    """SetPinResponse

    :param activated_at: Time that the card was activated, in Unix time., defaults to None
    :type activated_at: float, optional
    :param assigned_at: Time that the card was assigned to a cardholder, in Unix time., defaults to None
    :type assigned_at: str, optional
    :param bin: Bank Identifier Number for the institution issuing the card., defaults to None
    :type bin: str, optional
    :param blocked_reason: Reason for blocking the card., defaults to None
    :type blocked_reason: SetPinResponseBlockedReason, optional
    :param card_id: ID of the card. String starting with **card_**., defaults to None
    :type card_id: str, optional
    :param card_program: ID of the card program that the card is issued from. String starting with **cardprog_**., defaults to None
    :type card_program: str, optional
    :param card_tracking_id: Reserved., defaults to None
    :type card_tracking_id: str, optional
    :param country_iso_alpha_2: The country where the card is issued. Two-letter ISO 3166-1 ALPHA-2 code., defaults to None
    :type country_iso_alpha_2: str, optional
    :param created_at: Time of creation of the issued card object, in Unix time., defaults to None
    :type created_at: float, optional
    :param cvv: Card security code. only., defaults to None
    :type cvv: float, optional
    :param expiration_month: Expiration month of the card. Two digits. Relevant when the card issuer supports it for the country. only., defaults to None
    :type expiration_month: str, optional
    :param expiration_year: Expiration year of the card. Two digits. Relevant when the card issuer supports it for the country., defaults to None
    :type expiration_year: str, optional
    :param ewallet_contact: Describes the wallet contact that the card is assigned to. String starting with **cont_**. For details about the fields of the 'contact' object, see 'Add Contact to Wallet'in online API reference., defaults to None
    :type ewallet_contact: str, optional
    :param id_: ID of the issued card object. String starting with **ci_**., defaults to None
    :type id_: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: str, optional
    :param status: Status of the card. One of the following:\<BR\>* **ACT** - Active.\<BR\> * **BLO** - Blocked.\<BR\>* **IMP** - Imported in bulk, but not yet personalized.\<BR\>* **INA** - Inactive.\<BR\>, defaults to None
    :type status: SetPinResponseStatus, optional
    :param sub_bin: Two-digit code., defaults to None
    :type sub_bin: str, optional
    """

    def __init__(
        self,
        activated_at: float = None,
        assigned_at: str = None,
        bin: str = None,
        blocked_reason: SetPinResponseBlockedReason = None,
        card_id: str = None,
        card_program: str = None,
        card_tracking_id: str = None,
        country_iso_alpha_2: str = None,
        created_at: float = None,
        cvv: float = None,
        expiration_month: str = None,
        expiration_year: str = None,
        ewallet_contact: str = None,
        id_: str = None,
        metadata: str = None,
        status: SetPinResponseStatus = None,
        sub_bin: str = None,
    ):
        """SetPinResponse

        :param activated_at: Time that the card was activated, in Unix time., defaults to None
        :type activated_at: float, optional
        :param assigned_at: Time that the card was assigned to a cardholder, in Unix time., defaults to None
        :type assigned_at: str, optional
        :param bin: Bank Identifier Number for the institution issuing the card., defaults to None
        :type bin: str, optional
        :param blocked_reason: Reason for blocking the card., defaults to None
        :type blocked_reason: SetPinResponseBlockedReason, optional
        :param card_id: ID of the card. String starting with **card_**., defaults to None
        :type card_id: str, optional
        :param card_program: ID of the card program that the card is issued from. String starting with **cardprog_**., defaults to None
        :type card_program: str, optional
        :param card_tracking_id: Reserved., defaults to None
        :type card_tracking_id: str, optional
        :param country_iso_alpha_2: The country where the card is issued. Two-letter ISO 3166-1 ALPHA-2 code., defaults to None
        :type country_iso_alpha_2: str, optional
        :param created_at: Time of creation of the issued card object, in Unix time., defaults to None
        :type created_at: float, optional
        :param cvv: Card security code. only., defaults to None
        :type cvv: float, optional
        :param expiration_month: Expiration month of the card. Two digits. Relevant when the card issuer supports it for the country. only., defaults to None
        :type expiration_month: str, optional
        :param expiration_year: Expiration year of the card. Two digits. Relevant when the card issuer supports it for the country., defaults to None
        :type expiration_year: str, optional
        :param ewallet_contact: Describes the wallet contact that the card is assigned to. String starting with **cont_**. For details about the fields of the 'contact' object, see 'Add Contact to Wallet'in online API reference., defaults to None
        :type ewallet_contact: str, optional
        :param id_: ID of the issued card object. String starting with **ci_**., defaults to None
        :type id_: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: str, optional
        :param status: Status of the card. One of the following:\<BR\>* **ACT** - Active.\<BR\> * **BLO** - Blocked.\<BR\>* **IMP** - Imported in bulk, but not yet personalized.\<BR\>* **INA** - Inactive.\<BR\>, defaults to None
        :type status: SetPinResponseStatus, optional
        :param sub_bin: Two-digit code., defaults to None
        :type sub_bin: str, optional
        """
        self.activated_at = self._define_number(
            "activated_at", activated_at, nullable=True
        )
        self.assigned_at = self._define_str("assigned_at", assigned_at, nullable=True)
        self.bin = self._define_str("bin", bin, nullable=True)
        self.blocked_reason = (
            self._enum_matching(
                blocked_reason, SetPinResponseBlockedReason.list(), "blocked_reason"
            )
            if blocked_reason
            else None
        )
        self.card_id = self._define_str("card_id", card_id, nullable=True)
        self.card_program = self._define_str(
            "card_program", card_program, nullable=True
        )
        self.card_tracking_id = self._define_str(
            "card_tracking_id", card_tracking_id, nullable=True
        )
        self.country_iso_alpha_2 = self._define_str(
            "country_iso_alpha_2", country_iso_alpha_2, nullable=True
        )
        self.created_at = self._define_number("created_at", created_at, nullable=True)
        self.cvv = self._define_number("cvv", cvv, nullable=True)
        self.expiration_month = self._define_str(
            "expiration_month", expiration_month, nullable=True
        )
        self.expiration_year = self._define_str(
            "expiration_year", expiration_year, nullable=True
        )
        self.ewallet_contact = self._define_str(
            "ewallet_contact", ewallet_contact, nullable=True
        )
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.metadata = self._define_str("metadata", metadata, nullable=True)
        self.status = (
            self._enum_matching(status, SetPinResponseStatus.list(), "status")
            if status
            else None
        )
        self.sub_bin = self._define_str("sub_bin", sub_bin, nullable=True)
