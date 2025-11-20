"""
Model de Ordens de Serviço
"""
from sqlalchemy import (
    Column, Integer, String, TEXT, CHAR, DATE, TIMESTAMP, NUMERIC,
    ForeignKey, Computed
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=False)
    equipamento_empresa_id = Column(Integer, ForeignKey("equipamentos_empresa.id", ondelete="RESTRICT"), nullable=False)
    caixa_id = Column(Integer, ForeignKey("caixas.id"))
    fase_id = Column(Integer, ForeignKey("fases_os.id"))
    tipo_calibracao_id = Column(Integer, ForeignKey("tipos_calibracao.id"))

    chave_acesso = Column(String(20), unique=True, nullable=False, index=True)  # Para cliente acompanhar
    checklist_arquivo = Column(String(50))
    etiqueta_codigo = Column(String(50))
    quantidade_pilhas = Column(Integer, default=0)
    quantidade_sopradores = Column(Integer, default=0)

    # Datas do fluxo
    data_solicitacao = Column(TIMESTAMP, server_default=func.now())
    data_envio = Column(TIMESTAMP)
    data_chegada = Column(TIMESTAMP)
    data_calibracao = Column(TIMESTAMP)
    data_retorno = Column(TIMESTAMP)
    data_entrega = Column(TIMESTAMP)
    data_proxima_calibracao = Column(DATE)

    # Observações
    observacoes = Column(TEXT)
    certificado_texto = Column(TEXT)

    # Logística
    codigo_envio = Column(String(50))
    codigo_retorno = Column(String(50))

    # Dados de calibração
    certificado_numero = Column(String(50))
    certificado_temperatura = Column(String(50))
    certificado_pressao = Column(String(50))
    teste_1 = Column(String(50))
    teste_2 = Column(String(50))
    teste_3 = Column(String(50))
    teste_media = Column(String(50))
    situacao_calibracao = Column(String(50))
    pdf_certificado = Column(String(50))

    # Financeiro
    valor_servico = Column(NUMERIC(14, 2), default=0)
    valor_frete_envio = Column(NUMERIC(14, 2), default=0)
    valor_frete_retorno = Column(NUMERIC(14, 2), default=0)
    valor_total = Column(NUMERIC(14, 2), Computed("valor_servico + valor_frete_envio + valor_frete_retorno"))

    # Status
    pago = Column(CHAR(1), default="N")
    recebido = Column(CHAR(1), default="N")
    garantia = Column(CHAR(1), default="N")
    situacao_servico = Column(CHAR(1), default="E")  # E (Espera), A (Andamento), F (Finalizado), C (Cancelado)

    # Anexos
    arquivo_anexo = Column(String(50))

    # Timestamps
    data_criacao = Column(TIMESTAMP, server_default=func.now())
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    empresa = relationship("Empresa", back_populates="ordens_servico")
    equipamento_empresa = relationship("EquipamentoEmpresa", back_populates="ordens_servico", foreign_keys=[equipamento_empresa_id])
    caixa = relationship("Caixa", back_populates="ordens_servico")
    fase = relationship("FaseOS", back_populates="ordens_servico")
    tipo_calibracao = relationship("TipoCalibracao", back_populates="ordens_servico")
    logs = relationship("LogOrdemServico", back_populates="ordem_servico")

    def __repr__(self):
        return f"<OrdemServico {self.chave_acesso}>"


class Caixa(Base):
    __tablename__ = "caixas"

    id = Column(Integer, primary_key=True, index=True)
    data_criacao = Column(DATE, server_default=func.now())
    status = Column(CHAR(1), default="P")  # P (Pendente), A (Andamento), F (Finalizado)
    observacoes = Column(TEXT)
    data_atualizacao = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    ordens_servico = relationship("OrdemServico", back_populates="caixa")

    def __repr__(self):
        return f"<Caixa {self.id} - {self.status}>"
