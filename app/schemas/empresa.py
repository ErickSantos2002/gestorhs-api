"""
Schemas de Empresas
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class TipoPessoaEnum(str, Enum):
    JURIDICA = "J"
    FISICA = "F"


class StatusContatoEnum(str, Enum):
    ATIVO = "ativo"
    SEM_CONTATO = "sem_contato"
    INATIVO = "inativo"
    PERDIDO = "perdido"


class EmpresaBase(BaseModel):
    tipo_pessoa: TipoPessoaEnum
    cnpj: Optional[str] = Field(None, min_length=14, max_length=14)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    inscricao_estadual: Optional[str] = Field(None, max_length=20)
    inscricao_municipal: Optional[str] = Field(None, max_length=20)
    razao_social: str = Field(..., min_length=3, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)

    # Endereço
    cep: Optional[str] = Field(None, max_length=10)
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, pattern="^[A-Z]{2}$")

    # Contatos
    contato_nome: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    telefone_2: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    whatsapp_2: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    site: Optional[str] = Field(None, max_length=200)

    # Outros
    observacoes: Optional[str] = None
    palavras_chave: Optional[str] = Field(None, max_length=250)
    ativo: str = Field("S", pattern="^[SN]$")
    status_contato: StatusContatoEnum = StatusContatoEnum.ATIVO

    @field_validator('cnpj', 'cpf')
    def validar_documento(cls, v, info):
        tipo_pessoa = info.data.get('tipo_pessoa')
        if tipo_pessoa == 'J' and not v:
            raise ValueError('CNPJ é obrigatório para pessoa jurídica')
        if tipo_pessoa == 'F' and not v:
            raise ValueError('CPF é obrigatório para pessoa física')
        return v


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    tipo_pessoa: Optional[TipoPessoaEnum] = None
    cnpj: Optional[str] = Field(None, min_length=14, max_length=14)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    inscricao_estadual: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    razao_social: Optional[str] = Field(None, min_length=3, max_length=200)
    nome_fantasia: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, pattern="^[A-Z]{2}$")
    contato_nome: Optional[str] = None
    telefone: Optional[str] = None
    telefone_2: Optional[str] = None
    celular: Optional[str] = None
    whatsapp: Optional[str] = None
    whatsapp_2: Optional[str] = None
    email: Optional[EmailStr] = None
    site: Optional[str] = None
    observacoes: Optional[str] = None
    palavras_chave: Optional[str] = None
    ativo: Optional[str] = Field(None, pattern="^[SN]$")
    status_contato: Optional[StatusContatoEnum] = None
    data_ultima_visita: Optional[date] = None


class EmpresaResponse(EmpresaBase):
    id: int
    imagem: Optional[str] = None
    data_cadastro: date
    data_ultima_visita: Optional[date] = None
    usuario_cadastro_id: Optional[int] = None
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True


class EmpresaListResponse(BaseModel):
    id: int
    tipo_pessoa: str
    cnpj: Optional[str] = None
    cpf: Optional[str] = None
    razao_social: str
    nome_fantasia: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    ativo: str
    status_contato: str

    class Config:
        from_attributes = True


class EmpresaHistoricoResponse(BaseModel):
    id: int
    empresa_id: int
    razao_social: str
    tipo_operacao: str
    data_modificacao: datetime
    usuario_modificacao_id: Optional[int] = None

    class Config:
        from_attributes = True
