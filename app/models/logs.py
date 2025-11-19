"""
Models de Logs e Auditoria
"""
from sqlalchemy import Column, Integer, String, TEXT, CHAR, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class LogSistema(Base):
    __tablename__ = "logs_sistema"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_hora = Column(TIMESTAMP, server_default=func.now(), index=True)
    acao = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    entidade_tipo = Column(String(50))  # Tipo de entidade afetada
    entidade_id = Column(Integer)  # ID da entidade afetada
    descricao = Column(TEXT)
    dados_anteriores = Column(JSON)  # JSONB no PostgreSQL
    dados_novos = Column(JSON)  # JSONB no PostgreSQL
    ip_address = Column(String(45))  # IPv6 suportado
    user_agent = Column(String(500))

    # Relationships
    usuario = relationship("Usuario")

    def __repr__(self):
        return f"<LogSistema {self.acao} - {self.entidade_tipo}:{self.entidade_id}>"


class LogOrdemServico(Base):
    __tablename__ = "logs_ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_hora = Column(TIMESTAMP, server_default=func.now(), index=True)
    tipo_autor = Column(CHAR(1), default="S")  # S (Sistema), C (Cliente)
    acao = Column(String(50), nullable=False)
    descricao = Column(TEXT)

    # Relationships
    ordem_servico = relationship("OrdemServico", back_populates="logs")
    usuario = relationship("Usuario")

    def __repr__(self):
        return f"<LogOrdemServico OS:{self.ordem_servico_id} - {self.acao}>"
