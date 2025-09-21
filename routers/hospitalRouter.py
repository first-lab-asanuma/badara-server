from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from db.database import get_db
from entities.entities import THospital
from schemas import Hospital

router = APIRouter()

@router.get("/api/hospital/{hospital_id}", response_model=Optional[Hospital])
async def get_hospital_info(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """ID로 병원 정보를 조회합니다."""
    hospital = db.query(THospital).filter(THospital.id == hospital_id, THospital.deleted_flag == False).first()
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    
    return hospital
