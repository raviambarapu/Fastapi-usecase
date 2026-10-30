from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)

class UserResponse(BaseModel):
    id: int
    email:str
    full_name: str
    role:str
    is_active:bool

class TokenResponse(BaseModel):
    access_token:str
    token_type: str = "bearer"
    refresh_token: str | None = None

class TokenData(BaseModel):
    sub:str
    role: str | None = None