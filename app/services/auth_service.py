"""
Service de Autenticação
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.usuario import Usuario
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.config import settings


class AuthService:
    """Service para operações de autenticação"""

    @staticmethod
    def authenticate_user(db: Session, login: str, password: str) -> Usuario:
        """
        Autentica usuário com login e senha

        Args:
            db: Sessão do banco
            login: Login do usuário
            password: Senha em texto plano

        Returns:
            Usuário autenticado

        Raises:
            HTTPException: Se credenciais inválidas
        """
        user = db.query(Usuario).filter(Usuario.login == login).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login ou senha incorretos"
            )

        if not verify_password(password, user.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login ou senha incorretos"
            )

        if user.ativo != "S":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )

        # Atualizar último acesso
        user.ultimo_acesso = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def create_tokens(user: Usuario) -> dict:
        """
        Cria access token e refresh token para o usuário

        Args:
            user: Usuário autenticado

        Returns:
            Dict com access_token, refresh_token, token_type, expires_in
        """
        token_data = {
            "user_id": user.id,
            "login": user.login,
            "perfil": user.perfil
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"user_id": user.id})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Em segundos
        }

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """
        Renova access token usando refresh token

        Args:
            db: Sessão do banco
            refresh_token: Refresh token válido

        Returns:
            Novo access token

        Raises:
            HTTPException: Se refresh token inválido
        """
        payload = decode_token(refresh_token)

        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )

        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )

        # Buscar usuário
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user or user.ativo != "S":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo"
            )

        # Criar novo access token
        token_data = {
            "user_id": user.id,
            "login": user.login,
            "perfil": user.perfil
        }

        access_token = create_access_token(token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
