from __future__ import annotations
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .contact import Contact


@JsonMap({"id_": "id"})
class CardIssuing(BaseModel):
    """CardIssuing

    :param activated_at: Time that the card was activated, in Unix time. Response only., defaults to None
    :type activated_at: float, optional
    :param assigned_at: Time that the card was assigned to a cardholder, in Unix time. Response only., defaults to None
    :type assigned_at: float, optional
    :param blocked_reason: Reason for blocking the card., defaults to None
    :type blocked_reason: str, optional
    :param card_id: ID of the card. String starting with **card_**., defaults to None
    :type card_id: str, optional
    :param card_program: ID of the card program that the card is issued from. String starting with **cardprog_**., defaults to None
    :type card_program: str, optional
    :param country_iso_alpha_2: The country where the card is issued. Two-letter ISO 3166-1 ALPHA-2 code. Response only., defaults to None
    :type country_iso_alpha_2: str, optional
    :param created_at: Time of creation of the issued card object, in Unix time. Response only., defaults to None
    :type created_at: float, optional
    :param ewallet_contact: ewallet_contact, defaults to None
    :type ewallet_contact: Contact, optional
    :param id_: ID of the Issued Card object. String starting with **ci_**., defaults to None
    :type id_: str, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param public_details: Details of the issued card., defaults to None
    :type public_details: dict, optional
    :param status: Status of the card, defaults to None
    :type status: str, optional
    :param card_tracking_id: Reserved, defaults to None
    :type card_tracking_id: str, optional
    """

    def __init__(
        self,
        activated_at: float = None,
        assigned_at: float = None,
        blocked_reason: str = None,
        card_id: str = None,
        card_program: str = None,
        country_iso_alpha_2: str = None,
        created_at: float = None,
        ewallet_contact: Contact = None,
        id_: str = None,
        metadata: dict = None,
        public_details: dict = None,
        status: str = None,
        card_tracking_id: str = None,
    ):
        """CardIssuing

        :param activated_at: Time that the card was activated, in Unix time. Response only., defaults to None
        :type activated_at: float, optional
        :param assigned_at: Time that the card was assigned to a cardholder, in Unix time. Response only., defaults to None
        :type assigned_at: float, optional
        :param blocked_reason: Reason for blocking the card., defaults to None
        :type blocked_reason: str, optional
        :param card_id: ID of the card. String starting with **card_**., defaults to None
        :type card_id: str, optional
        :param card_program: ID of the card program that the card is issued from. String starting with **cardprog_**., defaults to None
        :type card_program: str, optional
        :param country_iso_alpha_2: The country where the card is issued. Two-letter ISO 3166-1 ALPHA-2 code. Response only., defaults to None
        :type country_iso_alpha_2: str, optional
        :param created_at: Time of creation of the issued card object, in Unix time. Response only., defaults to None
        :type created_at: float, optional
        :param ewallet_contact: ewallet_contact, defaults to None
        :type ewallet_contact: Contact, optional
        :param id_: ID of the Issued Card object. String starting with **ci_**., defaults to None
        :type id_: str, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param public_details: Details of the issued card., defaults to None
        :type public_details: dict, optional
        :param status: Status of the card, defaults to None
        :type status: str, optional
        :param card_tracking_id: Reserved, defaults to None
        :type card_tracking_id: str, optional
        """
        self.activated_at = self._define_number(
            "activated_at", activated_at, nullable=True
        )
        self.assigned_at = self._define_number(
            "assigned_at", assigned_at, nullable=True
        )
        self.blocked_reason = self._define_str(
            "blocked_reason", blocked_reason, nullable=True
        )
        self.card_id = self._define_str("card_id", card_id, nullable=True)
        self.card_program = self._define_str(
            "card_program", card_program, nullable=True
        )
        self.country_iso_alpha_2 = self._define_str(
            "country_iso_alpha_2", country_iso_alpha_2, nullable=True
        )
        self.created_at = self._define_number("created_at", created_at, nullable=True)
        self.ewallet_contact = self._define_object(ewallet_contact, Contact)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.metadata = metadata
        self.public_details = public_details
        self.status = self._define_str("status", status, nullable=True)
        self.card_tracking_id = self._define_str(
            "card_tracking_id", card_tracking_id, nullable=True
        )
