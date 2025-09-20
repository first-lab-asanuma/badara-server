from pydantic import BaseModel
from typing import Optional
from datetime import date, time

# Pydantic models (Schemas) for API data validation

# --- Base Schemas ---
# These are the base schemas with fields common to both creation and reading.

class UserBase(BaseModel):
    email: Optional[str] = None
    line_id: Optional[str] = None
    login_id: Optional[str] = None
    user_type: Optional[str] = '0' # 0: patient
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    contact: Optional[str] = None

class ReservationBase(BaseModel):
    user_id: int
    hospital_id: int
    reservation_date: date
    reservation_time: time
    treatment: Optional[str] = None

# --- Create Schemas ---
# These schemas are used when creating new records (e.g., in POST requests).
# They inherit from the base and add any additional required fields.

class UserCreate(UserBase):
    password: str # Require password on creation

class ReservationCreate(ReservationBase):
    pass # No extra fields needed for creation

# --- Read Schemas ---
# These schemas are used when reading data from the database (e.g., in GET responses).
# They include all fields to be returned to the client and have orm_mode enabled.

class User(UserBase):
    id: int
    hospital_id: int
    medical_record_no: Optional[str] = None

    class Config:
        orm_mode = True

class Reservation(ReservationBase):
    id: int

    class Config:
        orm_mode = True

# --- Other Schemas for specific use cases ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None # Corresponds to login_id

class LineLoginRequest(BaseModel):
    line_id: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    contact: Optional[str] = None