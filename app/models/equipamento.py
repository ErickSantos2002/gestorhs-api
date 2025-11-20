"""
Models de Equipamentos e Equipamentos Empresa
"""
from sqlalchemy import (
    Column, Integer, String, TEXT, CHAR, DATE, TIMESTAMP, NUMERIC,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    codigo = Column(String(50), unique=True, index=True)
    descricao = Column(String(200), nullable=False, index=True)
    modelo = Column(String(100))
    detalhes = Column(TEXT)
    especificacoes_tecnicas = Column(TEXT)
    peso_calibracao = Column(NUMERIC(9, 3))
    periodo_calibracao_dias = Column(Integer, default=365)  # Padrão 365 dias
    preco_de = Column(NUMERIC(14, 2))
    preco_por = Column(NUMERIC(14, 2))
    custo = Column(NUMERIC(14, 2))
    peso = Column(NUMERIC(9, 3))
    estoque_atual = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=0)
    estoque_maximo = Column(Integer, default=0)
    imagem = Column(String(200))
    video_url = Column(String(200))
    tags = Column(TEXT)
    palavras_chave = Column(TEXT)
    descricao_seo = Column(String(200))
    ativo = Column(CHAR(1), default="S", nullable=False)
    destaque = Column(CHAR(1), default="N")
    visualizacoes = Column(Integer, default=0)
    data_cadastro = Column(DATE, server_default=func.now())
    data_criacao = Column(TIMESTAMP, server_default=func.now())
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    categoria = relationship("Categoria", back_populates="equipamentos")
    marca = relationship("Marca", back_populates="equipamentos")
    equipamentos_empresa = relationship("EquipamentoEmpresa", back_populates="equipamento")

    def __repr__(self):
        return f"<Equipamento {self.descricao} ({self.codigo})>"


class EquipamentoEmpresa(Base):
    __tablename__ = "equipamentos_empresa"
    __table_args__ = (
        UniqueConstraint('equipamento_id', 'numero_serie', name='uq_equipamento_serie'),
    )

    id = Column(Integer, primary_key=True, index=True)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id", ondelete="RESTRICT"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=False)
    numero_serie = Column(String(50))
    numero_patrimonio = Column(String(50))
    data_compra = Column(DATE)
    data_ultima_calibracao = Column(DATE)
    data_proxima_calibracao = Column(DATE, index=True)
    data_ultimo_aviso = Column(TIMESTAMP)
    os_atual_id = Column(Integer, ForeignKey("ordens_servico.id"))

    # Dados de calibração
    certificado_numero = Column(String(50))
    certificado_temperatura = Column(String(50))
    certificado_pressao = Column(String(50))
    teste_1 = Column(String(50))
    teste_2 = Column(String(50))
    teste_3 = Column(String(50))
    teste_media = Column(String(50))
    situacao_calibracao = Column(String(50))

    # Status
    status = Column(CHAR(1), default="A")  # A (Ativo), I (Inativo), M (Manutenção), B (Baixado)
    ativo = Column(CHAR(1), default="S", nullable=False)
    calibracao_recusada = Column(CHAR(1), default="N")  # Cliente não quer fazer calibração
    data_criacao = Column(TIMESTAMP, server_default=func.now())
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    equipamento = relationship("Equipamento", back_populates="equipamentos_empresa")
    empresa = relationship("Empresa", back_populates="equipamentos")
    ordens_servico = relationship("OrdemServico", back_populates="equipamento_empresa", foreign_keys="OrdemServico.equipamento_empresa_id")
    os_atual = relationship("OrdemServico", foreign_keys=[os_atual_id], post_update=True)

    def __repr__(self):
        return f"<EquipamentoEmpresa {self.numero_serie}>"
