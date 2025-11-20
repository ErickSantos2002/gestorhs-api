"""
Schemas de Equipamentos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class EquipamentoBase(BaseModel):
    categoria_id: Optional[int] = None
    marca_id: Optional[int] = None
    codigo: str = Field(..., max_length=50)
    descricao: str = Field(..., min_length=3, max_length=200)
    modelo: Optional[str] = Field(None, max_length=100)
    detalhes: Optional[str] = None
    especificacoes_tecnicas: Optional[str] = None
    peso_calibracao: Optional[Decimal] = None
    periodo_calibracao_dias: int = Field(365, ge=1)
    preco_de: Optional[Decimal] = None
    preco_por: Optional[Decimal] = None
    custo: Optional[Decimal] = None
    peso: Optional[Decimal] = None
    estoque_minimo: int = Field(0, ge=0)
    estoque_maximo: int = Field(0, ge=0)
    tags: Optional[str] = None
    palavras_chave: Optional[str] = None
    descricao_seo: Optional[str] = Field(None, max_length=200)
    ativo: str = Field("S", pattern="^[SN]$")
    destaque: str = Field("N", pattern="^[SN]$")


class EquipamentoCreate(EquipamentoBase):
    pass


class EquipamentoUpdate(BaseModel):
    categoria_id: Optional[int] = None
    marca_id: Optional[int] = None
    codigo: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = Field(None, min_length=3, max_length=200)
    modelo: Optional[str] = None
    detalhes: Optional[str] = None
    especificacoes_tecnicas: Optional[str] = None
    peso_calibracao: Optional[Decimal] = None
    periodo_calibracao_dias: Optional[int] = Field(None, ge=1)
    preco_de: Optional[Decimal] = None
    preco_por: Optional[Decimal] = None
    custo: Optional[Decimal] = None
    peso: Optional[Decimal] = None
    estoque_minimo: Optional[int] = Field(None, ge=0)
    estoque_maximo: Optional[int] = Field(None, ge=0)
    tags: Optional[str] = None
    palavras_chave: Optional[str] = None
    descricao_seo: Optional[str] = None
    ativo: Optional[str] = Field(None, pattern="^[SN]$")
    destaque: Optional[str] = Field(None, pattern="^[SN]$")


class EquipamentoResponse(EquipamentoBase):
    id: int
    estoque_atual: int
    imagem: Optional[str] = None
    video_url: Optional[str] = None
    visualizacoes: int
    data_cadastro: date
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True


class EquipamentoListResponse(BaseModel):
    id: int
    codigo: str
    descricao: str
    modelo: Optional[str] = None
    categoria_id: Optional[int] = None
    marca_id: Optional[int] = None
    estoque_atual: int
    periodo_calibracao_dias: int
    ativo: str

    class Config:
        from_attributes = True


# Equipamentos Empresa

class EquipamentoEmpresaBase(BaseModel):
    equipamento_id: int
    empresa_id: int
    numero_serie: Optional[str] = Field(None, max_length=50)
    numero_patrimonio: Optional[str] = Field(None, max_length=50)
    data_compra: Optional[date] = None
    status: str = Field("A", pattern="^[AIMB]$")  # A, I, M, B
    ativo: str = Field("S", pattern="^[SN]$")
    calibracao_recusada: str = Field("N", pattern="^[SN]$")


class EquipamentoEmpresaCreate(EquipamentoEmpresaBase):
    pass


class EquipamentoEmpresaUpdate(BaseModel):
    numero_serie: Optional[str] = None
    numero_patrimonio: Optional[str] = None
    data_compra: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^[AIMB]$")
    ativo: Optional[str] = Field(None, pattern="^[SN]$")
    calibracao_recusada: Optional[str] = Field(None, pattern="^[SN]$")


class EquipamentoEmpresaResponse(EquipamentoEmpresaBase):
    id: int
    data_ultima_calibracao: Optional[date] = None
    data_proxima_calibracao: Optional[date] = None
    data_ultimo_aviso: Optional[datetime] = None
    os_atual_id: Optional[int] = None
    certificado_numero: Optional[str] = None
    situacao_calibracao: Optional[str] = None
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True
