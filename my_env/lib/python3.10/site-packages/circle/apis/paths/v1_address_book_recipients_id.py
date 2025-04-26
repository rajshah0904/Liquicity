from circle.paths.v1_address_book_recipients_id.get import ApiForget
from circle.paths.v1_address_book_recipients_id.delete import ApiFordelete
from circle.paths.v1_address_book_recipients_id.patch import ApiForpatch


class V1AddressBookRecipientsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
