from pwdlib import PasswordHash
from fastapi import Depends,HTTPException,status
from sqlmodel import Session,select
import jwt
from database import get_session
from datetime import datetime,timedelta,timezone
from models import User
from fastapi.security import OAuth2PasswordBearer

password_hash=PasswordHash.recommended()

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/token")
SECRET_KEY="my-super-secret-key-change-later"
ALGORITHM="HS256"
TOKEN_EXPIRE=30

def hash_password(password:str)->str:
    return password_hash.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return password_hash.verify(plain_password,hashed_password)

def get_user(username:str,session:Session):
    statement=select(User).where(User.username==username)

    return session.exec(statement).first()

def authenticate_user(username:str,password:str,session:Session):
    user=get_user(username,session)
    if not user:
        return None
    if not verify_password(password,user.password):
        return None
    return user

def create_access_token(username:str,role:str):
    expire=(datetime.now(timezone.utc)+timedelta(minutes=TOKEN_EXPIRE))
    payload={
        "sub":username,
        "role":role,
        "exp":expire}
    token=jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    return token

async def get_current_user(token:str=Depends(oauth2_scheme),session:Session=Depends(get_session)):
    credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail="could not validate credentials")
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get("sub")
        if username is None:
            raise credential_exception
    except jwt.InvalidTokenError:
        raise credential_exception
    user=get_user(username, session)
    if user is None:
        raise credential_exception
    return user

async def require_admin(current_user:User=Depends(get_current_user)):
    if current_user.role!="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Admin access required")
    return current_user

