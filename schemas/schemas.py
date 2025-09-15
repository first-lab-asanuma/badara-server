from pydantic import BaseModel
from typing import Optional

# --- 예약 관련 모델 ---

class ReservationBase(BaseModel):
    date: str
    time: str
    treatmentContent: Optional[str] = None

class ReservationCreate(ReservationBase):
    patient_id: int # User ID for the patient

class Reservation(BaseModel):
    id: int
    patient_id: int # User ID for the patient
    phone: str
    date: str
    time: str
    treatmentContent: Optional[str] = None

# --- 인증 및 사용자 관련 모델 ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: int # Add ID to User model
    line_id: str
    username: str
    email: str = None
    disabled: Optional[bool] = False
    role: str = "patient"
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]

class UserInDB(User):
    hashed_password: str = None

class UserMe(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]

class UserUpdate(BaseModel):
    email: str = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class PatientCreate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    line_id: Optional[str]

class LineLoginRequest(BaseModel):
    line_id: str
