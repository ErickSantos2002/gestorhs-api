"""
Models de Empresas e Histórico
"""
from sqlalchemy import Column, Integer, String, CHAR, TEXT, DATE, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    tipo_pessoa = Column(CHAR(1), nullable=False)  # J (Jurídica) ou F (Física)
    cnpj = Column(CHAR(14), unique=True, index=True)
    cpf = Column(CHAR(11), unique=True, index=True)
    inscricao_estadual = Column(String(20))
    inscricao_municipal = Column(String(20))
    razao_social = Column(String(200), nullable=False, index=True)
    nome_fantasia = Column(String(200))

    # Endereço
    cep = Column(String(10))
    logradouro = Column(String(200))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(CHAR(2))

    # Contatos
    contato_nome = Column(String(100))
    telefone = Column(String(20))
    telefone_2 = Column(String(20))
    celular = Column(String(20))
    whatsapp = Column(String(20))
    whatsapp_2 = Column(String(20))
    email = Column(String(200))
    site = Column(String(200))

    # Outros
    observacoes = Column(TEXT)
    palavras_chave = Column(String(250))
    imagem = Column(String(50))
    ativo = Column(CHAR(1), default="S", nullable=False)
    status_contato = Column(String(20), default="ativo")  # ativo, sem_contato, inativo, perdido
    data_cadastro = Column(DATE, server_default=func.now())
    data_ultima_visita = Column(DATE)
    usuario_cadastro_id = Column(Integer, ForeignKey("usuarios.id"))
    data_criacao = Column(TIMESTAMP, server_default=func.now())
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    usuario_cadastro = relationship("Usuario", foreign_keys=[usuario_cadastro_id])
    equipamentos = relationship("EquipamentoEmpresa", back_populates="empresa")
    ordens_servico = relationship("OrdemServico", back_populates="empresa")

    def __repr__(self):
        return f"<Empresa {self.razao_social}>"


class EmpresaHistorico(Base):
    __tablename__ = "empresas_historico"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)

    # Cópia de todos os campos de Empresa
    tipo_pessoa = Column(CHAR(1))
    cnpj = Column(CHAR(14))
    cpf = Column(CHAR(11))
    inscricao_estadual = Column(String(20))
    inscricao_municipal = Column(String(20))
    razao_social = Column(String(200))
    nome_fantasia = Column(String(200))
    cep = Column(String(10))
    logradouro = Column(String(200))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(CHAR(2))
    contato_nome = Column(String(100))
    telefone = Column(String(20))
    telefone_2 = Column(String(20))
    celular = Column(String(20))
    whatsapp = Column(String(20))
    whatsapp_2 = Column(String(20))
    email = Column(String(200))
    site = Column(String(200))
    observacoes = Column(TEXT)
    palavras_chave = Column(String(250))
    imagem = Column(String(50))
    ativo = Column(CHAR(1))
    status_contato = Column(String(20))
    data_cadastro = Column(DATE)
    data_ultima_visita = Column(DATE)
    usuario_cadastro_id = Column(Integer)

    # Auditoria
    data_modificacao = Column(TIMESTAMP, server_default=func.now())
    usuario_modificacao_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo_operacao = Column(String(10))  # INSERT, UPDATE, DELETE

    # Relationships
    empresa = relationship("Empresa")
    usuario_modificacao = relationship("Usuario", foreign_keys=[usuario_modificacao_id])

    def __repr__(self):
        return f"<EmpresaHistorico empresa_id={self.empresa_id} op={self.tipo_operacao}>"
