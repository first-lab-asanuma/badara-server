from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

import authManager
from db.database import db
from schemas.schemas import Reservation, ReservationCreate, User


router = APIRouter()

@router.get("/api/reservation/patient/{patient_id}", response_model=Optional[Reservation])
def get_reservation_by_patient_id(patient_id: int, current_user: User = Depends(authManager.get_current_active_user)):
    """환자 사용자 ID로 해당 환자의 예약을 조회합니다. (인증 필요)"""
    reservation = next((r for r in db["reservation"] if r["patient_id"] == patient_id), None)
    if not reservation:
        # 환자는 있지만 예약이 없는 경우 404 대신 None을 반환합니다.
        return None
    return reservation

@router.post("/api/reservation", response_model=Reservation, status_code=201)
def create_reservation(reservation: ReservationCreate, current_user: User = Depends(authManager.get_current_active_user)):
    """새로운 예약을 생성합니다. (인증 필요)"""
    # 환자 ID로 환자 정보 찾기 (이제 users_db에서 찾음)
    patient_user = next((u for u in db["users"].values() if u.get("id") == reservation.patient_id and u.get("role") == "patient"), None)
    if not patient_user:
        raise HTTPException(status_code=404, detail=f"Patient user with id {reservation.patient_id} not found")

    new_id = max([r["id"] for r in db["reservation"]] or [0]) + 1

    # Directly construct the dictionary with all fields
    final_reservation_data = {
        "id": new_id,
        "patient_id": reservation.patient_id,
        "date": reservation.date,
        "time": reservation.time,
        "phone": patient_user["phone"], # Get phone from user object
        "treatmentContent": reservation.treatmentContent
    }

    db["reservation"].append(final_reservation_data)
    print(f"--- RESERVATION DB INSERTED ---")
    print(db["reservation"])
    print(f"-------------------------------")
    print(f"--- DEBUG: final_reservation_data before Pydantic ---")
    print(final_reservation_data)
    print(f"----------------------------------------------------")
    return Reservation(**final_reservation_data)

# @router.delete("/api/reservation/{reservation_id}", status_code=204)
# def delete_reservation(reservation_id: int, current_user: User = Depends(authManager.get_current_active_user)):
#     """ID로 예약을 삭제합니다. (인증 필요)"""
#     reservation_index = next((i for i, r in enumerate(db["reservation"]) if r["id"] == reservation_id), None)
#
#     if reservation_index is None:
#         raise HTTPException(status_code=404, detail="Reservation not found")
#
#     db["reservation"].pop(reservation_index)
#     print(f"--- RESERVATION DB DELETED ---")
#     print(db["reservation"])
#     print(f"------------------------------")
#     # 성공 시에는 204 No Content이므로 별도의 메시지를 반환하지 않습니다.
#     return

@router.get("/api/reservable-schedule")
def get_reservable_schedule(current_user: User = Depends(authManager.get_current_active_user)):
    """인증 후 예약 가능한 일정 정보를 반환합니다."""
    return db["available_slots_data"]