from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr
    redirect_to: str = Field(min_length=1, max_length=2048)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
