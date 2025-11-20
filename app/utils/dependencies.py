"""
Dependências do FastAPI (autenticação, permissões, etc)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.usuario import Usuario
from app.utils.security import decode_token
from app.schemas.auth import TokenData

# Security scheme para JWT
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtém o usuário atual a partir do token JWT

    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise credentials_exception

    # Verificar se é access token
    if payload.get("type") != "access":
        raise credentials_exception

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # Buscar usuário no banco
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Verificar se usuário está ativo
    if user.ativo != "S":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    return user


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """Retorna usuário ativo"""
    return current_user


def require_perfil(*perfis_permitidos: str):
    """
    Dependency para verificar se usuário tem perfil adequado

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_perfil("admin"))])
        def admin_route():
            ...
    """
    def check_perfil(current_user: Usuario = Depends(get_current_user)):
        if current_user.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Perfis permitidos: {', '.join(perfis_permitidos)}"
            )
        return current_user
    return check_perfil


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Permite apenas usuários admin"""
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores"
        )
    return current_user


def require_gerente_ou_superior(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Permite gerentes e admins"""
    if current_user.perfil not in ["admin", "gerente"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas gerentes e administradores"
        )
    return current_user
