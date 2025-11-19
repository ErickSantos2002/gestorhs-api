"""
Router de Autenticação
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, TokenRefreshRequest
from app.schemas.usuario import UsuarioResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_active_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Realiza login e retorna tokens de acesso

    - **login**: Login do usuário
    - **senha**: Senha do usuário
    """
    # Autenticar usuário
    user = AuthService.authenticate_user(db, credentials.login, credentials.senha)

    # Criar tokens
    tokens = AuthService.create_tokens(user)

    return tokens


@router.post("/refresh", response_model=dict)
def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Renova o access token usando o refresh token

    - **refresh_token**: Refresh token válido
    """
    tokens = AuthService.refresh_access_token(db, request.refresh_token)
    return tokens


@router.post("/logout")
def logout(current_user: Usuario = Depends(get_current_active_user)):
    """
    Realiza logout (apenas para consistência, token expira automaticamente)
    """
    return {
        "success": True,
        "message": "Logout realizado com sucesso"
    }


@router.get("/me", response_model=UsuarioResponse)
def get_current_user_info(current_user: Usuario = Depends(get_current_active_user)):
    """
    Retorna informações do usuário autenticado
    """
    return current_user
