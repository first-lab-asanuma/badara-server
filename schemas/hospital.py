import base64
from typing import Optional, Any, List
from datetime import date

from pydantic import BaseModel, field_validator

from utils import hashid_manager


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
    treatment: Optional[List[str]] = None


class Holiday(BaseModel):
    id: int
    holiday_date: date
    
    class Config:
        from_attributes = True


class HolidayCreate(BaseModel):
    holiday_date: date


class HolidayDelete(BaseModel):
    id: int

class Hospital(HospitalBase):
    id: str

    @field_validator('id', mode='before')
    @classmethod
    def encode_id(cls, v: Any) -> str:
        if isinstance(v, int):
            return hashid_manager.encode_id(v)
        return v

    @field_validator('line_qr_code', mode='before')
    @classmethod
    def convert_bytes_to_base64(cls, v: Any) -> str:
        if isinstance(v, bytes):
            return base64.b64encode(v).decode('utf-8')
        return v

    @field_validator('treatment', mode='before')
    @classmethod
    def split_treatment_to_list(cls, v: Any) -> Any:
        # DB에서 문자열로 온 경우 "," 기준 분리하여 리스트로 반환
        if v is None:
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip() != '']
        return v

    class Config:
        from_attributes = True

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
    treatment: Optional[List[str]] = None

    @field_validator('treatment', mode='before')
    @classmethod
    def validate_treatment_items(cls, v: Any) -> Any:
        # 업데이트 입력 시: 리스트가 아니거나, 비어있거나, 빈 항목이 포함되면 에러
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError('treatment must be a non-empty list of strings')
        trimmed = [str(item).strip() for item in v]
        if len(trimmed) == 0 or any(s == '' for s in trimmed):
            raise ValueError('treatment items cannot be empty')
        return trimmed
