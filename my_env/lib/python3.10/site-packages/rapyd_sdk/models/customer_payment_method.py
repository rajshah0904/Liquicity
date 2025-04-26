from __future__ import annotations
from typing import Union
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.one_of_base_model import OneOfBaseModel
from .category import Category
from .next_action import NextAction
from .bin_details import BinDetails


@JsonMap({"id_": "id", "type_": "type"})
class CustomerPaymentMethod1(BaseModel):
    """CustomerPaymentMethod1

    :param bic_swift: BIC (SWIFT) code for the bank account., defaults to None
    :type bic_swift: str, optional
    :param account_last4: Last four digits of the bank account number or IBAN (International Bank Account Number)., defaults to None
    :type account_last4: str, optional
    :param id_: ID of the Payment Method object. String starting with **card_** or **other_**., defaults to None
    :type id_: str, optional
    :param type_: Name of the payment method type. For example, **it_visa_card**. To get a list of payment methods for a country, use 'List Payment Methods by Country'., defaults to None
    :type type_: str, optional
    :param category: category, defaults to None
    :type category: Category, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param image: A URL to the image of the icon for the type of payment method. Response only, defaults to None
    :type image: str, optional
    :param webhook_url: Reserved. Response only, defaults to None
    :type webhook_url: str, optional
    :param supporting_documentation: Reserved. Response only., defaults to None
    :type supporting_documentation: str, optional
    :param next_action: Indicates the next action for completing the payment. Response only. One of the following values are - * 3d_verification - The next action is 3DS authentication. To simulate 3DS authentication in the sandbox, see Simulating 3DS Authentication. Relevant only to card payments. * pending_capture - The next action is pending the capture of the amount. Relevant only to card payments when the amount is not zero. * pending_confirmation - The next action is pending the confirmation for the payment. Relevant to all payment methods excluding card payment. * not_applicable - The payment has completed or the next action is not relevant., defaults to None
    :type next_action: NextAction, optional
    """

    def __init__(
        self,
        bic_swift: str = None,
        account_last4: str = None,
        id_: str = None,
        type_: str = None,
        category: Category = None,
        metadata: dict = None,
        image: str = None,
        webhook_url: str = None,
        supporting_documentation: str = None,
        next_action: NextAction = None,
    ):
        """CustomerPaymentMethod1

        :param bic_swift: BIC (SWIFT) code for the bank account., defaults to None
        :type bic_swift: str, optional
        :param account_last4: Last four digits of the bank account number or IBAN (International Bank Account Number)., defaults to None
        :type account_last4: str, optional
        :param id_: ID of the Payment Method object. String starting with **card_** or **other_**., defaults to None
        :type id_: str, optional
        :param type_: Name of the payment method type. For example, **it_visa_card**. To get a list of payment methods for a country, use 'List Payment Methods by Country'., defaults to None
        :type type_: str, optional
        :param category: category, defaults to None
        :type category: Category, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param image: A URL to the image of the icon for the type of payment method. Response only, defaults to None
        :type image: str, optional
        :param webhook_url: Reserved. Response only, defaults to None
        :type webhook_url: str, optional
        :param supporting_documentation: Reserved. Response only., defaults to None
        :type supporting_documentation: str, optional
        :param next_action: Indicates the next action for completing the payment. Response only. One of the following values are - * 3d_verification - The next action is 3DS authentication. To simulate 3DS authentication in the sandbox, see Simulating 3DS Authentication. Relevant only to card payments. * pending_capture - The next action is pending the capture of the amount. Relevant only to card payments when the amount is not zero. * pending_confirmation - The next action is pending the confirmation for the payment. Relevant to all payment methods excluding card payment. * not_applicable - The payment has completed or the next action is not relevant., defaults to None
        :type next_action: NextAction, optional
        """
        self.bic_swift = self._define_str("bic_swift", bic_swift, nullable=True)
        self.account_last4 = self._define_str(
            "account_last4", account_last4, nullable=True
        )
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.type_ = self._define_str("type_", type_, nullable=True)
        self.category = (
            self._enum_matching(category, Category.list(), "category")
            if category
            else None
        )
        self.metadata = metadata
        self.image = self._define_str("image", image, nullable=True)
        self.webhook_url = self._define_str("webhook_url", webhook_url, nullable=True)
        self.supporting_documentation = self._define_str(
            "supporting_documentation", supporting_documentation, nullable=True
        )
        self.next_action = (
            self._enum_matching(next_action, NextAction.list(), "next_action")
            if next_action
            else None
        )


@JsonMap({"id_": "id", "type_": "type"})
class CustomerPaymentMethod2(BaseModel):
    """CustomerPaymentMethod2

    :param last_name: Customer's last name., defaults to None
    :type last_name: str, optional
    :param first_name: Customer's first name., defaults to None
    :type first_name: str, optional
    :param id_: ID of the Payment Method object. String starting with **card_** or **other_**., defaults to None
    :type id_: str, optional
    :param type_: Name of the payment method type. For example, **it_visa_card**. To get a list of payment methods for a country, use 'List Payment Methods by Country'., defaults to None
    :type type_: str, optional
    :param category: category, defaults to None
    :type category: Category, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param image: A URL to the image of the icon for the type of payment method. Response only, defaults to None
    :type image: str, optional
    :param webhook_url: Reserved. Response only, defaults to None
    :type webhook_url: str, optional
    :param supporting_documentation: Reserved. Response only., defaults to None
    :type supporting_documentation: str, optional
    :param next_action: Indicates the next action for completing the payment. Response only. One of the following values are - * 3d_verification - The next action is 3DS authentication. To simulate 3DS authentication in the sandbox, see Simulating 3DS Authentication. Relevant only to card payments. * pending_capture - The next action is pending the capture of the amount. Relevant only to card payments when the amount is not zero. * pending_confirmation - The next action is pending the confirmation for the payment. Relevant to all payment methods excluding card payment. * not_applicable - The payment has completed or the next action is not relevant., defaults to None
    :type next_action: NextAction, optional
    """

    def __init__(
        self,
        last_name: str = None,
        first_name: str = None,
        id_: str = None,
        type_: str = None,
        category: Category = None,
        metadata: dict = None,
        image: str = None,
        webhook_url: str = None,
        supporting_documentation: str = None,
        next_action: NextAction = None,
    ):
        """CustomerPaymentMethod2

        :param last_name: Customer's last name., defaults to None
        :type last_name: str, optional
        :param first_name: Customer's first name., defaults to None
        :type first_name: str, optional
        :param id_: ID of the Payment Method object. String starting with **card_** or **other_**., defaults to None
        :type id_: str, optional
        :param type_: Name of the payment method type. For example, **it_visa_card**. To get a list of payment methods for a country, use 'List Payment Methods by Country'., defaults to None
        :type type_: str, optional
        :param category: category, defaults to None
        :type category: Category, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param image: A URL to the image of the icon for the type of payment method. Response only, defaults to None
        :type image: str, optional
        :param webhook_url: Reserved. Response only, defaults to None
        :type webhook_url: str, optional
        :param supporting_documentation: Reserved. Response only., defaults to None
        :type supporting_documentation: str, optional
        :param next_action: Indicates the next action for completing the payment. Response only. One of the following values are - * 3d_verification - The next action is 3DS authentication. To simulate 3DS authentication in the sandbox, see Simulating 3DS Authentication. Relevant only to card payments. * pending_capture - The next action is pending the capture of the amount. Relevant only to card payments when the amount is not zero. * pending_confirmation - The next action is pending the confirmation for the payment. Relevant to all payment methods excluding card payment. * not_applicable - The payment has completed or the next action is not relevant., defaults to None
        :type next_action: NextAction, optional
        """
        self.last_name = self._define_str("last_name", last_name, nullable=True)
        self.first_name = self._define_str("first_name", first_name, nullable=True)
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.type_ = self._define_str("type_", type_, nullable=True)
        self.category = (
            self._enum_matching(category, Category.list(), "category")
            if category
            else None
        )
        self.metadata = metadata
        self.image = self._define_str("image", image, nullable=True)
        self.webhook_url = self._define_str("webhook_url", webhook_url, nullable=True)
        self.supporting_documentation = self._define_str(
            "supporting_documentation", supporting_documentation, nullable=True
        )
        self.next_action = (
            self._enum_matching(next_action, NextAction.list(), "next_action")
            if next_action
            else None
        )


@JsonMap({"id_": "id", "type_": "type"})
class CustomerPaymentMethod3(BaseModel):
    """CustomerPaymentMethod3

    :param last4: Last four digits of the card or IBAN (International Bank Account Number)., defaults to None
    :type last4: str, optional
    :param acs_check: Results of the Access Control Server (ACS) check. Possible values: * pass *fail * unavailable *unchecked * Relevant to cards., defaults to None
    :type acs_check: str, optional
    :param cvv_check: Verification of the card’s CVV. Valid values: * pass * fail * unavailable *  unchecked, defaults to None
    :type cvv_check: str, optional
    :param bin_details: Bank Identification Number (BIN) details. Read-only. Object containing the following fields - * bin_number - BIN number * country - The two-letter ISO 3166-1 ALPHA-2 code for the country. Uppercase. * funding - Type of card funding. One of the following [credit, debit, prepaid, unknown] * bank - Name of the issuing bank. Relevant to cards, defaults to None
    :type bin_details: BinDetails, optional
    :param expiration_year: Year of expiration., defaults to None
    :type expiration_year: str, optional
    :param expiration_month: Month of expiration., defaults to None
    :type expiration_month: str, optional
    :param fingerprint_token: Hash of the card number, expiration date and CVV., defaults to None
    :type fingerprint_token: str, optional
    :param id_: ID of the Payment Method object. String starting with **card_** or **other_**., defaults to None
    :type id_: str, optional
    :param type_: Name of the payment method type. For example, **it_visa_card**. To get a list of payment methods for a country, use 'List Payment Methods by Country'., defaults to None
    :type type_: str, optional
    :param category: category, defaults to None
    :type category: Category, optional
    :param metadata: A JSON object defined by the client., defaults to None
    :type metadata: dict, optional
    :param image: A URL to the image of the icon for the type of payment method. Response only, defaults to None
    :type image: str, optional
    :param webhook_url: Reserved. Response only, defaults to None
    :type webhook_url: str, optional
    :param supporting_documentation: Reserved. Response only., defaults to None
    :type supporting_documentation: str, optional
    :param next_action: Indicates the next action for completing the payment. Response only. One of the following values are - * 3d_verification - The next action is 3DS authentication. To simulate 3DS authentication in the sandbox, see Simulating 3DS Authentication. Relevant only to card payments. * pending_capture - The next action is pending the capture of the amount. Relevant only to card payments when the amount is not zero. * pending_confirmation - The next action is pending the confirmation for the payment. Relevant to all payment methods excluding card payment. * not_applicable - The payment has completed or the next action is not relevant., defaults to None
    :type next_action: NextAction, optional
    """

    def __init__(
        self,
        last4: str = None,
        acs_check: str = None,
        cvv_check: str = None,
        bin_details: BinDetails = None,
        expiration_year: str = None,
        expiration_month: str = None,
        fingerprint_token: str = None,
        id_: str = None,
        type_: str = None,
        category: Category = None,
        metadata: dict = None,
        image: str = None,
        webhook_url: str = None,
        supporting_documentation: str = None,
        next_action: NextAction = None,
    ):
        """CustomerPaymentMethod3

        :param last4: Last four digits of the card or IBAN (International Bank Account Number)., defaults to None
        :type last4: str, optional
        :param acs_check: Results of the Access Control Server (ACS) check. Possible values: * pass *fail * unavailable *unchecked * Relevant to cards., defaults to None
        :type acs_check: str, optional
        :param cvv_check: Verification of the card’s CVV. Valid values: * pass * fail * unavailable *  unchecked, defaults to None
        :type cvv_check: str, optional
        :param bin_details: Bank Identification Number (BIN) details. Read-only. Object containing the following fields - * bin_number - BIN number * country - The two-letter ISO 3166-1 ALPHA-2 code for the country. Uppercase. * funding - Type of card funding. One of the following [credit, debit, prepaid, unknown] * bank - Name of the issuing bank. Relevant to cards, defaults to None
        :type bin_details: BinDetails, optional
        :param expiration_year: Year of expiration., defaults to None
        :type expiration_year: str, optional
        :param expiration_month: Month of expiration., defaults to None
        :type expiration_month: str, optional
        :param fingerprint_token: Hash of the card number, expiration date and CVV., defaults to None
        :type fingerprint_token: str, optional
        :param id_: ID of the Payment Method object. String starting with **card_** or **other_**., defaults to None
        :type id_: str, optional
        :param type_: Name of the payment method type. For example, **it_visa_card**. To get a list of payment methods for a country, use 'List Payment Methods by Country'., defaults to None
        :type type_: str, optional
        :param category: category, defaults to None
        :type category: Category, optional
        :param metadata: A JSON object defined by the client., defaults to None
        :type metadata: dict, optional
        :param image: A URL to the image of the icon for the type of payment method. Response only, defaults to None
        :type image: str, optional
        :param webhook_url: Reserved. Response only, defaults to None
        :type webhook_url: str, optional
        :param supporting_documentation: Reserved. Response only., defaults to None
        :type supporting_documentation: str, optional
        :param next_action: Indicates the next action for completing the payment. Response only. One of the following values are - * 3d_verification - The next action is 3DS authentication. To simulate 3DS authentication in the sandbox, see Simulating 3DS Authentication. Relevant only to card payments. * pending_capture - The next action is pending the capture of the amount. Relevant only to card payments when the amount is not zero. * pending_confirmation - The next action is pending the confirmation for the payment. Relevant to all payment methods excluding card payment. * not_applicable - The payment has completed or the next action is not relevant., defaults to None
        :type next_action: NextAction, optional
        """
        self.last4 = self._define_str("last4", last4, nullable=True)
        self.acs_check = self._define_str("acs_check", acs_check, nullable=True)
        self.cvv_check = self._define_str("cvv_check", cvv_check, nullable=True)
        self.bin_details = self._define_object(bin_details, BinDetails)
        self.expiration_year = self._define_str(
            "expiration_year", expiration_year, nullable=True
        )
        self.expiration_month = self._define_str(
            "expiration_month", expiration_month, nullable=True
        )
        self.fingerprint_token = self._define_str(
            "fingerprint_token", fingerprint_token, nullable=True
        )
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.type_ = self._define_str("type_", type_, nullable=True)
        self.category = (
            self._enum_matching(category, Category.list(), "category")
            if category
            else None
        )
        self.metadata = metadata
        self.image = self._define_str("image", image, nullable=True)
        self.webhook_url = self._define_str("webhook_url", webhook_url, nullable=True)
        self.supporting_documentation = self._define_str(
            "supporting_documentation", supporting_documentation, nullable=True
        )
        self.next_action = (
            self._enum_matching(next_action, NextAction.list(), "next_action")
            if next_action
            else None
        )


class CustomerPaymentMethodGuard(OneOfBaseModel):
    class_list = {
        "CustomerPaymentMethod1": CustomerPaymentMethod1,
        "CustomerPaymentMethod2": CustomerPaymentMethod2,
        "CustomerPaymentMethod3": CustomerPaymentMethod3,
    }


CustomerPaymentMethod = Union[
    CustomerPaymentMethod1, CustomerPaymentMethod2, CustomerPaymentMethod3
]
