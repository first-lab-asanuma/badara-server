from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, time

import authManager
from db.database import get_db, available_slots_data
from models.models import TReservation, TUser
from schemas.schemas import Reservation, ReservationCreate

router = APIRouter()

@router.get("/api/reservations/available_slots")
async def get_available_slots(current_user: TUser = Depends(authManager.get_current_active_user)):
    """예약 가능한 시간 슬롯과 휴일 정보를 반환합니다."""
    # 이 데이터는 현재 db/database.py에 하드코딩되어 있습니다.
    # 실제 애플리케이션에서는 데이터베이스나 설정 파일에서 가져와야 합니다.
    return {"available_slots": available_slots_data["available_slots"]}

@router.post("/api/reservations", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """새로운 예약을 생성합니다."""
    # 예약하려는 user_id가 현재 사용자 본인이거나 관리자인지 확인
    if reservation.user_id != current_user.id and current_user.user_type not in ["1", "system_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create reservation for this user")

    # 요청된 날짜가 휴일인지 확인
    # if reservation.reservation_date.strftime("%Y-%m-%d") in holidays:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot make a reservation on a holiday.")

    # 요청된 시간 슬롯이 사용 가능한지 확인
    date_str = reservation.reservation_date.strftime("%Y-%m-%d")
    time_str = reservation.reservation_time.strftime("%H:%M")
    
    if date_str not in available_slots_data["available_slots"] or \
       time_str not in available_slots_data["available_slots"][date_str]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested time slot is not available.")

    # 동일한 사용자가 동일한 시간에 이미 예약했는지 확인
    existing_reservation = db.query(TReservation).filter(
        TReservation.user_id == reservation.user_id,
        TReservation.reservation_date == reservation.reservation_date,
        TReservation.reservation_time == reservation.reservation_time,
        TReservation.deleted_flag == False # 활성 예약만 고려
    ).first()

    if existing_reservation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have a reservation at this time.")

    # 새 예약 생성
    new_reservation = TReservation(
        **reservation.model_dump(),
        hospital_id=1 # Placeholder, 사용자/병원 컨텍스트에 따라 동적으로 설정되어야 함
    )
    db.add(new_reservation);
    db.commit()
    db.refresh(new_reservation)
    return new_reservation

@router.get("/api/reservations", response_model=List[Reservation])
async def get_reservations(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """모든 예약 정보를 반환합니다. (관리자만 접근 가능) """
    if current_user.user_type not in ["1", "system_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all reservations")
    
    reservations = db.query(TReservation).filter(TReservation.deleted_flag == False).all()
    return reservations

@router.get("/api/reservations/{reservation_id}", response_model=Reservation)
async def get_reservation_by_id(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """ID로 특정 예약 정보를 조회합니다."""
    reservation = db.query(TReservation).filter(TReservation.id == reservation_id, TReservation.deleted_flag == False).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    
    # 현재 사용자 본인이거나 관리자만 자신의 예약을 볼 수 있도록 허용
    if reservation.user_id != current_user.id and current_user.user_type not in ["1", "system_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this reservation")
        
    return reservation

@router.delete("/api/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """ID로 예약을 취소합니다."""
    reservation = db.query(TReservation).filter(TReservation.id == reservation_id, TReservation.deleted_flag == False).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    # 현재 사용자 본인이거나 관리자만 자신의 예약을 취소할 수 있도록 허용
    if reservation.user_id != current_user.id and current_user.user_type not in ["1", "system_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this reservation")

    reservation.deleted_flag = True
    reservation.cancel_date = date.today() # 취소일을 오늘 날짜로 설정
    db.commit()
    return