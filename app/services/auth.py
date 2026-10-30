from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status


from app.models.user import User
from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token
from app.schemas.user import UserCreate,TokenResponse


def register_user(db:Session, data: UserCreate) -> User:

    print("EMAIL RECEIVED:", data.email)
    
    all_users = db.scalars(select(User)).all()
    
    print("All Users: ", all_users)

        
    existing = db.scalars(select(User).where(User.email == data.email)).first()

    print("Existing user: ",existing)
    print("PASSWORD LENGTH:", len(data.password))
    print("PASSWORD:", data.password)
    if existing:
        print("user found")
        raise HTTPException(status_code=409, detail="Email already registered")

    print("user not found")
    user = User(email = data.email, hashed_password = hash_password(data.password), full_name = data.full_name)




    db.add(user)
    db.commit()
    db.refresh(user)

    print("user created:", user)
    return user

def authenticate_user(db:Session, email:str, password:str) -> User:
    user = db.scalars(select(User).where(User.email == email)).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate":"Bearer"})

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disable")

    return user


def login(db:Session,email:str,password:str) -> TokenResponse:
    user = authenticate_user(db,email,password)

    access_token = create_access_token({"sub":user.email,"role":user.role})

    refresh_token = create_refresh_token(user.email)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

