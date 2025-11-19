"""
Model de Usuários
"""
from sqlalchemy import Column, Integer, String, CHAR, TIMESTAMP, TIME, JSON
from sqlalchemy.sql import func
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    login = Column(String(20), unique=True, nullable=False, index=True)
    senha = Column(String(255), nullable=False)  # Hash bcrypt
    imagem = Column(String(50))
    sexo = Column(CHAR(1))
    telefone = Column(String(20))
    permissoes = Column(JSON)  # JSONB no PostgreSQL
    perfil = Column(String(20), nullable=False, default="atendente")  # admin, gerente, tecnico, atendente
    alertas = Column(JSON)  # JSONB no PostgreSQL
    hora_inicio = Column(TIME)
    hora_fim = Column(TIME)
    dias_trabalho = Column(String(20))
    ativo = Column(CHAR(1), default="S", nullable=False)
    ultimo_acesso = Column(TIMESTAMP)
    data_cadastro = Column(TIMESTAMP, server_default=func.now())
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Usuario {self.nome} ({self.login})>"
