from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from .user import User

class ReservationBase(BaseModel):
    reservation_date: date
    reservation_time: time
    treatment: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int

    class Config:
        orm_mode = True

class ReservationWithPatient(Reservation):
    patient: User
