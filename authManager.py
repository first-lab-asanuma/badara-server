from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional

from schemas.schemas import TokenData, User, UserInDB
from db.database import users_db

# 비밀 키, 알고리즘, 토큰 만료 시간 설정
# 이 SECRET_KEY는 외부에 노출되면 안 됩니다. 실제 운영 환경에서는 환경 변수로 관리해야 합니다.
TOKEN_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
TOKEN_ALGORITHM = "HS256"
TOKEN_ACCESS_EXPIRE_MINUTES = 30

# 비밀번호 해싱을 위한 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 스키마 정의, tokenUrl은 토큰을 얻기 위한 엔드포인트를 가리킵니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def verify_password(plain_password, hashed_password):
    """일반 비밀번호와 해시된 비밀번호를 비교합니다."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """비밀번호를 해시합니다."""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[UserInDB]:
    """데이터베이스에서 사용자를 찾습니다."""
    if username in users_db:
        user_dict = users_db[username]
        return UserInDB(**user_dict)
    return None

def get_user_by_line_id(line_id: str) -> Optional[UserInDB]:
    """데이터베이스에서 lineId로 사용자를 찾습니다."""
    for user_dict in users_db.values():
        if user_dict.get("line_id") == line_id:
            print(user_dict)
            return UserInDB(**user_dict)
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """토큰을 디코딩하여 현재 사용자를 가져옵니다."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """현재 활성화된 사용자인지 확인합니다."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
