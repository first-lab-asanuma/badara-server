from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from auth import authManager
from db.database import get_db
from entities.entities import THospital, TUser
from enums.user_type import UserType
from schemas import Hospital

router = APIRouter()

@router.get("/api/hospital/{hospital_code}", response_model=Optional[Hospital])
async def get_hospital_info(
    hospital_code: str,
    db: Session = Depends(get_db)
):
    """병원 공개 코드로 병원 정보를 조회합니다."""
    hospital = db.query(THospital).filter(THospital.hospital_code == hospital_code, THospital.deleted_flag == False).first()
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    
    return hospital

@router.get("/api/hospitals/me", response_model=Hospital)
async def get_my_hospital_info(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """
    현재 로그인한 사용자의 병원 정보를 조회합니다.
    """
    hospital = db.query(THospital).filter(THospital.id == current_user.hospital_id, THospital.deleted_flag == False).first()
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    
    return hospital

@router.put("/api/hospitals/me", response_model=Hospital)
async def update_my_hospital_info(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user),
    name: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    postal_code: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    fax: Optional[str] = Form(None),
    reservation_policy_header: Optional[str] = Form(None),
    reservation_policy_body: Optional[str] = Form(None),
    treatment: Optional[str] = Form(None),
    line_qr_code: Optional[UploadFile] = File(None)
):
    """
    현재 로그인한 사용자의 병원 정보를 업데이트합니다. (multipart/form-data)
    병원 관리자 또는 시스템 관리자만 접근 가능합니다.
    """
    if current_user.user_type not in [UserType.HOSPITAL_ADMIN, UserType.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update hospital information"
        )

    hospital_to_update = db.query(THospital).filter(THospital.id == current_user.hospital_id).first()

    if not hospital_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")

    update_data = {
        "name": name,
        "website": website,
        "postal_code": postal_code,
        "address": address,
        "phone": phone,
        "fax": fax,
        "reservation_policy_header": reservation_policy_header,
        "reservation_policy_body": reservation_policy_body,
        "treatment": treatment,
    }

    # Filter out fields that were not provided (are None)
    update_data = {k: v for k, v in update_data.items() if v is not None}

    if line_qr_code:
        qr_code_bytes = await line_qr_code.read()
        update_data["line_qr_code"] = qr_code_bytes

    for key, value in update_data.items():
        setattr(hospital_to_update, key, value)

    db.commit()
    db.refresh(hospital_to_update)

    return hospital_to_update
