from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

import authManager
from db.database import db
from schemas.schemas import Token, UserMe, LineLoginRequest, User, UserUpdate

router = APIRouter()

@router.post("/token/line", response_model=Token)
async def login_for_access_token_line(request: LineLoginRequest):
    """LINE ID로 사용자를 확인하고 액세스 토큰을 발급합니다."""
    user = authManager.get_user_by_line_id(request.line_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect lineId",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=authManager.TOKEN_ACCESS_EXPIRE_MINUTES)
    access_token = authManager.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """사용자 로그인 및 액세스 토큰 발급"""
    user = authManager.get_user(form_data.username)
    if not user or not authManager.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=authManager.TOKEN_ACCESS_EXPIRE_MINUTES)
    access_token = authManager.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/users/me", response_model=UserMe)
async def read_users_me(current_user: User = Depends(authManager.get_current_user)):
    """현재 로그인한 사용자 정보를 반환합니다. (토큰 인증 필요)"""
    return current_user

@router.put("/api/users/me", response_model=User)
async def update_users_me(user_update: UserUpdate, current_user: User = Depends(authManager.get_current_active_user)):
    """현재 로그인한 사용자 정보를 업데이트합니다. (토큰 인증 필요)"""
    user_data_in_db = db["users"][current_user.username]

    # Get the fields that were actually sent in the request
    update_data = user_update.model_dump(exclude_unset=True)

    # Update the user data in the database
    for key, value in update_data.items():
        user_data_in_db[key] = value

    db["users"][current_user.username] = user_data_in_db

    print(f"--- USER DB UPDATED (ME) ---")
    print(db["users"])
    print(f"--------------------------")

    return User(**user_data_in_db)

@router.get("/api/token/verify", status_code=status.HTTP_200_OK)
async def verify_token(current_user: User = Depends(authManager.get_current_user)):
    """
    Verifies the validity of the access token.
    Returns a success response if the token is valid, otherwise a 401 error.
    """
    return {"valid": True}