"""
Schemas de Autenticação
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    senha: str = Field(..., min_length=1, max_length=72)  # Bcrypt limite


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Segundos


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    senha_nova: str = Field(..., min_length=6, max_length=72)


class TokenData(BaseModel):
    user_id: Optional[int] = None
    login: Optional[str] = None
    perfil: Optional[str] = None
