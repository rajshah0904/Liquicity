from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None = None
    tos_url: str | None = None
    kyc_status: str
    bridge_wallet_id: str | None = None

class TOSAcceptedIn(BaseModel):
    signed_agreement_id: str 

class RegisterIn(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    # additional optional fields in future 