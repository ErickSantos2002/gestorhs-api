"""
Schemas de Ordens de Serviço
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class SituacaoServicoEnum(str, Enum):
    ESPERA = "E"
    ANDAMENTO = "A"
    FINALIZADO = "F"
    CANCELADO = "C"


class OrdemServicoBase(BaseModel):
    empresa_id: int
    equipamento_empresa_id: int
    tipo_calibracao_id: Optional[int] = None
    caixa_id: Optional[int] = None
    observacoes: Optional[str] = None
    quantidade_pilhas: int = Field(0, ge=0)
    quantidade_sopradores: int = Field(0, ge=0)
    valor_servico: Decimal = Field(0, ge=0)
    valor_frete_envio: Decimal = Field(0, ge=0)
    valor_frete_retorno: Decimal = Field(0, ge=0)

    @field_validator('valor_servico', 'valor_frete_envio', 'valor_frete_retorno', mode='before')
    @classmethod
    def convert_int_to_decimal(cls, v):
        """Converte int para Decimal para evitar warnings de serialização"""
        if isinstance(v, int):
            return Decimal(str(v))
        return v


class OrdemServicoCreate(OrdemServicoBase):
    pass


class OrdemServicoUpdate(BaseModel):
    fase_id: Optional[int] = None
    tipo_calibracao_id: Optional[int] = None
    caixa_id: Optional[int] = None
    observacoes: Optional[str] = None
    quantidade_pilhas: Optional[int] = Field(None, ge=0)
    quantidade_sopradores: Optional[int] = Field(None, ge=0)
    data_envio: Optional[datetime] = None
    data_chegada: Optional[datetime] = None
    data_retorno: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
    codigo_envio: Optional[str] = None
    codigo_retorno: Optional[str] = None
    valor_servico: Optional[Decimal] = Field(None, ge=0)
    valor_frete_envio: Optional[Decimal] = Field(None, ge=0)
    valor_frete_retorno: Optional[Decimal] = Field(None, ge=0)
    pago: Optional[str] = Field(None, pattern="^[SN]$")
    recebido: Optional[str] = Field(None, pattern="^[SN]$")
    garantia: Optional[str] = Field(None, pattern="^[SN]$")

    @field_validator('valor_servico', 'valor_frete_envio', 'valor_frete_retorno', mode='before')
    @classmethod
    def convert_int_to_decimal(cls, v):
        """Converte int para Decimal para evitar warnings de serialização"""
        if v is not None and isinstance(v, int):
            return Decimal(str(v))
        return v


class OrdemServicoFinalizar(BaseModel):
    data_calibracao: datetime
    certificado_numero: str = Field(..., min_length=1)
    certificado_temperatura: Optional[str] = None
    certificado_pressao: Optional[str] = None
    teste_1: str = Field(..., min_length=1)
    teste_2: str = Field(..., min_length=1)
    teste_3: str = Field(..., min_length=1)
    teste_media: str = Field(..., min_length=1)
    situacao_calibracao: str = Field(..., min_length=1)
    certificado_texto: Optional[str] = None


class OrdemServicoResponse(OrdemServicoBase):
    id: int
    chave_acesso: str
    fase_id: Optional[int] = None
    checklist_arquivo: Optional[str] = None
    etiqueta_codigo: Optional[str] = None
    data_solicitacao: datetime
    data_envio: Optional[datetime] = None
    data_chegada: Optional[datetime] = None
    data_calibracao: Optional[datetime] = None
    data_retorno: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
    data_proxima_calibracao: Optional[date] = None
    certificado_texto: Optional[str] = None
    codigo_envio: Optional[str] = None
    codigo_retorno: Optional[str] = None
    certificado_numero: Optional[str] = None
    certificado_temperatura: Optional[str] = None
    certificado_pressao: Optional[str] = None
    teste_1: Optional[str] = None
    teste_2: Optional[str] = None
    teste_3: Optional[str] = None
    teste_media: Optional[str] = None
    situacao_calibracao: Optional[str] = None
    pdf_certificado: Optional[str] = None
    valor_total: Decimal
    pago: str
    recebido: str
    garantia: str
    situacao_servico: str
    arquivo_anexo: Optional[str] = None
    data_criacao: datetime
    data_atualizacao: datetime

    @field_validator('valor_total', mode='before')
    @classmethod
    def convert_valor_total(cls, v):
        """Converte int para Decimal para evitar warnings de serialização"""
        if isinstance(v, int):
            return Decimal(str(v))
        return v

    class Config:
        from_attributes = True


class OrdemServicoListResponse(BaseModel):
    id: int
    chave_acesso: str
    empresa_id: int
    equipamento_empresa_id: int
    fase_id: Optional[int] = None
    data_solicitacao: datetime
    data_calibracao: Optional[datetime] = None
    situacao_servico: str
    valor_total: Decimal
    pago: str

    @field_validator('valor_total', mode='before')
    @classmethod
    def convert_valor_total(cls, v):
        """Converte int para Decimal para evitar warnings de serialização"""
        if isinstance(v, int):
            return Decimal(str(v))
        return v

    class Config:
        from_attributes = True
