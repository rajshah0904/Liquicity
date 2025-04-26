from __future__ import annotations
from enum import Enum
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .v1hosteddisbursebeneficiary_beneficiary_optional_fields import (
    V1hosteddisbursebeneficiaryBeneficiaryOptionalFields,
)


class DisburseBeneficiaryBodyBeneficiaryEntityType(Enum):
    """An enumeration representing different categories.

    :cvar COMPANY: "company"
    :vartype COMPANY: str
    :cvar INDIVIDUAL: "individual"
    :vartype INDIVIDUAL: str
    """

    COMPANY = "company"
    INDIVIDUAL = "individual"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                DisburseBeneficiaryBodyBeneficiaryEntityType._member_map_.values(),
            )
        )


class DisburseBeneficiaryBodyBeneficiaryExtendedFields(Enum):
    """An enumeration representing different categories.

    :cvar TRUE: "true"
    :vartype TRUE: str
    :cvar FALSE: "false"
    :vartype FALSE: str
    """

    TRUE = "true"
    FALSE = "false"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                DisburseBeneficiaryBodyBeneficiaryExtendedFields._member_map_.values(),
            )
        )


class DisburseBeneficiaryBodyCategory(Enum):
    """An enumeration representing different categories.

    :cvar BANK: "bank"
    :vartype BANK: str
    :cvar CARD: "card"
    :vartype CARD: str
    """

    BANK = "bank"
    CARD = "card"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value, DisburseBeneficiaryBodyCategory._member_map_.values()
            )
        )


class DisburseBeneficiaryBodySenderEntityType(Enum):
    """An enumeration representing different categories.

    :cvar COMPANY: "company"
    :vartype COMPANY: str
    :cvar INDIVIDUAL: "individual"
    :vartype INDIVIDUAL: str
    """

    COMPANY = "company"
    INDIVIDUAL = "individual"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                DisburseBeneficiaryBodySenderEntityType._member_map_.values(),
            )
        )


@JsonMap({})
class DisburseBeneficiaryBody(BaseModel):
    """DisburseBeneficiaryBody

    :param beneficiary_country: The two-letter ISO 3166-1 ALPHA-2 code for the country of the beneficiary’s bank account. The two-letter prefix of the payout method type matches the beneficiary country code., defaults to None
    :type beneficiary_country: str, optional
    :param beneficiary_entity_type: Type of entity for the beneficiary. One of the following:
    :type beneficiary_entity_type: DisburseBeneficiaryBodyBeneficiaryEntityType
    :param beneficiary_extended_fields: When the value is **true**, the hosted tokenization page displays additional required fields.\<BR\> * Additional required fields when `beneficiary_entity_type` is **individual**: `address`, `city`, `country`, `date_of_birth`, `first_name`, `gender`, `identification_type`, `identification_value`, `last_name`, `nationality`. \<BR\> * Additional required fields when `beneficiary_entity_type` is **company**: `address`, `city`, `company_name`, `country`, `country_of_incorporation`, `date_of_incorporation`, `identification_type`, `identification_value`.\<BR\> For more information on the additional required fields, see 'Create Extended Beneficiary'.\<BR\> **Note**: Currently only available in the sandbox., defaults to None
    :type beneficiary_extended_fields: DisburseBeneficiaryBodyBeneficiaryExtendedFields, optional
    :param beneficiary_optional_fields: Additional information about the beneficiary., defaults to None
    :type beneficiary_optional_fields: List[V1hosteddisbursebeneficiaryBeneficiaryOptionalFields], optional
    :param category: The category of payout method. One of the following: \<BR\> * **bank**\<BR\> * **card** - US only., defaults to None
    :type category: DisburseBeneficiaryBodyCategory, optional
    :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type complete_url: str, optional
    :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'.\<BR\> * When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param merchant_alias: Client's name., defaults to None
    :type merchant_alias: str, optional
    :param merchant_reference_id: Identifier defined by the client for reference purposes. Limit: 45 characters., defaults to None
    :type merchant_reference_id: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation. \<BR\> **Range**: 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param payout_currency: Currency accepted by the beneficiary’s bank account. Three-letter ISO 4217 code., defaults to None
    :type payout_currency: str, optional
    :param payout_method_types_exclude: List of payout methods that are excluded from display on the beneficiary tokenization page., defaults to None
    :type payout_method_types_exclude: List[dict], optional
    :param payout_method_types_include: Array of strings. List of payout methods that are displayed on the beneficiary tokenization page., defaults to None
    :type payout_method_types_include: List[dict], optional
    :param sender_country: The two-letter ISO 3166-1 ALPHA-2 code for the sender’s country.
    :type sender_country: str
    :param sender_currency: Currency paid from the sender’s wallet. Three-letter ISO 4217 code., defaults to None
    :type sender_currency: str, optional
    :param sender_entity_type: Type of entity for the sender.
    :type sender_entity_type: DisburseBeneficiaryBodySenderEntityType
    """

    def __init__(
        self,
        beneficiary_entity_type: DisburseBeneficiaryBodyBeneficiaryEntityType,
        sender_country: str,
        sender_entity_type: DisburseBeneficiaryBodySenderEntityType,
        beneficiary_country: str = None,
        beneficiary_extended_fields: DisburseBeneficiaryBodyBeneficiaryExtendedFields = None,
        beneficiary_optional_fields: List[
            V1hosteddisbursebeneficiaryBeneficiaryOptionalFields
        ] = None,
        category: DisburseBeneficiaryBodyCategory = None,
        complete_url: str = None,
        language: str = None,
        merchant_alias: str = None,
        merchant_reference_id: str = None,
        page_expiration: float = None,
        payout_currency: str = None,
        payout_method_types_exclude: List[dict] = None,
        payout_method_types_include: List[dict] = None,
        sender_currency: str = None,
    ):
        """DisburseBeneficiaryBody

        :param beneficiary_country: The two-letter ISO 3166-1 ALPHA-2 code for the country of the beneficiary’s bank account. The two-letter prefix of the payout method type matches the beneficiary country code., defaults to None
        :type beneficiary_country: str, optional
        :param beneficiary_entity_type: Type of entity for the beneficiary. One of the following:
        :type beneficiary_entity_type: DisburseBeneficiaryBodyBeneficiaryEntityType
        :param beneficiary_extended_fields: When the value is **true**, the hosted tokenization page displays additional required fields.\<BR\> * Additional required fields when `beneficiary_entity_type` is **individual**: `address`, `city`, `country`, `date_of_birth`, `first_name`, `gender`, `identification_type`, `identification_value`, `last_name`, `nationality`. \<BR\> * Additional required fields when `beneficiary_entity_type` is **company**: `address`, `city`, `company_name`, `country`, `country_of_incorporation`, `date_of_incorporation`, `identification_type`, `identification_value`.\<BR\> For more information on the additional required fields, see 'Create Extended Beneficiary'.\<BR\> **Note**: Currently only available in the sandbox., defaults to None
        :type beneficiary_extended_fields: DisburseBeneficiaryBodyBeneficiaryExtendedFields, optional
        :param beneficiary_optional_fields: Additional information about the beneficiary., defaults to None
        :type beneficiary_optional_fields: List[V1hosteddisbursebeneficiaryBeneficiaryOptionalFields], optional
        :param category: The category of payout method. One of the following: \<BR\> * **bank**\<BR\> * **card** - US only., defaults to None
        :type category: DisburseBeneficiaryBodyCategory, optional
        :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type complete_url: str, optional
        :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'.\<BR\> * When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param merchant_alias: Client's name., defaults to None
        :type merchant_alias: str, optional
        :param merchant_reference_id: Identifier defined by the client for reference purposes. Limit: 45 characters., defaults to None
        :type merchant_reference_id: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation. \<BR\> **Range**: 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param payout_currency: Currency accepted by the beneficiary’s bank account. Three-letter ISO 4217 code., defaults to None
        :type payout_currency: str, optional
        :param payout_method_types_exclude: List of payout methods that are excluded from display on the beneficiary tokenization page., defaults to None
        :type payout_method_types_exclude: List[dict], optional
        :param payout_method_types_include: Array of strings. List of payout methods that are displayed on the beneficiary tokenization page., defaults to None
        :type payout_method_types_include: List[dict], optional
        :param sender_country: The two-letter ISO 3166-1 ALPHA-2 code for the sender’s country.
        :type sender_country: str
        :param sender_currency: Currency paid from the sender’s wallet. Three-letter ISO 4217 code., defaults to None
        :type sender_currency: str, optional
        :param sender_entity_type: Type of entity for the sender.
        :type sender_entity_type: DisburseBeneficiaryBodySenderEntityType
        """
        self.beneficiary_country = self._define_str(
            "beneficiary_country", beneficiary_country, nullable=True
        )
        self.beneficiary_entity_type = self._enum_matching(
            beneficiary_entity_type,
            DisburseBeneficiaryBodyBeneficiaryEntityType.list(),
            "beneficiary_entity_type",
        )
        self.beneficiary_extended_fields = (
            self._enum_matching(
                beneficiary_extended_fields,
                DisburseBeneficiaryBodyBeneficiaryExtendedFields.list(),
                "beneficiary_extended_fields",
            )
            if beneficiary_extended_fields
            else None
        )
        self.beneficiary_optional_fields = self._define_list(
            beneficiary_optional_fields,
            V1hosteddisbursebeneficiaryBeneficiaryOptionalFields,
        )
        self.category = (
            self._enum_matching(
                category, DisburseBeneficiaryBodyCategory.list(), "category"
            )
            if category
            else None
        )
        self.complete_url = self._define_str(
            "complete_url", complete_url, nullable=True
        )
        self.language = self._define_str("language", language, nullable=True)
        self.merchant_alias = self._define_str(
            "merchant_alias", merchant_alias, nullable=True
        )
        self.merchant_reference_id = self._define_str(
            "merchant_reference_id", merchant_reference_id, nullable=True
        )
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.payout_currency = self._define_str(
            "payout_currency", payout_currency, nullable=True
        )
        self.payout_method_types_exclude = payout_method_types_exclude
        self.payout_method_types_include = payout_method_types_include
        self.sender_country = sender_country
        self.sender_currency = self._define_str(
            "sender_currency", sender_currency, nullable=True
        )
        self.sender_entity_type = self._enum_matching(
            sender_entity_type,
            DisburseBeneficiaryBodySenderEntityType.list(),
            "sender_entity_type",
        )
