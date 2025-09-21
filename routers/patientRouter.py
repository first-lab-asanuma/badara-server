from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from auth import authManager
from db.database import get_db
from entities.entities import TUser, THospital
from schemas import User, PatientCreate, UserUpdate, UserType

router = APIRouter()

@router.post("/api/users/patient", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_patient_user(user: PatientCreate, db: Session = Depends(get_db)):
    """새로운 환자(user_type="0") 사용자를 등록합니다."""
    # 동일한 login_id를 가진 사용자가 있는지 확인
    # db_user = authManager.get_user(db, login_id=user.login_id)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Login ID already registered")

    hospital = db.query(THospital).filter(THospital.hospital_code == user.hospital_code, THospital.deleted_flag == False).first()
    new_user = TUser(
        **user.model_dump(exclude={'hospital_code'}),
        hospital_id=hospital.id
    )
    
    db.add(new_user)
    db.flush()
    db.refresh(new_user)
    
    return new_user

@router.put("/api/users/patient/{user_id}", response_model=User)
async def update_patient_info(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: TUser = Depends(authManager.get_current_active_user)):
    """ID로 환자(user_type="0") 사용자 정보를 업데이트합니다. (인증 필요)"""
    # user_type '1'이 병원 관리자라고 가정합니다.
    if current_user.user_type not in [UserType.HOSPITAL_ADMIN, UserType.SYSTEM_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update patient information")

    user_to_update = db.query(TUser).filter(TUser.id == user_id, TUser.user_type == UserType.PATIENT).first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="Patient user not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_to_update, key, value)
        
    db.refresh(user_to_update)
    
    return user_to_update

@router.get("/api/me/id")
async def get_my_id(current_user: TUser = Depends(authManager.get_current_user)):
    """로그인한 사용자의 ID를 반환합니다. (토큰 인증 필요)"""
    return {"id": current_user.id}
