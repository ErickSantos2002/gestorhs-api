"""
Router de Dashboard
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.ordem_servico import OrdemServico
from app.models.equipamento import EquipamentoEmpresa
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.dashboard import (
    DashboardPrincipal,
    CardAndamento,
    CardAtrasado,
    CardProximas,
    CardFinalizada
)
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/principal", response_model=DashboardPrincipal)
def get_dashboard_principal(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Retorna métricas principais do dashboard (7 cards)
    """
    hoje = date.today()
    trinta_dias_atras = hoje - timedelta(days=30)

    # 1. Ordens em andamento
    ordens_andamento = db.query(OrdemServico).filter(
        OrdemServico.situacao_servico == "A"
    ).count()

    # 2. Clientes atrasados (com calibrações vencidas)
    clientes_atrasados = db.query(func.count(func.distinct(EquipamentoEmpresa.empresa_id))).filter(
        EquipamentoEmpresa.data_proxima_calibracao < hoje,
        EquipamentoEmpresa.ativo == "S",
        EquipamentoEmpresa.calibracao_recusada == "N"
    ).scalar()

    # 3. Calibrações atrasadas
    calibracoes_atrasadas = db.query(EquipamentoEmpresa).filter(
        EquipamentoEmpresa.data_proxima_calibracao < hoje,
        EquipamentoEmpresa.ativo == "S",
        EquipamentoEmpresa.calibracao_recusada == "N"
    ).count()

    # 4. Calibrações próximas (próximos 30 dias)
    trinta_dias_frente = hoje + timedelta(days=30)
    calibracoes_proximas = db.query(EquipamentoEmpresa).filter(
        and_(
            EquipamentoEmpresa.data_proxima_calibracao >= hoje,
            EquipamentoEmpresa.data_proxima_calibracao <= trinta_dias_frente
        ),
        EquipamentoEmpresa.ativo == "S",
        EquipamentoEmpresa.calibracao_recusada == "N"
    ).count()

    # 5. Ordens finalizadas últimos 30 dias
    ordens_finalizadas_30dias = db.query(OrdemServico).filter(
        OrdemServico.situacao_servico == "F",
        OrdemServico.data_calibracao >= trinta_dias_atras
    ).count()

    # 6. Calibrações "não vai fazer"
    calibracoes_nao_fazer = db.query(EquipamentoEmpresa).filter(
        EquipamentoEmpresa.calibracao_recusada == "S",
        EquipamentoEmpresa.ativo == "S"
    ).count()

    # 7. Clientes perdidos
    clientes_perdidos = db.query(Empresa).filter(
        Empresa.status_contato == "perdido",
        Empresa.ativo == "S"
    ).count()

    return DashboardPrincipal(
        ordens_andamento=ordens_andamento,
        clientes_atrasados=clientes_atrasados,
        calibracoes_atrasadas=calibracoes_atrasadas,
        calibracoes_proximas=calibracoes_proximas,
        ordens_finalizadas_30dias=ordens_finalizadas_30dias,
        calibracoes_nao_fazer=calibracoes_nao_fazer,
        clientes_perdidos=clientes_perdidos
    )


@router.get("/andamento")
def get_ordens_andamento(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista ordens em andamento com detalhes"""
    ordens = db.query(OrdemServico).filter(
        OrdemServico.situacao_servico == "A"
    ).order_by(OrdemServico.data_solicitacao).limit(limit).all()

    cards = []
    for os in ordens:
        dias_em_aberto = (datetime.utcnow() - os.data_solicitacao).days

        cards.append({
            "id": os.id,
            "chave_acesso": os.chave_acesso,
            "empresa": os.empresa.razao_social if os.empresa else "",
            "equipamento": os.equipamento_empresa.equipamento.descricao if os.equipamento_empresa and os.equipamento_empresa.equipamento else "",
            "fase": os.fase.nome if os.fase else None,
            "data_solicitacao": os.data_solicitacao,
            "dias_em_aberto": dias_em_aberto
        })

    return {
        "success": True,
        "data": cards
    }


@router.get("/calibracoes-atrasadas")
def get_calibracoes_atrasadas(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista calibrações vencidas"""
    hoje = date.today()

    equipamentos = db.query(EquipamentoEmpresa).filter(
        EquipamentoEmpresa.data_proxima_calibracao < hoje,
        EquipamentoEmpresa.ativo == "S",
        EquipamentoEmpresa.calibracao_recusada == "N"
    ).order_by(EquipamentoEmpresa.data_proxima_calibracao).limit(limit).all()

    cards = []
    for eq in equipamentos:
        dias_atrasado = (hoje - eq.data_proxima_calibracao).days

        cards.append({
            "empresa_id": eq.empresa_id,
            "empresa": eq.empresa.razao_social if eq.empresa else "",
            "equipamento_id": eq.equipamento_id,
            "equipamento": eq.equipamento.descricao if eq.equipamento else "",
            "numero_serie": eq.numero_serie,
            "data_proxima_calibracao": eq.data_proxima_calibracao,
            "dias_atrasado": dias_atrasado
        })

    return {
        "success": True,
        "data": cards
    }


@router.get("/calibracoes-proximas")
def get_calibracoes_proximas(
    dias: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista calibrações próximas do vencimento"""
    hoje = date.today()
    data_limite = hoje + timedelta(days=dias)

    equipamentos = db.query(EquipamentoEmpresa).filter(
        and_(
            EquipamentoEmpresa.data_proxima_calibracao >= hoje,
            EquipamentoEmpresa.data_proxima_calibracao <= data_limite
        ),
        EquipamentoEmpresa.ativo == "S",
        EquipamentoEmpresa.calibracao_recusada == "N"
    ).order_by(EquipamentoEmpresa.data_proxima_calibracao).limit(limit).all()

    cards = []
    for eq in equipamentos:
        dias_para_vencer = (eq.data_proxima_calibracao - hoje).days

        cards.append({
            "empresa_id": eq.empresa_id,
            "empresa": eq.empresa.razao_social if eq.empresa else "",
            "equipamento_id": eq.equipamento_id,
            "equipamento": eq.equipamento.descricao if eq.equipamento else "",
            "numero_serie": eq.numero_serie,
            "data_proxima_calibracao": eq.data_proxima_calibracao,
            "dias_para_vencer": dias_para_vencer
        })

    return {
        "success": True,
        "data": cards
    }


@router.get("/finalizadas")
def get_ordens_finalizadas(
    dias: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista ordens finalizadas recentemente"""
    data_inicio = date.today() - timedelta(days=dias)

    ordens = db.query(OrdemServico).filter(
        OrdemServico.situacao_servico == "F",
        OrdemServico.data_calibracao >= data_inicio
    ).order_by(OrdemServico.data_calibracao.desc()).limit(limit).all()

    cards = []
    for os in ordens:
        cards.append({
            "id": os.id,
            "chave_acesso": os.chave_acesso,
            "empresa": os.empresa.razao_social if os.empresa else "",
            "equipamento": os.equipamento_empresa.equipamento.descricao if os.equipamento_empresa and os.equipamento_empresa.equipamento else "",
            "data_calibracao": os.data_calibracao,
            "valor_total": float(os.valor_total) if os.valor_total else 0
        })

    return {
        "success": True,
        "data": cards
    }


@router.get("/grafico-mensal")
def get_grafico_mensal(
    meses: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Gráfico de OSs e faturamento por mês"""
    data_inicio = date.today() - timedelta(days=meses * 30)

    # Query agrupada por mês
    result = db.query(
        func.extract('year', OrdemServico.data_solicitacao).label('ano'),
        func.extract('month', OrdemServico.data_solicitacao).label('mes'),
        func.count(OrdemServico.id).label('total_ordens'),
        func.sum(OrdemServico.valor_total).label('total_faturamento')
    ).filter(
        OrdemServico.data_solicitacao >= data_inicio,
        OrdemServico.situacao_servico != "C"
    ).group_by('ano', 'mes').order_by('ano', 'mes').all()

    dados = []
    for row in result:
        dados.append({
            "ano": int(row.ano),
            "mes": int(row.mes),
            "total_ordens": row.total_ordens,
            "total_faturamento": float(row.total_faturamento or 0)
        })

    return {
        "success": True,
        "data": dados
    }
