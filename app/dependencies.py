from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.orm import Session

from jose import JWTError

from app.database import SessionLocal
from app.models.user import User
from app.auth.jwt import verify_access_token

from app.permissions import get_permissions

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate":"bearer"})

    try:
        token_data = verify_access_token(token)
    except JWTError:
        raise credentials_exception

    user = db.scalars(select(User).where(User.email == token_data.sub)).first()

    if user is None or not user.is_active:
        raise credentials_exception

    return user

def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Admin acess required")
    
    return current_user


def require_role(*allowed_roles:str):

    def check(current_user:User = Depends(get_current_user)) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires one of:{allowed_roles}")
        
        return current_user
    
    return check


def require_permission(permission:str):

    def check_permission(current_user:User = Depends(get_current_user)) -> User:
        user_permission = get_permissions(current_user.role)

        if permission not in user_permission:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Permission required: {permission}")
        
        return current_user
    
    return check_permission