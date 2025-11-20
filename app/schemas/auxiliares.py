"""
Schemas para Entidades Auxiliares
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime


# ===== CATEGORIA =====
class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = None
    ativo: str = Field("S", pattern="^[SN]$")


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = None
    ativo: Optional[str] = Field(None, pattern="^[SN]$")


class CategoriaResponse(CategoriaBase):
    id: int
    data_cadastro: Optional[date] = None

    @field_validator('data_cadastro', mode='before')
    @classmethod
    def convert_datetime_to_date(cls, v):
        """Converte datetime para date se necessário"""
        if isinstance(v, datetime):
            return v.date()
        return v

    class Config:
        from_attributes = True


# ===== MARCA =====
class MarcaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    site: Optional[str] = Field(None, max_length=200)
    ativo: str = Field("S", pattern="^[SN]$")


class MarcaCreate(MarcaBase):
    pass


class MarcaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    site: Optional[str] = Field(None, max_length=200)
    ativo: Optional[str] = Field(None, pattern="^[SN]$")


class MarcaResponse(MarcaBase):
    id: int
    data_cadastro: Optional[date] = None

    @field_validator('data_cadastro', mode='before')
    @classmethod
    def convert_datetime_to_date(cls, v):
        """Converte datetime para date se necessário"""
        if isinstance(v, datetime):
            return v.date()
        return v

    class Config:
        from_attributes = True


# ===== SETOR =====
class SetorBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = None
    ativo: str = Field("S", pattern="^[SN]$")


class SetorCreate(SetorBase):
    pass


class SetorUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = None
    ativo: Optional[str] = Field(None, pattern="^[SN]$")


class SetorResponse(SetorBase):
    id: int

    class Config:
        from_attributes = True


# ===== FASE OS =====
class FaseOSBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=50)
    descricao: Optional[str] = None
    ordem: int = Field(..., ge=1)
    cor: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    ativo: str = Field("S", pattern="^[SN]$")


class FaseOSCreate(FaseOSBase):
    pass


class FaseOSUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=50)
    descricao: Optional[str] = None
    ordem: Optional[int] = Field(None, ge=1)
    cor: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    ativo: Optional[str] = Field(None, pattern="^[SN]$")


class FaseOSResponse(FaseOSBase):
    id: int

    class Config:
        from_attributes = True


# ===== TIPO CALIBRAÇÃO =====
class TipoCalibracaoBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = None
    valor_padrao: Optional[float] = Field(None, ge=0)
    prazo_dias: Optional[int] = Field(None, ge=1)
    ativo: str = Field("S", pattern="^[SN]$")


class TipoCalibracaoCreate(TipoCalibracaoBase):
    pass


class TipoCalibracaoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = None
    valor_padrao: Optional[float] = Field(None, ge=0)
    prazo_dias: Optional[int] = Field(None, ge=1)
    ativo: Optional[str] = Field(None, pattern="^[SN]$")


class TipoCalibracaoResponse(TipoCalibracaoBase):
    id: int

    class Config:
        from_attributes = True
