"""
Schemas do Dashboard
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class DashboardPrincipal(BaseModel):
    ordens_andamento: int
    clientes_atrasados: int
    calibracoes_atrasadas: int
    calibracoes_proximas: int
    ordens_finalizadas_30dias: int
    calibracoes_nao_fazer: int
    clientes_perdidos: int


class CardAndamento(BaseModel):
    id: int
    chave_acesso: str
    empresa: str
    equipamento: str
    fase: Optional[str] = None
    data_solicitacao: datetime
    dias_em_aberto: int

    class Config:
        from_attributes = True


class CardAtrasado(BaseModel):
    empresa_id: int
    empresa: str
    equipamento_id: int
    equipamento: str
    numero_serie: Optional[str] = None
    data_proxima_calibracao: date
    dias_atrasado: int

    class Config:
        from_attributes = True


class CardProximas(BaseModel):
    empresa_id: int
    empresa: str
    equipamento_id: int
    equipamento: str
    numero_serie: Optional[str] = None
    data_proxima_calibracao: date
    dias_para_vencer: int

    class Config:
        from_attributes = True


class CardFinalizada(BaseModel):
    id: int
    chave_acesso: str
    empresa: str
    equipamento: str
    data_calibracao: datetime
    valor_total: Decimal

    class Config:
        from_attributes = True


class GraficoMensal(BaseModel):
    mes: str
    ano: int
    total_ordens: int
    total_faturamento: Decimal


class GraficoFases(BaseModel):
    fase: str
    quantidade: int
