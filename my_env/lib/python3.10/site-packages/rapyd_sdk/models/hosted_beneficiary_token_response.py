from __future__ import annotations
from enum import Enum
from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .hosted_beneficiary_token_response_beneficiary_optional_fields import (
    HostedBeneficiaryTokenResponseBeneficiaryOptionalFields,
)
from .hosted_beneficiary_token_response_merchant_customer_support import (
    HostedBeneficiaryTokenResponseMerchantCustomerSupport,
)


class HostedBeneficiaryTokenResponseBeneficiaryEntityType(Enum):
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
                HostedBeneficiaryTokenResponseBeneficiaryEntityType._member_map_.values(),
            )
        )


class HostedBeneficiaryTokenResponseBeneficiaryExtendedFields(Enum):
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
                HostedBeneficiaryTokenResponseBeneficiaryExtendedFields._member_map_.values(),
            )
        )


class HostedBeneficiaryTokenResponseCategory(Enum):
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
                lambda x: x.value,
                HostedBeneficiaryTokenResponseCategory._member_map_.values(),
            )
        )


class HostedBeneficiaryTokenResponseEntityType(Enum):
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
                HostedBeneficiaryTokenResponseEntityType._member_map_.values(),
            )
        )


class HostedBeneficiaryTokenResponseSenderEntityType(Enum):
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
                HostedBeneficiaryTokenResponseSenderEntityType._member_map_.values(),
            )
        )


class HostedBeneficiaryTokenResponseStatus(Enum):
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
            map(
                lambda x: x.value,
                HostedBeneficiaryTokenResponseStatus._member_map_.values(),
            )
        )


@JsonMap({"id_": "id"})
class HostedBeneficiaryTokenResponse(BaseModel):
    """HostedBeneficiaryTokenResponse

    :param beneficiary_country: The two-letter ISO 3166-1 ALPHA-2 code for the country of the beneficiary’s bank account. The two-letter prefix of the payout method type matches the beneficiary country code., defaults to None
    :type beneficiary_country: str, optional
    :param beneficiary_currency: Currency accepted by the beneficiary’s bank account. Three-letter ISO 4217 code., defaults to None
    :type beneficiary_currency: str, optional
    :param beneficiary_entity_type: Type of entity for the beneficiary. One of the following:, defaults to None
    :type beneficiary_entity_type: HostedBeneficiaryTokenResponseBeneficiaryEntityType, optional
    :param beneficiary_extended_fields: When the value is **true**, the hosted tokenization page displays additional required fields.\<BR\> * Additional required fields when `beneficiary_entity_type` is **individual**: `address`, `city`, `country`, `date_of_birth`, `first_name`, `gender`, `identification_type`, `identification_value`, `last_name`, `nationality`. \<BR\> * Additional required fields when `beneficiary_entity_type` is **company**: `address`, `city`, `company_name`, `country`, `country_of_incorporation`, `date_of_incorporation`, `identification_type`, `identification_value`.\<BR\> For more information on the additional required fields, see 'Create Extended Beneficiary'.\<BR\> **Note**: Currently only available in the sandbox., defaults to None
    :type beneficiary_extended_fields: HostedBeneficiaryTokenResponseBeneficiaryExtendedFields, optional
    :param beneficiary_id: ID of the beneficiary. String starting with **beneficiary_**., defaults to None
    :type beneficiary_id: str, optional
    :param beneficiary_optional_fields: Additional information about the beneficiary., defaults to None
    :type beneficiary_optional_fields: List[HostedBeneficiaryTokenResponseBeneficiaryOptionalFields], optional
    :param beneficiary_validated: Indicates whether the beneficiary has been validated., defaults to None
    :type beneficiary_validated: bool, optional
    :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type cancel_url: str, optional
    :param category: The category of payout method. One of the following: \<BR\> * **bank**\<BR\> * **card** - US only., defaults to None
    :type category: HostedBeneficiaryTokenResponseCategory, optional
    :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
    :type complete_url: str, optional
    :param country: The two-letter ISO 3166-1 ALPHA-2 code for the beneficiary’s country. The two-letter prefix of the payout method type must match the beneficiary country code., defaults to None
    :type country: str, optional
    :param currency: Currency accepted by the beneficiary’s bank account. Three-letter ISO 4217 code., defaults to None
    :type currency: str, optional
    :param entity_type: Type of entity for the beneficiary. One of the following:, defaults to None
    :type entity_type: HostedBeneficiaryTokenResponseEntityType, optional
    :param expiration: The page expiration date in Unix time., defaults to None
    :type expiration: str, optional
    :param id_: ID of the beneficiary tokenization page. String starting with **hp_ben_**.The page expiration date in Unix time., defaults to None
    :type id_: str, optional
    :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'.\<BR\> * When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
    :type language: str, optional
    :param merchant_alias: Client's name., defaults to None
    :type merchant_alias: str, optional
    :param merchant_color: Color of the call-to-action (CTA) button on the hosted page.\<BR\> To configure this field, use the Client Portal., defaults to None
    :type merchant_color: str, optional
    :param merchant_customer_support: Contains details of the client’s customer support. To configure these fields, use the Client Portal., defaults to None
    :type merchant_customer_support: List[HostedBeneficiaryTokenResponseMerchantCustomerSupport], optional
    :param merchant_logo: URL for the image of the client's logo.\<BR\> To configure this field, use the Client Portal., defaults to None
    :type merchant_logo: str, optional
    :param merchant_reference_id: Identifier defined by the client for reference purposes. Limit: 45 characters., defaults to None
    :type merchant_reference_id: str, optional
    :param merchant_website: The URL where the customer is redirected after exiting the hosted page. \<BR\> Relevant when one or both of the following fields is unset:\<BR\> * `cancel_url` \<BR\> * `complete_url`\<BR\> To configure this field, use the Client Portal., defaults to None
    :type merchant_website: str, optional
    :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation. \<BR\> **Range**: 1 minute to 30 days., defaults to None
    :type page_expiration: float, optional
    :param payout_currency: Currency accepted by the beneficiary’s bank account. Three-letter ISO 4217 code., defaults to None
    :type payout_currency: str, optional
    :param payout_method_type: The payout method type selected by the customer. The two-letter prefix must match the beneficiary country code., defaults to None
    :type payout_method_type: str, optional
    :param payout_method_types_exclude: List of payout methods that are excluded from display on the beneficiary tokenization page., defaults to None
    :type payout_method_types_exclude: List[dict], optional
    :param payout_method_types_include: Array of strings. List of payout methods that are displayed on the beneficiary tokenization page., defaults to None
    :type payout_method_types_include: List[dict], optional
    :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
    :type redirect_url: str, optional
    :param sender_country: The two-letter ISO 3166-1 ALPHA-2 code for the sender’s country., defaults to None
    :type sender_country: str, optional
    :param sender_currency: Currency paid from the sender’s wallet. Three-letter ISO 4217 code., defaults to None
    :type sender_currency: str, optional
    :param sender_entity_type: Type of entity for the sender. One of the following:., defaults to None
    :type sender_entity_type: HostedBeneficiaryTokenResponseSenderEntityType, optional
    :param status: Status of the hosted page. One of the following:\<BR\>* **NEW** - The hosted page was created.\<BR\> * **DON** - Done. The beneficiary details were saved.\<BR\> * **EXP** - The hosted page expired., defaults to None
    :type status: HostedBeneficiaryTokenResponseStatus, optional
    :param timestamp: Timestamp for the request to create the beneficiary tokenization object page, in Unix time., defaults to None
    :type timestamp: str, optional
    :param tokenization_page: ID of the beneficiary tokenization page. String starting with **hp_ben_**., defaults to None
    :type tokenization_page: str, optional
    """

    def __init__(
        self,
        beneficiary_country: str = None,
        beneficiary_currency: str = None,
        beneficiary_entity_type: HostedBeneficiaryTokenResponseBeneficiaryEntityType = None,
        beneficiary_extended_fields: HostedBeneficiaryTokenResponseBeneficiaryExtendedFields = None,
        beneficiary_id: str = None,
        beneficiary_optional_fields: List[
            HostedBeneficiaryTokenResponseBeneficiaryOptionalFields
        ] = None,
        beneficiary_validated: bool = None,
        cancel_url: str = None,
        category: HostedBeneficiaryTokenResponseCategory = None,
        complete_url: str = None,
        country: str = None,
        currency: str = None,
        entity_type: HostedBeneficiaryTokenResponseEntityType = None,
        expiration: str = None,
        id_: str = None,
        language: str = None,
        merchant_alias: str = None,
        merchant_color: str = None,
        merchant_customer_support: List[
            HostedBeneficiaryTokenResponseMerchantCustomerSupport
        ] = None,
        merchant_logo: str = None,
        merchant_reference_id: str = None,
        merchant_website: str = None,
        page_expiration: float = None,
        payout_currency: str = None,
        payout_method_type: str = None,
        payout_method_types_exclude: List[dict] = None,
        payout_method_types_include: List[dict] = None,
        redirect_url: str = None,
        sender_country: str = None,
        sender_currency: str = None,
        sender_entity_type: HostedBeneficiaryTokenResponseSenderEntityType = None,
        status: HostedBeneficiaryTokenResponseStatus = None,
        timestamp: str = None,
        tokenization_page: str = None,
    ):
        """HostedBeneficiaryTokenResponse

        :param beneficiary_country: The two-letter ISO 3166-1 ALPHA-2 code for the country of the beneficiary’s bank account. The two-letter prefix of the payout method type matches the beneficiary country code., defaults to None
        :type beneficiary_country: str, optional
        :param beneficiary_currency: Currency accepted by the beneficiary’s bank account. Three-letter ISO 4217 code., defaults to None
        :type beneficiary_currency: str, optional
        :param beneficiary_entity_type: Type of entity for the beneficiary. One of the following:, defaults to None
        :type beneficiary_entity_type: HostedBeneficiaryTokenResponseBeneficiaryEntityType, optional
        :param beneficiary_extended_fields: When the value is **true**, the hosted tokenization page displays additional required fields.\<BR\> * Additional required fields when `beneficiary_entity_type` is **individual**: `address`, `city`, `country`, `date_of_birth`, `first_name`, `gender`, `identification_type`, `identification_value`, `last_name`, `nationality`. \<BR\> * Additional required fields when `beneficiary_entity_type` is **company**: `address`, `city`, `company_name`, `country`, `country_of_incorporation`, `date_of_incorporation`, `identification_type`, `identification_value`.\<BR\> For more information on the additional required fields, see 'Create Extended Beneficiary'.\<BR\> **Note**: Currently only available in the sandbox., defaults to None
        :type beneficiary_extended_fields: HostedBeneficiaryTokenResponseBeneficiaryExtendedFields, optional
        :param beneficiary_id: ID of the beneficiary. String starting with **beneficiary_**., defaults to None
        :type beneficiary_id: str, optional
        :param beneficiary_optional_fields: Additional information about the beneficiary., defaults to None
        :type beneficiary_optional_fields: List[HostedBeneficiaryTokenResponseBeneficiaryOptionalFields], optional
        :param beneficiary_validated: Indicates whether the beneficiary has been validated., defaults to None
        :type beneficiary_validated: bool, optional
        :param cancel_url: URL where the customer is redirected after pressing **Back to Website** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type cancel_url: str, optional
        :param category: The category of payout method. One of the following: \<BR\> * **bank**\<BR\> * **card** - US only., defaults to None
        :type category: HostedBeneficiaryTokenResponseCategory, optional
        :param complete_url: URL where the customer is redirected after pressing **Close** to exit the hosted page. This URL overrides the `merchant_website` URL. Does not support localhost URLs., defaults to None
        :type complete_url: str, optional
        :param country: The two-letter ISO 3166-1 ALPHA-2 code for the beneficiary’s country. The two-letter prefix of the payout method type must match the beneficiary country code., defaults to None
        :type country: str, optional
        :param currency: Currency accepted by the beneficiary’s bank account. Three-letter ISO 4217 code., defaults to None
        :type currency: str, optional
        :param entity_type: Type of entity for the beneficiary. One of the following:, defaults to None
        :type entity_type: HostedBeneficiaryTokenResponseEntityType, optional
        :param expiration: The page expiration date in Unix time., defaults to None
        :type expiration: str, optional
        :param id_: ID of the beneficiary tokenization page. String starting with **hp_ben_**.The page expiration date in Unix time., defaults to None
        :type id_: str, optional
        :param language: Determines the default language of the hosted page. For a list of values, see 'List Supported Languages'.\<BR\> * When this parameter is null, the language of the user's browser is used.\<BR\> * If the language of the user's browser cannot be determined, the default language is English., defaults to None
        :type language: str, optional
        :param merchant_alias: Client's name., defaults to None
        :type merchant_alias: str, optional
        :param merchant_color: Color of the call-to-action (CTA) button on the hosted page.\<BR\> To configure this field, use the Client Portal., defaults to None
        :type merchant_color: str, optional
        :param merchant_customer_support: Contains details of the client’s customer support. To configure these fields, use the Client Portal., defaults to None
        :type merchant_customer_support: List[HostedBeneficiaryTokenResponseMerchantCustomerSupport], optional
        :param merchant_logo: URL for the image of the client's logo.\<BR\> To configure this field, use the Client Portal., defaults to None
        :type merchant_logo: str, optional
        :param merchant_reference_id: Identifier defined by the client for reference purposes. Limit: 45 characters., defaults to None
        :type merchant_reference_id: str, optional
        :param merchant_website: The URL where the customer is redirected after exiting the hosted page. \<BR\> Relevant when one or both of the following fields is unset:\<BR\> * `cancel_url` \<BR\> * `complete_url`\<BR\> To configure this field, use the Client Portal., defaults to None
        :type merchant_website: str, optional
        :param page_expiration: End of the time when the customer can use the hosted page, in Unix time. If `page_expiration` is not set, the hosted page expires 14 days after creation. \<BR\> **Range**: 1 minute to 30 days., defaults to None
        :type page_expiration: float, optional
        :param payout_currency: Currency accepted by the beneficiary’s bank account. Three-letter ISO 4217 code., defaults to None
        :type payout_currency: str, optional
        :param payout_method_type: The payout method type selected by the customer. The two-letter prefix must match the beneficiary country code., defaults to None
        :type payout_method_type: str, optional
        :param payout_method_types_exclude: List of payout methods that are excluded from display on the beneficiary tokenization page., defaults to None
        :type payout_method_types_exclude: List[dict], optional
        :param payout_method_types_include: Array of strings. List of payout methods that are displayed on the beneficiary tokenization page., defaults to None
        :type payout_method_types_include: List[dict], optional
        :param redirect_url: URL of the hosted page that is shown to the customer., defaults to None
        :type redirect_url: str, optional
        :param sender_country: The two-letter ISO 3166-1 ALPHA-2 code for the sender’s country., defaults to None
        :type sender_country: str, optional
        :param sender_currency: Currency paid from the sender’s wallet. Three-letter ISO 4217 code., defaults to None
        :type sender_currency: str, optional
        :param sender_entity_type: Type of entity for the sender. One of the following:., defaults to None
        :type sender_entity_type: HostedBeneficiaryTokenResponseSenderEntityType, optional
        :param status: Status of the hosted page. One of the following:\<BR\>* **NEW** - The hosted page was created.\<BR\> * **DON** - Done. The beneficiary details were saved.\<BR\> * **EXP** - The hosted page expired., defaults to None
        :type status: HostedBeneficiaryTokenResponseStatus, optional
        :param timestamp: Timestamp for the request to create the beneficiary tokenization object page, in Unix time., defaults to None
        :type timestamp: str, optional
        :param tokenization_page: ID of the beneficiary tokenization page. String starting with **hp_ben_**., defaults to None
        :type tokenization_page: str, optional
        """
        self.beneficiary_country = self._define_str(
            "beneficiary_country", beneficiary_country, nullable=True
        )
        self.beneficiary_currency = self._define_str(
            "beneficiary_currency", beneficiary_currency, nullable=True
        )
        self.beneficiary_entity_type = (
            self._enum_matching(
                beneficiary_entity_type,
                HostedBeneficiaryTokenResponseBeneficiaryEntityType.list(),
                "beneficiary_entity_type",
            )
            if beneficiary_entity_type
            else None
        )
        self.beneficiary_extended_fields = (
            self._enum_matching(
                beneficiary_extended_fields,
                HostedBeneficiaryTokenResponseBeneficiaryExtendedFields.list(),
                "beneficiary_extended_fields",
            )
            if beneficiary_extended_fields
            else None
        )
        self.beneficiary_id = self._define_str(
            "beneficiary_id", beneficiary_id, nullable=True
        )
        self.beneficiary_optional_fields = self._define_list(
            beneficiary_optional_fields,
            HostedBeneficiaryTokenResponseBeneficiaryOptionalFields,
        )
        self.beneficiary_validated = beneficiary_validated
        self.cancel_url = self._define_str("cancel_url", cancel_url, nullable=True)
        self.category = (
            self._enum_matching(
                category, HostedBeneficiaryTokenResponseCategory.list(), "category"
            )
            if category
            else None
        )
        self.complete_url = self._define_str(
            "complete_url", complete_url, nullable=True
        )
        self.country = self._define_str("country", country, nullable=True)
        self.currency = self._define_str("currency", currency, nullable=True)
        self.entity_type = (
            self._enum_matching(
                entity_type,
                HostedBeneficiaryTokenResponseEntityType.list(),
                "entity_type",
            )
            if entity_type
            else None
        )
        self.expiration = self._define_str("expiration", expiration, nullable=True)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.language = self._define_str("language", language, nullable=True)
        self.merchant_alias = self._define_str(
            "merchant_alias", merchant_alias, nullable=True
        )
        self.merchant_color = self._define_str(
            "merchant_color", merchant_color, nullable=True
        )
        self.merchant_customer_support = self._define_list(
            merchant_customer_support,
            HostedBeneficiaryTokenResponseMerchantCustomerSupport,
        )
        self.merchant_logo = self._define_str(
            "merchant_logo", merchant_logo, nullable=True
        )
        self.merchant_reference_id = self._define_str(
            "merchant_reference_id", merchant_reference_id, nullable=True
        )
        self.merchant_website = self._define_str(
            "merchant_website", merchant_website, nullable=True
        )
        self.page_expiration = self._define_number(
            "page_expiration", page_expiration, nullable=True
        )
        self.payout_currency = self._define_str(
            "payout_currency", payout_currency, nullable=True
        )
        self.payout_method_type = self._define_str(
            "payout_method_type", payout_method_type, nullable=True
        )
        self.payout_method_types_exclude = payout_method_types_exclude
        self.payout_method_types_include = payout_method_types_include
        self.redirect_url = self._define_str(
            "redirect_url", redirect_url, nullable=True
        )
        self.sender_country = self._define_str(
            "sender_country", sender_country, nullable=True
        )
        self.sender_currency = self._define_str(
            "sender_currency", sender_currency, nullable=True
        )
        self.sender_entity_type = (
            self._enum_matching(
                sender_entity_type,
                HostedBeneficiaryTokenResponseSenderEntityType.list(),
                "sender_entity_type",
            )
            if sender_entity_type
            else None
        )
        self.status = (
            self._enum_matching(
                status, HostedBeneficiaryTokenResponseStatus.list(), "status"
            )
            if status
            else None
        )
        self.timestamp = self._define_str("timestamp", timestamp, nullable=True)
        self.tokenization_page = self._define_str(
            "tokenization_page", tokenization_page, nullable=True
        )
