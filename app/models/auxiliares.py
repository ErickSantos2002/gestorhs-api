"""
Models Auxiliares (Categorias, Marcas, Setores, Fases, Tipos)
"""
from sqlalchemy import Column, Integer, String, TEXT, CHAR, DATE, TIMESTAMP, NUMERIC
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(TEXT)
    ativo = Column(CHAR(1), default="S", nullable=False)
    data_cadastro = Column(DATE, server_default=func.now())

    # Relationships
    equipamentos = relationship("Equipamento", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria {self.nome}>"


class Marca(Base):
    __tablename__ = "marcas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    site = Column(String(200))
    ativo = Column(CHAR(1), default="S", nullable=False)
    data_cadastro = Column(DATE, server_default=func.now())

    # Relationships
    equipamentos = relationship("Equipamento", back_populates="marca")

    def __repr__(self):
        return f"<Marca {self.nome}>"


class Setor(Base):
    __tablename__ = "setores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(TEXT)
    ativo = Column(CHAR(1), default="S", nullable=False)

    def __repr__(self):
        return f"<Setor {self.nome}>"


class FaseOS(Base):
    __tablename__ = "fases_os"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    descricao = Column(TEXT)
    ordem = Column(Integer, nullable=False)  # Ordem sequencial das fases
    cor = Column(String(7))  # Cor hexadecimal #RRGGBB
    ativo = Column(CHAR(1), default="S", nullable=False)

    # Relationships
    ordens_servico = relationship("OrdemServico", back_populates="fase")

    def __repr__(self):
        return f"<FaseOS {self.ordem}. {self.nome}>"


class TipoCalibracao(Base):
    __tablename__ = "tipos_calibracao"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(TEXT)
    valor_padrao = Column(NUMERIC(14, 2))
    prazo_dias = Column(Integer)
    ativo = Column(CHAR(1), default="S", nullable=False)

    # Relationships
    ordens_servico = relationship("OrdemServico", back_populates="tipo_calibracao")

    def __repr__(self):
        return f"<TipoCalibracao {self.nome}>"
