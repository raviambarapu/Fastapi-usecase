import os

from datetime import timedelta, datetime, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError

from app.schemas.user import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data:dict, expires_delta:timedelta | None = None) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp":expire})

    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)


def verify_access_token(token: str) -> TokenData:

    payload = jwt.decode(token,SECRET_KEY, algorithms=ALGORITHM)

    sub = payload.get("sub")

    if sub is None:
        raise JWTError("Token missing subject")

    return TokenData(sub=sub, role=payload.get("role"))

def create_refresh_token(email:str) -> str:
    
    return create_access_token(data={"sub":email,"type":"refresh"}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))