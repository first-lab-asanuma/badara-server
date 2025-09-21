from pydantic import BaseModel
from typing import Optional

class Hospital(BaseModel):
    id: int
    name: str
    website: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    line_qr_code: Optional[str] = None
    reservation_policy_header: Optional[str] = None
    reservation_policy_body: Optional[str] = None
    treatment: Optional[str] = None

    class Config:
        orm_mode = True
