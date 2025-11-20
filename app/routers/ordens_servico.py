"""
Router de Ordens de Serviço
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.ordem_servico import OrdemServico
from app.models.logs import LogOrdemServico
from app.models.usuario import Usuario
from app.schemas.ordem_servico import (
    OrdemServicoCreate,
    OrdemServicoUpdate,
    OrdemServicoFinalizar,
    OrdemServicoResponse,
    OrdemServicoListResponse
)
from app.services.os_service import OSService
from app.utils.dependencies import get_current_active_user
from app.utils.pagination import paginate

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])


@router.get("", response_model=dict)
def list_ordens_servico(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    empresa_id: Optional[int] = None,
    equipamento_empresa_id: Optional[int] = None,
    fase_id: Optional[int] = None,
    situacao_servico: Optional[str] = Query(None, pattern="^[EAFC]$"),
    pago: Optional[str] = Query(None, pattern="^[SN]$"),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista ordens de serviço com filtros"""
    query = db.query(OrdemServico)

    if empresa_id:
        query = query.filter(OrdemServico.empresa_id == empresa_id)
    if equipamento_empresa_id:
        query = query.filter(OrdemServico.equipamento_empresa_id == equipamento_empresa_id)
    if fase_id:
        query = query.filter(OrdemServico.fase_id == fase_id)
    if situacao_servico:
        query = query.filter(OrdemServico.situacao_servico == situacao_servico)
    if pago:
        query = query.filter(OrdemServico.pago == pago)
    if data_inicio:
        query = query.filter(OrdemServico.data_solicitacao >= data_inicio)
    if data_fim:
        query = query.filter(OrdemServico.data_solicitacao <= data_fim)

    query = query.order_by(OrdemServico.data_solicitacao.desc())
    result = paginate(query, page, size)

    return {
        "success": True,
        "data": {
            "items": [OrdemServicoListResponse.model_validate(os) for os in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    }


@router.get("/{os_id}", response_model=OrdemServicoResponse)
def get_ordem_servico(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Busca ordem de serviço por ID"""
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )
    return os


@router.get("/chave/{chave_acesso}", response_model=OrdemServicoResponse)
def get_ordem_servico_by_chave(
    chave_acesso: str,
    db: Session = Depends(get_db)
):
    """Busca ordem de serviço por chave de acesso (público para cliente)"""
    os = db.query(OrdemServico).filter(OrdemServico.chave_acesso == chave_acesso).first()
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )
    return os


@router.post("", response_model=OrdemServicoResponse, status_code=status.HTTP_201_CREATED)
def create_ordem_servico(
    os_data: OrdemServicoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Cria nova ordem de serviço"""
    os = OSService.create_ordem_servico(
        db,
        os_data.model_dump(),
        current_user.id
    )
    db.commit()
    db.refresh(os)

    return os


@router.put("/{os_id}", response_model=OrdemServicoResponse)
def update_ordem_servico(
    os_id: int,
    os_data: OrdemServicoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Atualiza ordem de serviço"""
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    # Não permitir editar se finalizada ou cancelada
    if os.situacao_servico in ["F", "C"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível editar ordem de serviço finalizada ou cancelada"
        )

    update_data = os_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(os, field, value)

    db.commit()
    db.refresh(os)

    return os


@router.delete("/{os_id}")
def cancel_ordem_servico(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Cancela ordem de serviço"""
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    if os.situacao_servico == "F":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar ordem de serviço finalizada"
        )

    os.situacao_servico = "C"
    os.fase_id = 8  # Cancelado

    # Registrar log
    log = LogOrdemServico(
        ordem_servico_id=os.id,
        usuario_id=current_user.id,
        tipo_autor="S",
        acao="CANCELAMENTO",
        descricao="Ordem de serviço cancelada"
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "message": "Ordem de serviço cancelada com sucesso"
    }


@router.patch("/{os_id}/fase")
def mudar_fase(
    os_id: int,
    nova_fase_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Muda fase da ordem de serviço"""
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    if os.situacao_servico in ["F", "C"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível mudar fase de ordem de serviço finalizada ou cancelada"
        )

    OSService.mudar_fase(db, os, nova_fase_id, current_user.id)
    db.commit()

    return {
        "success": True,
        "message": "Fase alterada com sucesso"
    }


@router.post("/{os_id}/finalizar", response_model=OrdemServicoResponse)
def finalizar_ordem_servico(
    os_id: int,
    dados: OrdemServicoFinalizar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Finaliza ordem de serviço com dados de calibração"""
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    if os.situacao_servico == "F":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço já finalizada"
        )

    if os.situacao_servico == "C":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível finalizar ordem de serviço cancelada"
        )

    OSService.finalizar_ordem_servico(
        db,
        os,
        dados.model_dump(),
        current_user.id
    )
    db.commit()
    db.refresh(os)

    return os


@router.patch("/{os_id}/pagar")
def marcar_como_pago(
    os_id: int,
    pago: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Marca ordem de serviço como paga/não paga"""
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    os.pago = "S" if pago else "N"

    # Registrar log
    log = LogOrdemServico(
        ordem_servico_id=os.id,
        usuario_id=current_user.id,
        tipo_autor="S",
        acao="PAGAMENTO",
        descricao=f"Ordem de serviço marcada como {'paga' if pago else 'não paga'}"
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "message": f"Ordem de serviço marcada como {'paga' if pago else 'não paga'}"
    }


@router.get("/{os_id}/logs")
def get_logs(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista logs da ordem de serviço"""
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    logs = db.query(LogOrdemServico).filter(
        LogOrdemServico.ordem_servico_id == os_id
    ).order_by(LogOrdemServico.data_hora.desc()).all()

    return {
        "success": True,
        "data": logs
    }
