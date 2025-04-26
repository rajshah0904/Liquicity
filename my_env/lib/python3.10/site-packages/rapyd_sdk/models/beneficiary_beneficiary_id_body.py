from enum import Enum
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class BeneficiaryBeneficiaryIdBodyGender(Enum):
    """An enumeration representing different categories.

    :cvar MALE: "male"
    :vartype MALE: str
    :cvar FEMALE: "female"
    :vartype FEMALE: str
    :cvar OTHER: "other"
    :vartype OTHER: str
    :cvar NOTAPPLICABLE: "not_applicable"
    :vartype NOTAPPLICABLE: str
    """

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    NOTAPPLICABLE = "not_applicable"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                BeneficiaryBeneficiaryIdBodyGender._member_map_.values(),
            )
        )


class BeneficiaryBeneficiaryIdBodyIdentificationType(Enum):
    """An enumeration representing different categories.

    :cvar DRIVERSLICENSE: "drivers_license"
    :vartype DRIVERSLICENSE: str
    :cvar IDENTIFICATIONID: "identification_id"
    :vartype IDENTIFICATIONID: str
    :cvar INTERNATIONALPASSPORT: "international_passport"
    :vartype INTERNATIONALPASSPORT: str
    :cvar RESIDENCEPERMIT: "residence_permit"
    :vartype RESIDENCEPERMIT: str
    :cvar SOCIALSECURITY: "social_security"
    :vartype SOCIALSECURITY: str
    :cvar WORKPERMIT: "work_permit"
    :vartype WORKPERMIT: str
    """

    DRIVERSLICENSE = "drivers_license"
    IDENTIFICATIONID = "identification_id"
    INTERNATIONALPASSPORT = "international_passport"
    RESIDENCEPERMIT = "residence_permit"
    SOCIALSECURITY = "social_security"
    WORKPERMIT = "work_permit"

    def list():
        """Lists all category values.

        :return: A list of all category values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                BeneficiaryBeneficiaryIdBodyIdentificationType._member_map_.values(),
            )
        )


@JsonMap({})
class BeneficiaryBeneficiaryIdBody(BaseModel):
    """BeneficiaryBeneficiaryIdBody

    :param address: Beneficiary's street address including the build number., defaults to None
    :type address: str, optional
    :param city: City of the beneficiary., defaults to None
    :type city: str, optional
    :param company_name: Name of the beneficiary company. Relevant when `entity_type` is **company**., defaults to None
    :type company_name: str, optional
    :param country: Country of the beneficiary. Two-letter ISO 3166-1 ALPHA-2 code. The two-letter prefix of the payout method type must match the beneficiary country code., defaults to None
    :type country: str, optional
    :param country_of_incorporation: The country where the company was registered. Two-letter ISO 3166-1 ALPHA-2 code. Relevant when `entity_type` is **company**., defaults to None
    :type country_of_incorporation: str, optional
    :param date_of_birth: Date of birth of the individual. Format: DD/MM/YYYY. Relevant when `entity_type` is **individual**., defaults to None
    :type date_of_birth: str, optional
    :param date_of_incorporation: The date when the company was registered. Format: DD/MM/YYYY. Relevant when `entity_type` is **company**., defaults to None
    :type date_of_incorporation: str, optional
    :param default_payout_method_type: The type of payout method for the beneficiary. The two-letter prefix must match the beneficiary country code., defaults to None
    :type default_payout_method_type: str, optional
    :param first_name: First name of the beneficiary. Relevant when `entity_type` is **individual**., defaults to None
    :type first_name: str, optional
    :param gender: Gender of the individual. Relevant when `entity_type` is **individual**., defaults to None
    :type gender: BeneficiaryBeneficiaryIdBodyGender, optional
    :param identification_type: Type of identification document for the beneficiary. When `entity_type` is **company**, this field must be**company_registered_number**. When `entity_type` is **individual**:, defaults to None
    :type identification_type: BeneficiaryBeneficiaryIdBodyIdentificationType, optional
    :param identification_value: Identification number on the document mentioned in `identification_type`., defaults to None
    :type identification_value: str, optional
    :param last_name: Family name of the beneficiary. Relevant when `entity_type` is **individual**. Required when `entity_type` is **individual**., defaults to None
    :type last_name: str, optional
    :param merchant_reference_id: ID defined by the client., defaults to None
    :type merchant_reference_id: str, optional
    :param nationality: The citizenship of the beneficiary. Two-letter ISO 3166-1 ALPHA-2 code for the country. To determine the code for a country, see 'List Countries'. Relevant when `entity_type` is **individual**., defaults to None
    :type nationality: str, optional
    """

    def __init__(
        self,
        address: str = None,
        city: str = None,
        company_name: str = None,
        country: str = None,
        country_of_incorporation: str = None,
        date_of_birth: str = None,
        date_of_incorporation: str = None,
        default_payout_method_type: str = None,
        first_name: str = None,
        gender: BeneficiaryBeneficiaryIdBodyGender = None,
        identification_type: BeneficiaryBeneficiaryIdBodyIdentificationType = None,
        identification_value: str = None,
        last_name: str = None,
        merchant_reference_id: str = None,
        nationality: str = None,
    ):
        """BeneficiaryBeneficiaryIdBody

        :param address: Beneficiary's street address including the build number., defaults to None
        :type address: str, optional
        :param city: City of the beneficiary., defaults to None
        :type city: str, optional
        :param company_name: Name of the beneficiary company. Relevant when `entity_type` is **company**., defaults to None
        :type company_name: str, optional
        :param country: Country of the beneficiary. Two-letter ISO 3166-1 ALPHA-2 code. The two-letter prefix of the payout method type must match the beneficiary country code., defaults to None
        :type country: str, optional
        :param country_of_incorporation: The country where the company was registered. Two-letter ISO 3166-1 ALPHA-2 code. Relevant when `entity_type` is **company**., defaults to None
        :type country_of_incorporation: str, optional
        :param date_of_birth: Date of birth of the individual. Format: DD/MM/YYYY. Relevant when `entity_type` is **individual**., defaults to None
        :type date_of_birth: str, optional
        :param date_of_incorporation: The date when the company was registered. Format: DD/MM/YYYY. Relevant when `entity_type` is **company**., defaults to None
        :type date_of_incorporation: str, optional
        :param default_payout_method_type: The type of payout method for the beneficiary. The two-letter prefix must match the beneficiary country code., defaults to None
        :type default_payout_method_type: str, optional
        :param first_name: First name of the beneficiary. Relevant when `entity_type` is **individual**., defaults to None
        :type first_name: str, optional
        :param gender: Gender of the individual. Relevant when `entity_type` is **individual**., defaults to None
        :type gender: BeneficiaryBeneficiaryIdBodyGender, optional
        :param identification_type: Type of identification document for the beneficiary. When `entity_type` is **company**, this field must be**company_registered_number**. When `entity_type` is **individual**:, defaults to None
        :type identification_type: BeneficiaryBeneficiaryIdBodyIdentificationType, optional
        :param identification_value: Identification number on the document mentioned in `identification_type`., defaults to None
        :type identification_value: str, optional
        :param last_name: Family name of the beneficiary. Relevant when `entity_type` is **individual**. Required when `entity_type` is **individual**., defaults to None
        :type last_name: str, optional
        :param merchant_reference_id: ID defined by the client., defaults to None
        :type merchant_reference_id: str, optional
        :param nationality: The citizenship of the beneficiary. Two-letter ISO 3166-1 ALPHA-2 code for the country. To determine the code for a country, see 'List Countries'. Relevant when `entity_type` is **individual**., defaults to None
        :type nationality: str, optional
        """
        self.address = self._define_str("address", address, nullable=True)
        self.city = self._define_str("city", city, nullable=True)
        self.company_name = self._define_str(
            "company_name", company_name, nullable=True
        )
        self.country = self._define_str("country", country, nullable=True)
        self.country_of_incorporation = self._define_str(
            "country_of_incorporation", country_of_incorporation, nullable=True
        )
        self.date_of_birth = self._define_str(
            "date_of_birth", date_of_birth, nullable=True
        )
        self.date_of_incorporation = self._define_str(
            "date_of_incorporation", date_of_incorporation, nullable=True
        )
        self.default_payout_method_type = self._define_str(
            "default_payout_method_type", default_payout_method_type, nullable=True
        )
        self.first_name = self._define_str("first_name", first_name, nullable=True)
        self.gender = (
            self._enum_matching(
                gender, BeneficiaryBeneficiaryIdBodyGender.list(), "gender"
            )
            if gender
            else None
        )
        self.identification_type = (
            self._enum_matching(
                identification_type,
                BeneficiaryBeneficiaryIdBodyIdentificationType.list(),
                "identification_type",
            )
            if identification_type
            else None
        )
        self.identification_value = self._define_str(
            "identification_value", identification_value, nullable=True
        )
        self.last_name = self._define_str("last_name", last_name, nullable=True)
        self.merchant_reference_id = self._define_str(
            "merchant_reference_id", merchant_reference_id, nullable=True
        )
        self.nationality = self._define_str("nationality", nationality, nullable=True)
