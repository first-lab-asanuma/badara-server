from pydantic import BaseModel, model_validator
from typing import Optional, Any
from enums.user_type import UserType

class UserBase(BaseModel):
    email: str | None = None
    line_id: str | None = None
    login_id: str | None = None
    user_type: Optional[UserType]
    last_name: Optional[str]
    first_name: Optional[str]
    contact: Optional[str]

    @model_validator(mode='before')
    @classmethod
    def check_ids_based_on_user_type(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        user_type = data.get('user_type')

        if user_type == UserType.PATIENT:
            if not data.get('line_id'):
                raise ValueError('For patients, line_id is required.')
            if not data.get('last_name'):
                raise ValueError('For patients, last_name is required.')
            if not data.get('first_name'):
                raise ValueError('For patients, first_name is required.')
            if not data.get('contact'):
                raise ValueError('For patients, contact is required.')
        elif user_type == UserType.HOSPITAL_ADMIN:
            if not data.get('login_id'):
                raise ValueError('For hospital admins, login_id is required.')
            if not data.get('password'):
                raise ValueError('For hospital admins, password is required.')
            if not data.get('email'):
                raise ValueError('For hospital admins, email is required.')
            if not data.get('last_name'):
                raise ValueError('For hospital admins, last_name is required.')
            if not data.get('first_name'):
                raise ValueError('For hospital admins, first_name is required.')
            if not data.get('contact'):
                raise ValueError('For hospital admins, contact is required.')

        return data

class UserCreate(UserBase):
    pass

class PatientCreate(UserCreate):
    user_type: UserType = UserType.PATIENT
    hospital_code: Optional[str]

class HospitalAdminCreate(UserCreate):
    user_type: UserType = UserType.HOSPITAL_ADMIN
    password: str

class User(UserBase):
    id: int
    hospital_id: int
    medical_record_no: Optional[str] = None

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    contact: Optional[str] = None
    medical_record_no: Optional[str] = None
