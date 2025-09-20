from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

# Import new models, schemas, and db dependency
from models.models import TUser
from schemas.schemas import TokenData
from db.database import get_db

# --- Constants ---
TOKEN_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
TOKEN_ALGORITHM = "HS256"
TOKEN_ACCESS_EXPIRE_MINUTES = 30

# --- Security Utils ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def verify_password(plain_password, hashed_password):
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hashes a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt

# --- Database User Functions ---

def get_user(db: Session, login_id: str) -> Optional[TUser]:
    """Finds a user by login_id in the database."""
    return db.query(TUser).filter(TUser.login_id == login_id).first()

def get_user_by_line_id(db: Session, line_id: str) -> Optional[TUser]:
    """Finds a user by line_id in the database."""
    return db.query(TUser).filter(TUser.line_id == line_id).first()

# --- Authentication Dependencies ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> TUser:
    """Decodes token and returns the current user from DB."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        # The "sub" claim should now be the user's login_id
        login_id: str = payload.get("sub")
        if login_id is None:
            raise credentials_exception
        token_data = TokenData(username=login_id) # Using username field in TokenData for login_id
    except JWTError:
        raise credentials_exception
    
    user = get_user(db=db, login_id=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: TUser = Depends(get_current_user)) -> TUser:
    """Checks if the current user is active (not deleted)."""
    if current_user.deleted_flag:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user