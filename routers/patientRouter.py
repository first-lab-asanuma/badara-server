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
    hospital = db.query(THospital).filter(THospital.hospital_code == user.hospital_code, THospital.deleted_flag == False).first()
    if not hospital:
        raise HTTPException(status_code=400, detail="Hospital with the given code not found.")

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
    if current_user.user_type not in [UserType.HOSPITAL_ADMIN, UserType.SYSTEM_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update patient information")

    user_to_update = db.query(TUser).filter(TUser.id == user_id, TUser.user_type == UserType.PATIENT).first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="Patient user not found")

    # 병원 관리자는 자기 병원 소속의 환자 정보만 수정 가능
    if current_user.user_type == UserType.HOSPITAL_ADMIN and user_to_update.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this patient's information")

    update_data = user_update.model_dump(exclude_unset=True)

    # medical_record_no 중복 확인
    if 'medical_record_no' in update_data and update_data['medical_record_no'] is not None:
        existing_patient = db.query(TUser).filter(
            TUser.hospital_id == user_to_update.hospital_id,
            TUser.medical_record_no == update_data['medical_record_no'],
            TUser.id != user_id
        ).first()
        if existing_patient:
            raise HTTPException(status_code=400, detail="Medical record number already exists for another patient in this hospital.")

    for key, value in update_data.items():
        setattr(user_to_update, key, value)

    db.commit()
    db.refresh(user_to_update)
    
    return user_to_update

@router.get("/api/hospitals/{hospital_id}/patients", response_model=List[User])
async def get_hospital_patients(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """
    특정 병원의 환자 목록을 조회합니다.
    시스템 관리자는 모든 병원의 환자를 조회할 수 있으며,
    병원 관리자는 자신이 속한 병원의 환자만 조회할 수 있습니다.
    """
    # 권한 확인
    if current_user.user_type == UserType.HOSPITAL_ADMIN:
        if current_user.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view patients of other hospitals"
            )
    elif current_user.user_type != UserType.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view patient lists"
        )

    patients = db.query(TUser).filter(
        TUser.hospital_id == hospital_id,
        TUser.user_type == UserType.PATIENT,
        TUser.deleted_flag == False
    ).order_by(TUser.last_name, TUser.first_name).all()

    return patients

@router.get("/api/me/patients", response_model=List[User])
async def get_my_hospital_patients(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """
    현재 로그인한 병원 관리자가 속한 병원의 환자 목록을 조회합니다.
    """
    if current_user.user_type != UserType.HOSPITAL_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hospital administrators can view their hospital's patient list"
        )

    patients = db.query(TUser).filter(
        TUser.hospital_id == current_user.hospital_id,
        TUser.user_type == UserType.PATIENT,
        TUser.deleted_flag == False
    ).order_by(TUser.last_name, TUser.first_name).all()

    return patients

@router.get("/api/me/id")
async def get_my_id(current_user: TUser = Depends(authManager.get_current_user)):
    """로그인한 사용자의 ID를 반환합니다. (토큰 인증 필요)"""
    return {"id": current_user.id}
