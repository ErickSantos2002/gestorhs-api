"""
Utilitarios de seguranca (JWT, hash de senha, etc)
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Contexto para hash de senhas com bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Gera hash bcrypt da senha
    Bcrypt tem limite de 72 bytes - trunca se necessario
    """
    # Truncar para 72 bytes se necessario
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha corresponde ao hash
    Bcrypt tem limite de 72 bytes - trunca se necessario
    """
    # Truncar para 72 bytes se necessario
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError as e:
        # Se o hash no banco esta corrompido, retornar False
        if "password cannot be longer than 72 bytes" in str(e):
            return False
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um access token JWT

    Args:
        data: Dados a serem incluidos no token
        expires_delta: Tempo de expiracao (padrao: 30 minutos)

    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Cria um refresh token JWT

    Args:
        data: Dados a serem incluidos no token

    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida um token JWT

    Args:
        token: Token JWT a ser decodificado

    Returns:
        Payload do token ou None se invalido
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_chave_acesso() -> str:
    """
    Gera uma chave de acesso unica de 12 caracteres para Ordem de Servico
    Formato: XXXX-XXXX-XXXX
    """
    import random
    import string

    chars = string.ascii_uppercase + string.digits
    parts = []
    for _ in range(3):
        part = ''.join(random.choices(chars, k=4))
        parts.append(part)

    return '-'.join(parts)
