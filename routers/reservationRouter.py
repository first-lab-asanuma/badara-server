from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from auth import authManager
from db.database import get_db, available_slots_data
from entities.entities import TReservation, TUser, THoliday
from schemas import Reservation, ReservationCreate, UserType, ReservationWithPatient

router = APIRouter()

# 30분 간격으로 오전 9시부터 오후 6시 30분까지 예약 가능 시간 기본값
DEFAULT_TIME_SLOTS = [
    (datetime.min + timedelta(hours=h, minutes=m)).time().strftime("%H:%M")
    for h in range(9, 19)
    for m in (0, 30)
]

@router.get("/api/reservations/available_slots")
async def get_available_slots(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """
    향후 15일간의 예약 가능한 시간 슬롯을 동적으로 생성하여 반환합니다.
    - 휴일 및 예약이 꽉 찬 날은 결과에서 완전히 제외됩니다.
    - 이미 예약된 시간은 제외됩니다.
    """
    today = date.today()
    date_range = [today + timedelta(days=i) for i in range(15)]
    
    # 1. Get holidays for the hospital
    holidays_query = db.query(THoliday.holiday_date).filter(
        THoliday.hospital_id == current_user.hospital_id,
        THoliday.holiday_date.in_(date_range)
    ).all()
    holiday_dates = {h[0] for h in holidays_query}

    # 2. Get existing reservations for the hospital
    reservations_query = db.query(TReservation.reservation_date, TReservation.reservation_time).filter(
        TReservation.hospital_id == current_user.hospital_id,
        TReservation.reservation_date.in_(date_range),
        TReservation.deleted_flag == False
    ).all()
    
    booked_slots = {}
    for r_date, r_time in reservations_query:
        if r_date not in booked_slots:
            booked_slots[r_date] = set()
        booked_slots[r_date].add(r_time.strftime("%H:%M"))

    # 3. Build the available slots dictionary, excluding holidays and fully booked days
    available_slots = {}
    for day in date_range:
        if day not in holiday_dates:
            day_str = day.strftime("%Y-%m-%d")
            all_slots = set(DEFAULT_TIME_SLOTS)
            day_booked_slots = booked_slots.get(day, set())
            available_day_slots = sorted(list(all_slots - day_booked_slots))
            
            # Only add the day to the output if there is at least one available slot
            if available_day_slots:
                available_slots[day_str] = available_day_slots
            
    return {"available_slots": available_slots}

@router.post("/api/reservations", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """새로운 예약을 생성합니다."""
    # user_id와 hospital_id는 토큰에서 가져오므로, 요청 본문에서 제거

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
        TReservation.user_id == current_user.id,
        TReservation.reservation_date == reservation.reservation_date,
        TReservation.reservation_time == reservation.reservation_time,
        TReservation.deleted_flag == False # 활성 예약만 고려
    ).first()

    if existing_reservation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have a reservation at this time.")

    # 새 예약 생성
    new_reservation = TReservation(
        **reservation.model_dump(),
        user_id=current_user.id,
        hospital_id=current_user.hospital_id
    )
    db.add(new_reservation);
    db.flush()
    db.refresh(new_reservation)
    return new_reservation

@router.get("/api/me/reservations", response_model=Optional[Reservation])
async def get_my_reservations(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """소속된 병원의 예약 중, 현재 로그인한 사용자의 가장 최근에 만든 예약(미래)을 반환합니다."""
    now = datetime.now()
    reservation = db.query(TReservation).filter(
        TReservation.user_id == current_user.id,
        TReservation.hospital_id == current_user.hospital_id,
        TReservation.deleted_flag == False,
        func.concat(TReservation.reservation_date, ' ', TReservation.reservation_time) > now.strftime('%Y-%m-%d %H:%M:%S')
    ).order_by(
        TReservation.created_at.desc()
    ).first()
    return reservation

@router.get("/api/reservations", response_model=List[ReservationWithPatient])
async def get_reservations(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """모든 예약 정보를 반환합니다. (관리자만 접근 가능) """
    if current_user.user_type not in [UserType.HOSPITAL_ADMIN, UserType.SYSTEM_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all reservations")
    
    query = db.query(TReservation).options(joinedload(TReservation.patient)).filter(TReservation.deleted_flag == False)
    
    if current_user.user_type == UserType.HOSPITAL_ADMIN:
        query = query.filter(TReservation.hospital_id == current_user.hospital_id)
        
    reservations = query.all()
    return reservations

@router.get("/api/hospital/reservations", response_model=List[ReservationWithPatient])
async def get_hospital_reservations(
    from_date: date = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
    to_date: date = Query(..., description="조회 종료일 (YYYY-MM-DD)"),
    include_cancelled: bool = Query(False, description="취소된 예약을 포함할지 여부"),
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """
    병원 측에서 사용하는 API로, 지정된 기간 동안의 예약 내역을 조회합니다.
    병원 관리자 또는 시스템 관리자만 접근 가능합니다.
    """
    # 병원 관리자 또는 시스템 관리자만 접근 가능
    if current_user.user_type not in [UserType.HOSPITAL_ADMIN, UserType.SYSTEM_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query = db.query(TReservation).options(joinedload(TReservation.patient)).filter(
        TReservation.hospital_id == current_user.hospital_id,
        TReservation.reservation_date.between(from_date, to_date)
    )

    if not include_cancelled:
        query = query.filter(TReservation.deleted_flag == False, TReservation.cancel_date.is_(None))

    reservations = query.order_by(TReservation.reservation_date, TReservation.reservation_time).all()
    
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
    
    # 접근 권한 확인
    is_patient_self = reservation.user_id == current_user.id
    is_system_admin = current_user.user_type == UserType.SYSTEM_ADMIN
    is_hospital_admin_in_own_hospital = (
        current_user.user_type == UserType.HOSPITAL_ADMIN and
        reservation.hospital_id == current_user.hospital_id
    )

    if not (is_patient_self or is_system_admin or is_hospital_admin_in_own_hospital):
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

    # 접근 권한 확인
    is_patient_self = reservation.user_id == current_user.id
    is_system_admin = current_user.user_type == UserType.SYSTEM_ADMIN
    is_hospital_admin_in_own_hospital = (
        current_user.user_type == UserType.HOSPITAL_ADMIN and
        reservation.hospital_id == current_user.hospital_id
    )

    if not (is_patient_self or is_system_admin or is_hospital_admin_in_own_hospital):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this reservation")

    reservation.deleted_flag = True
    reservation.cancel_date = date.today() # 취소일을 오늘 날짜로 설정
    return