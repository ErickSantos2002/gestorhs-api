"""
Schemas de Usuários
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, time
from enum import Enum


class PerfilEnum(str, Enum):
    ADMIN = "admin"
    GERENTE = "gerente"
    TECNICO = "tecnico"
    ATENDENTE = "atendente"


class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    login: str = Field(..., min_length=3, max_length=20)
    sexo: Optional[str] = Field(None, pattern="^[MF]$")
    telefone: Optional[str] = Field(None, max_length=20)
    perfil: PerfilEnum = PerfilEnum.ATENDENTE
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None
    dias_trabalho: Optional[str] = Field(None, max_length=20)
    ativo: str = Field("S", pattern="^[SN]$")


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, max_length=72)  # Bcrypt limite
    permissoes: Optional[dict] = None
    alertas: Optional[dict] = None


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    sexo: Optional[str] = Field(None, pattern="^[MF]$")
    perfil: Optional[PerfilEnum] = None
    permissoes: Optional[dict] = None
    alertas: Optional[dict] = None
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None
    dias_trabalho: Optional[str] = None
    ativo: Optional[str] = Field(None, pattern="^[SN]$")


class UsuarioUpdateSenha(BaseModel):
    senha_atual: str = Field(..., min_length=6, max_length=72)
    senha_nova: str = Field(..., min_length=6, max_length=72)


class UsuarioResponse(UsuarioBase):
    id: int
    imagem: Optional[str] = None
    permissoes: Optional[dict] = None
    alertas: Optional[dict] = None
    ultimo_acesso: Optional[datetime] = None
    data_cadastro: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True


class UsuarioListResponse(BaseModel):
    id: int
    nome: str
    email: str
    login: str
    perfil: str
    ativo: str
    ultimo_acesso: Optional[datetime] = None

    class Config:
        from_attributes = True
