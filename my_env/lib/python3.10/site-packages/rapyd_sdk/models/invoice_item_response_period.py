from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


@JsonMap({})
class InvoiceItemResponsePeriod(BaseModel):
    """Defines the start and end of the time period that this invoice item refers to. Relevant when the invoice item refers to more than one day. Contains the following fields:

    :param start: First date in the period covered by the invoice, in Unix time. Response only., defaults to None
    :type start: str, optional
    :param end: Last date in the period covered by the invoice, in Unix time. Response only., defaults to None
    :type end: str, optional
    """

    def __init__(self, start: str = None, end: str = None):
        """Defines the start and end of the time period that this invoice item refers to. Relevant when the invoice item refers to more than one day. Contains the following fields:

        :param start: First date in the period covered by the invoice, in Unix time. Response only., defaults to None
        :type start: str, optional
        :param end: Last date in the period covered by the invoice, in Unix time. Response only., defaults to None
        :type end: str, optional
        """
        self.start = self._define_str("start", start, nullable=True)
        self.end = self._define_str("end", end, nullable=True)
