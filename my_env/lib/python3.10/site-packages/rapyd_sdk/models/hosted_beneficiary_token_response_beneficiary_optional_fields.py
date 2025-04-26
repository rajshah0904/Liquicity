from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class HostedBeneficiaryTokenResponseBeneficiaryOptionalFields(BaseModel):
    """HostedBeneficiaryTokenResponseBeneficiaryOptionalFields

    :param company_name: The name of the beneficiary's company. Relevant to beneficiaries that are not individuals. If the request does not contain this information, the hosted page prompts the customer for it. \<BR\> If `beneficiary_entity_type` is **individual**, this field must be omitted., defaults to None
    :type company_name: str, optional
    :param first_name: The first name of the beneficiary. Relevant to individual beneficiaries. If the request does not contain this information, the redirect page prompts the customer for it., defaults to None
    :type first_name: str, optional
    :param identification_type: Type of identification document. When `entity_type` is **company**, this field must be **company_registered_number**. When `entity_type` is **individual**, one of the following values: \<\>BR\> * **drivers_license**\<BR\> * **identification_id** \<BR\> * **international_passport** \<BR\> * **residence_permit**\<BR\> * **social_security**\<BR\> * **work_permit** type: string, defaults to None
    :type identification_type: any, optional
    :param identification_value: The identification of the document mentioned in identification_type., defaults to None
    :type identification_value: str, optional
    :param last_name: The last name of the beneficiary. Relevant to individual beneficiaries. If the request does not contain this information, the redirect page prompts the customer for it., defaults to None
    :type last_name: str, optional
    """

    def __init__(
        self,
        company_name: str = None,
        first_name: str = None,
        identification_type: any = None,
        identification_value: str = None,
        last_name: str = None,
    ):
        """HostedBeneficiaryTokenResponseBeneficiaryOptionalFields

        :param company_name: The name of the beneficiary's company. Relevant to beneficiaries that are not individuals. If the request does not contain this information, the hosted page prompts the customer for it. \<BR\> If `beneficiary_entity_type` is **individual**, this field must be omitted., defaults to None
        :type company_name: str, optional
        :param first_name: The first name of the beneficiary. Relevant to individual beneficiaries. If the request does not contain this information, the redirect page prompts the customer for it., defaults to None
        :type first_name: str, optional
        :param identification_type: Type of identification document. When `entity_type` is **company**, this field must be **company_registered_number**. When `entity_type` is **individual**, one of the following values: \<\>BR\> * **drivers_license**\<BR\> * **identification_id** \<BR\> * **international_passport** \<BR\> * **residence_permit**\<BR\> * **social_security**\<BR\> * **work_permit** type: string, defaults to None
        :type identification_type: any, optional
        :param identification_value: The identification of the document mentioned in identification_type., defaults to None
        :type identification_value: str, optional
        :param last_name: The last name of the beneficiary. Relevant to individual beneficiaries. If the request does not contain this information, the redirect page prompts the customer for it., defaults to None
        :type last_name: str, optional
        """
        self.company_name = self._define_str(
            "company_name", company_name, nullable=True
        )
        self.first_name = self._define_str("first_name", first_name, nullable=True)
        self.identification_type = identification_type
        self.identification_value = self._define_str(
            "identification_value", identification_value, nullable=True
        )
        self.last_name = self._define_str("last_name", last_name, nullable=True)
