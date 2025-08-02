from pydantic import BaseModel
from typing import Optional

class UserOut(BaseModel):
    id: str
    email: str

class TOSAcceptedIn(BaseModel):
    signed_agreement_id: str 

class RegisterIn(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # additional optional fields in future 