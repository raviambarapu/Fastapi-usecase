from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from jose import JWTError,jwt

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services import auth as auth_services

from app.schemas.user import(UserCreate,UserResponse,TokenResponse)

from app.auth.jwt import create_access_token,SECRET_KEY,ALGORITHM

from app.models.user import User

#Limiter import
from fastapi import Request
from app.limiter import limiter


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse,status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register(data: UserCreate, db:Session = Depends(get_db)):

    return auth_services.register_user(db,data)

@router.post("/token",response_model=TokenResponse, summary="Login and receive an access token")
@limiter.limit("5/minute")
def login(request:Request, form: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    _ = request  # Required by the limiter; otherwise unused in the handler.

    return auth_services.login(db,form.username,form.password)


# refresh token endpoint
@router.post("/refresh",response_model=TokenResponse)
def refresh_token(refresh_token:str, db:Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token,SECRET_KEY,algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Not a refresh token")

        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid refresh token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.scalars(select(User).where(User.email == email)).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401,detail="User not found")

    new_access_token = create_access_token({"sub":user.email, "role":user.role})

    return TokenResponse(access_token=new_access_token)