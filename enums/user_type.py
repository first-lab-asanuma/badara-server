from enum import Enum

class UserType(str, Enum):
    PATIENT = "0"
    HOSPITAL_ADMIN = "1"
    SYSTEM_ADMIN = "system_admin"
