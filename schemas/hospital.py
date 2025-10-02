import base64
from typing import Optional

from pydantic import BaseModel, field_validator


class HospitalBase(BaseModel):
    hospital_code: str
    name: str
    website: Optional[str] = None
    postal_code: str
    address: str
    phone: str
    fax: Optional[str] = None
    line_qr_code: str # Base64 encoded PNG data
    reservation_policy_header: Optional[str] = None
    reservation_policy_body: Optional[str] = None
    treatment: Optional[str] = None


class Hospital(HospitalBase):
    id: int

    @field_validator('line_qr_code', mode='before')
    @classmethod
    def convert_bytes_to_base64(cls, v: bytes) -> str:
        return base64.b64encode(v).decode('utf-8')

    class Config:
        orm_mode = True

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    line_qr_code: Optional[str] = None
    reservation_policy_header: Optional[str] = None
    reservation_policy_body: Optional[str] = None
    treatment: Optional[str] = None