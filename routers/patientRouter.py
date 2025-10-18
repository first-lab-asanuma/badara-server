from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta

from auth import authManager
from db.database import get_db
from entities.entities import TUser, THospital, TReservation
from schemas import User, PatientCreate, UserUpdate, UserType, PatientWithReservations, PatientNameId, UserWithLastReserve, PatientListCursorResponse
from utils import hashid_manager
from utils import cursor as cursor_util

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

@router.put("/api/users/patient/{user_hash_id}", response_model=User)
async def update_patient_info(user_hash_id: str, user_update: UserUpdate, db: Session = Depends(get_db), current_user: TUser = Depends(authManager.get_current_active_user)):
    """ID로 환자(user_type="0") 사용자 정보를 업데이트합니다. (인증 필요)"""
    user_id = hashid_manager.decode_id(user_hash_id)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Patient user not found")

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


@router.get("/api/users/patient/{user_hash_id}", response_model=PatientWithReservations)
async def get_patient_by_id(user_hash_id: str, db: Session = Depends(get_db), current_user: TUser = Depends(authManager.get_current_active_user)):
    """ID로 환자(user_type=\"0\") 사용자 정보를 조회합니다. (인증 필요)"""
    user_id = hashid_manager.decode_id(user_hash_id)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Patient user not found")

    if current_user.user_type not in [UserType.HOSPITAL_ADMIN, UserType.SYSTEM_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view patient information")

    patient = db.query(TUser).filter(TUser.id == user_id, TUser.user_type == UserType.PATIENT).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient user not found")

    # 병원 관리자는 자기 병원 소속의 환자 정보만 조회 가능
    if current_user.user_type == UserType.HOSPITAL_ADMIN and patient.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this patient's information")

    reservations = db.query(TReservation).filter(TReservation.user_id == user_id).order_by(TReservation.reservation_date.desc(), TReservation.reservation_time.desc()).limit(10).all()

    patient_with_reservations = PatientWithReservations.model_validate(patient)
    patient_with_reservations.reservations = reservations

    return patient_with_reservations





@router.get("/api/me/patients", response_model=PatientListCursorResponse)
async def get_my_hospital_patients(
    limit: int = Query(1000, ge=1, le=2000),
    cursor: Optional[str] = Query(None),
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

    base_query = db.query(TUser).filter(
        TUser.hospital_id == current_user.hospital_id,
        TUser.user_type == UserType.PATIENT,
        TUser.deleted_flag == False
    )

    if cursor:
        try:
            cur = cursor_util.decode_cursor(cursor)
            c_last = cur.get('last_name')
            c_first = cur.get('first_name')
            c_id = int(cur.get('id')) if cur.get('id') is not None else None
            if c_last is None or c_first is None or c_id is None:
                raise ValueError('invalid cursor parts')
            base_query = base_query.filter(
                or_(
                    TUser.last_name > c_last,
                    and_(TUser.last_name == c_last, TUser.first_name > c_first),
                    and_(TUser.last_name == c_last, TUser.first_name == c_first, TUser.id > c_id)
                )
            )
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効なカーソルです。")

    patients = base_query.order_by(TUser.last_name, TUser.first_name, TUser.id).limit(limit + 1).all()

    result = []
    for p in patients:
        res_date = None
        if getattr(p, 'last_reserve_date', None) is not None:
            # 날짜만 반환: YYYY-MM-DD
            res_date = p.last_reserve_date.strftime('%Y-%m-%d %H:%M:%S')
        item = UserWithLastReserve.model_validate(p).model_dump()
        item.pop('email', None)
        item.pop('login_id', None)
        item['last_reserve_date'] = res_date
        result.append(item)

    hasnext = len(result) > limit
    next_cursor = None
    if hasnext:
        result = result[:limit]
        last = patients[limit - 1]
        next_cursor = cursor_util.encode_cursor({
            'last_name': last.last_name or '',
            'first_name': last.first_name or '',
            'id': last.id,
        })

    return {"patients": result, "hasnext": hasnext, "next_cursor": next_cursor}


@router.get("/api/me/patients/mrn-unconfirmed", response_model=List[PatientNameId])
async def list_mrn_unconfirmed_patients(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """
    활성 환자 중 `medical_record_no`가 미확정(NULL 또는 빈 문자열)인 사용자 목록을
    해당 환자의 `id`와 `name`만 포함하여 반환한다. 이름은 성+이름을 합친 문자열이다.
    """
    if current_user.user_type != UserType.HOSPITAL_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hospital administrators can query this resource"
        )

    rows = (
        db.query(TUser.id, TUser.last_name, TUser.first_name)
        .filter(
            TUser.hospital_id == current_user.hospital_id,
            TUser.user_type == UserType.PATIENT,
            TUser.deleted_flag == False,
            or_(TUser.medical_record_no == None, TUser.medical_record_no == "")
        )
        .order_by(TUser.last_name, TUser.first_name)
        .all()
    )

    return [
        {
            "id": hashid_manager.encode_id(r.id),
            "name": f"{(r.last_name or '')}{(r.first_name or '')}",
        }
        for r in rows
    ]


@router.get("/api/me/patients/by-mrn/{medical_record_no}", response_model=User)
async def get_patient_by_mrn(
    medical_record_no: str,
    db: Session = Depends(get_db),
    current_user: TUser = Depends(authManager.get_current_active_user)
):
    """
    병원 관리자가 자신의 병원에서 특정 `medical_record_no`로 환자 정보를 단건 조회한다.
    """
    if current_user.user_type != UserType.HOSPITAL_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only hospital administrators can query this resource")

    patient = db.query(TUser).filter(
        TUser.hospital_id == current_user.hospital_id,
        TUser.user_type == UserType.PATIENT,
        TUser.deleted_flag == False,
        TUser.medical_record_no == medical_record_no
    ).first()

    if not patient:
        # i18n에서日本語に変換される（MRNは表示しない）
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with medical record number '{medical_record_no}' not found in this hospital."
        )

    return patient

@router.get("/api/me/id")
async def get_my_id(current_user: TUser = Depends(authManager.get_current_user)):
    """로그인한 사용자의 ID를 반환합니다. (토큰 인증 필요)"""
    return {"id": hashid_manager.encode_id(current_user.id)}
