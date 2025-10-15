from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import date, time
from utils import hashid_manager

class ReservationBase(BaseModel):
    reservation_date: date
    reservation_time: time
    treatment: Optional[str] = None
    cancel_date: Optional[date] = None
    deleted_flag: bool = False

class ReservationCreate(ReservationBase):
    pass


class ReservationCreateForAdmin(ReservationBase):
    medical_record_no: str

class Reservation(ReservationBase):
    id: str

    @field_validator('id', mode='before')
    @classmethod
    def encode_id(cls, v: Any) -> str:
        if isinstance(v, int):
            return hashid_manager.encode_id(v)
        return v

    class Config:
        from_attributes = True

class ReservationWithPatient(Reservation):
    patient: 'User'