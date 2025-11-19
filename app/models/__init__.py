"""
Importacao de todos os models
"""
from app.models.usuario import Usuario
from app.models.empresa import Empresa, EmpresaHistorico
from app.models.equipamento import Equipamento, EquipamentoEmpresa
from app.models.ordem_servico import OrdemServico, Caixa
from app.models.auxiliares import Categoria, Marca, Setor, FaseOS, TipoCalibracao
from app.models.anexos import Documento, Foto, LogoEmpresa
from app.models.logs import LogSistema, LogOrdemServico

__all__ = [
    "Usuario",
    "Empresa",
    "EmpresaHistorico",
    "Equipamento",
    "EquipamentoEmpresa",
    "OrdemServico",
    "Caixa",
    "Categoria",
    "Marca",
    "Setor",
    "FaseOS",
    "TipoCalibracao",
    "Documento",
    "Foto",
    "LogoEmpresa",
    "LogSistema",
    "LogOrdemServico",
]
