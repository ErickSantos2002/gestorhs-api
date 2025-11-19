"""
Models de Anexos (Documentos, Fotos, Logos)
"""
from sqlalchemy import Column, Integer, String, TEXT, CHAR, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    entidade_tipo = Column(String(50), nullable=False)  # equipamento, ordem_servico, empresa
    entidade_id = Column(Integer, nullable=False)
    titulo = Column(String(200))
    nome_arquivo = Column(String(200), nullable=False)
    caminho_arquivo = Column(String(500), nullable=False)
    tipo_mime = Column(String(100))
    tamanho_bytes = Column(BigInteger)
    posicao = Column(Integer, default=0)
    data_upload = Column(TIMESTAMP, server_default=func.now())
    usuario_upload_id = Column(Integer, ForeignKey("usuarios.id"))

    # Relationships
    usuario_upload = relationship("Usuario")

    def __repr__(self):
        return f"<Documento {self.nome_arquivo} ({self.entidade_tipo})>"


class Foto(Base):
    __tablename__ = "fotos"

    id = Column(Integer, primary_key=True, index=True)
    entidade_tipo = Column(String(50), nullable=False)  # equipamento, equipamento_empresa, empresa, ordem_servico
    entidade_id = Column(Integer, nullable=False)
    nome_arquivo = Column(String(200), nullable=False)
    caminho_arquivo = Column(String(500), nullable=False)
    legenda = Column(String(500))
    posicao = Column(Integer, default=0)
    tipo_foto = Column(String(20), default="galeria")  # principal, galeria, detalhe
    data_upload = Column(TIMESTAMP, server_default=func.now())
    usuario_upload_id = Column(Integer, ForeignKey("usuarios.id"))

    # Relationships
    usuario_upload = relationship("Usuario")

    def __repr__(self):
        return f"<Foto {self.nome_arquivo} ({self.entidade_tipo})>"


class LogoEmpresa(Base):
    __tablename__ = "logos_empresas"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    nome_arquivo = Column(String(200), nullable=False)
    caminho_arquivo = Column(String(500), nullable=False)
    ativo = Column(CHAR(1), default="S", nullable=False)
    data_upload = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    empresa = relationship("Empresa")

    def __repr__(self):
        return f"<LogoEmpresa empresa_id={self.empresa_id}>"
