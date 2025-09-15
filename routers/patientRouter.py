from fastapi import APIRouter, Depends, HTTPException, status

import authManager
from db.database import db
from schemas.schemas import User, PatientCreate

router = APIRouter()

@router.post("/api/users/patient", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_patient_user(user: PatientCreate):
    """새로운 환자(role="patient") 사용자를 등록합니다."""
    # TODO 同じ病院IDにLINEIDが重複しているのか確認。
    # if user.lineId in db["users"]:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Assign a new ID
    new_user_data = user.model_dump()
    new_user_data["id"] = max([u.get("id") for u in db["users"].values()] or [0]) + 1
    new_user_data["role"] = "patient"
    new_user_data["username"] = new_user_data["last_name"] + new_user_data["first_name"]
    db["users"][new_user_data["username"]] = new_user_data
    print(f"--- USER DB INSERTED ---")
    print(db["users"])
    print(new_user_data)
    print(f"--------------------------")
    return User(**new_user_data)


# @router.get("/api/users/patients", response_model=List[User])
# async def get_all_patients(current_user: User = Depends(authManager.get_current_active_user)):
#     """모든 환자(role="patient") 사용자 정보를 반환합니다. (인증 필요)"""
#     if current_user.role not in ["hospital_admin", "system_admin"]:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access patient list")
#
#     patients = [User(**user_data) for user_data in db["users"].values() if user_data.get("role") == "patient"]
#     return patients

# @router.get("/api/users/patient/{user_id}", response_model=User)
# async def get_patient_by_id(user_id: int, current_user: User = Depends(authManager.get_current_active_user)):
#     """ID로 특정 환자(role="patient") 사용자 정보를 조회합니다. (인증 필요)"""
#     if current_user.role not in ["hospital_admin", "system_admin"]:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access patient information")
#
#     user_data = next((u for u in db["users"].values() if u.get("id") == user_id and u.get("role") == "patient"), None)
#     if not user_data:
#         raise HTTPException(status_code=404, detail="Patient user not found")
#
#     return User(**user_data)

@router.put("/api/users/patient/{user_id}", response_model=User)
async def update_patient_info(user_id: int, user_update: User, current_user: User = Depends(authManager.get_current_active_user)):
    """ID로 환자(role="patient") 사용자 정보를 업데이트합니다. (인증 필요)"""
    if current_user.role not in ["hospital_admin", "system_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update patient information")

    for username, user_data in db["users"].items():
        if user_data.get("id") == user_id and user_data.get("role") == "patient":
            updated_user_data = user_update.model_dump(exclude_unset=True)
            # Ensure role cannot be changed to non-patient via this endpoint
            if "role" in updated_user_data and updated_user_data["role"] != "patient":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change user role via this endpoint")
            
            db["users"][username].update(updated_user_data)
            print(f"--- USER DB UPDATED ---")
            print(db["users"])
            print(f"--------------------------")
            return User(**db["users"][username])
    raise HTTPException(status_code=404, detail="Patient user not found")

@router.get("/api/me/id")
async def get_my_id(current_user: User = Depends(authManager.get_current_user)):
    """로그인한 사용자의 ID를 반환합니다. (토큰 인증 필요)"""
    return {"id": current_user.id}