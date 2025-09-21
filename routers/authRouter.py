from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session

from auth import authManager
from db.database import get_db
from entities.entities import TUser
from schemas import Token, User, UserUpdate, LineLoginRequest

router = APIRouter()

@router.post("/token/line", response_model=Token)
async def login_for_access_token_line(request: LineLoginRequest, db: Session = Depends(get_db)):
    """LINE ID로 사용자를 확인하고 액세스 토큰을 발급합니다."""
    user = authManager.get_user_by_line_id(db, request.line_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect lineId",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=authManager.TOKEN_ACCESS_EXPIRE_MINUTES)
    access_token = authManager.create_access_token(
        user=user,
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """사용자 로그인 및 액세스 토큰 발급"""
    # form_data.username is the login_id
    user = authManager.get_user(db, form_data.username)
    if not user or not authManager.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=authManager.TOKEN_ACCESS_EXPIRE_MINUTES)
    access_token = authManager.create_access_token(
        user=user,
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/users/me", response_model=User)
async def read_users_me(current_user: TUser = Depends(authManager.get_current_active_user)):
    """현재 로그인한 사용자 정보를 반환합니다. (토큰 인증 필요)"""
    return current_user

@router.put("/api/users/me", response_model=User)
async def update_users_me(user_update: UserUpdate, db: Session = Depends(get_db), current_user: TUser = Depends(authManager.get_current_active_user)):
    """현재 로그인한 사용자 정보를 업데이트합니다. (토큰 인증 필요)"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    return current_user

@router.get("/api/token/verify", status_code=status.HTTP_200_OK)
async def verify_token(current_user: TUser = Depends(authManager.get_current_user)):
    """
    Verifies the validity of the access token.
    Returns a success response if the token is valid, otherwise a 401 error.
    """
    return {"valid": True}
