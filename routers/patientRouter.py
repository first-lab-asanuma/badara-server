from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import authManager
from db.database import get_db
from models.models import TUser
from schemas.schemas import User, UserCreate, UserUpdate

router = APIRouter()

@router.post("/api/users/patient", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_patient_user(user: UserCreate, db: Session = Depends(get_db)):
    """새로운 환자(user_type="0") 사용자를 등록합니다."""
    # 동일한 login_id를 가진 사용자가 있는지 확인
    db_user = authManager.get_user(db, login_id=user.login_id)
    if db_user:
        raise HTTPException(status_code=400, detail="Login ID already registered")

    # 비밀번호 해싱
    hashed_password = authManager.get_password_hash(user.password)
    
    # 새 TUser 객체 생성
    # 참고: hospital_id=1 로 하드코딩 되어있습니다. 
    # 추후 이 부분은 인증된 사용자의 병원 ID를 사용하는 등 적절한 방식으로 처리해야 합니다.
    new_user = TUser(
        **user.model_dump(exclude={'password'}), 
        password=hashed_password,
        hospital_id=1 # Placeholder
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.put("/api/users/patient/{user_id}", response_model=User)
async def update_patient_info(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: TUser = Depends(authManager.get_current_active_user)):
    """ID로 환자(user_type="0") 사용자 정보를 업데이트합니다. (인증 필요)"""
    # user_type '1'이 병원 관리자라고 가정합니다.
    if current_user.user_type not in ["1", "system_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update patient information")

    user_to_update = db.query(TUser).filter(TUser.id == user_id, TUser.user_type == '0').first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="Patient user not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_to_update, key, value)
        
    db.commit()
    db.refresh(user_to_update)
    
    return user_to_update

@router.get("/api/me/id")
async def get_my_id(current_user: TUser = Depends(authManager.get_current_user)):
    """로그인한 사용자의 ID를 반환합니다. (토큰 인증 필요)"""
    return {"id": current_user.id}
