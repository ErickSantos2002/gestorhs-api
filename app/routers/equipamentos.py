"""
Router de Equipamentos e Equipamentos Empresa
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.equipamento import Equipamento, EquipamentoEmpresa
from app.models.usuario import Usuario
from app.schemas.equipamento import (
    EquipamentoCreate,
    EquipamentoUpdate,
    EquipamentoResponse,
    EquipamentoListResponse,
    EquipamentoEmpresaCreate,
    EquipamentoEmpresaUpdate,
    EquipamentoEmpresaResponse
)
from app.utils.dependencies import get_current_active_user
from app.utils.pagination import paginate

router = APIRouter(prefix="/equipamentos", tags=["Equipamentos"])
router_empresa = APIRouter(prefix="/equipamentos-empresa", tags=["Equipamentos Empresa"])


# ========== EQUIPAMENTOS (Catálogo) ==========

@router.get("", response_model=dict)
def list_equipamentos(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    descricao: Optional[str] = None,
    codigo: Optional[str] = None,
    categoria_id: Optional[int] = None,
    marca_id: Optional[int] = None,
    ativo: Optional[str] = Query(None, pattern="^[SN]$"),
    destaque: Optional[str] = Query(None, pattern="^[SN]$"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista equipamentos do catálogo"""
    query = db.query(Equipamento)

    if descricao:
        query = query.filter(Equipamento.descricao.ilike(f"%{descricao}%"))
    if codigo:
        query = query.filter(Equipamento.codigo.ilike(f"%{codigo}%"))
    if categoria_id:
        query = query.filter(Equipamento.categoria_id == categoria_id)
    if marca_id:
        query = query.filter(Equipamento.marca_id == marca_id)
    if ativo:
        query = query.filter(Equipamento.ativo == ativo)
    if destaque:
        query = query.filter(Equipamento.destaque == destaque)

    query = query.order_by(Equipamento.descricao)
    result = paginate(query, page, size)

    return {
        "success": True,
        "data": {
            "items": [EquipamentoListResponse.model_validate(e) for e in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    }


@router.get("/{equipamento_id}", response_model=EquipamentoResponse)
def get_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Busca equipamento por ID"""
    equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )
    return equipamento


@router.post("", response_model=EquipamentoResponse, status_code=status.HTTP_201_CREATED)
def create_equipamento(
    equipamento: EquipamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Cria novo equipamento"""
    # Verificar código único
    if db.query(Equipamento).filter(Equipamento.codigo == equipamento.codigo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código já cadastrado"
        )

    db_equipamento = Equipamento(**equipamento.model_dump())
    db.add(db_equipamento)
    db.commit()
    db.refresh(db_equipamento)

    return db_equipamento


@router.put("/{equipamento_id}", response_model=EquipamentoResponse)
def update_equipamento(
    equipamento_id: int,
    equipamento: EquipamentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Atualiza equipamento"""
    db_equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )

    # Verificar código único se alterado
    if equipamento.codigo and equipamento.codigo != db_equipamento.codigo:
        if db.query(Equipamento).filter(Equipamento.codigo == equipamento.codigo).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código já cadastrado"
            )

    update_data = equipamento.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_equipamento, field, value)

    db.commit()
    db.refresh(db_equipamento)

    return db_equipamento


@router.delete("/{equipamento_id}")
def delete_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Deleta equipamento (soft delete)"""
    db_equipamento = db.query(Equipamento).filter(Equipamento.id == equipamento_id).first()
    if not db_equipamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )

    db_equipamento.ativo = "N"
    db.commit()

    return {
        "success": True,
        "message": "Equipamento deletado com sucesso"
    }


# ========== EQUIPAMENTOS EMPRESA ==========

@router_empresa.get("", response_model=dict)
def list_equipamentos_empresa(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    empresa_id: Optional[int] = None,
    equipamento_id: Optional[int] = None,
    numero_serie: Optional[str] = None,
    status: Optional[str] = Query(None, pattern="^[AIMB]$"),
    vencimento_ate: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista equipamentos vinculados a empresas"""
    query = db.query(EquipamentoEmpresa)

    if empresa_id:
        query = query.filter(EquipamentoEmpresa.empresa_id == empresa_id)
    if equipamento_id:
        query = query.filter(EquipamentoEmpresa.equipamento_id == equipamento_id)
    if numero_serie:
        query = query.filter(EquipamentoEmpresa.numero_serie.ilike(f"%{numero_serie}%"))
    if status:
        query = query.filter(EquipamentoEmpresa.status == status)
    if vencimento_ate:
        query = query.filter(EquipamentoEmpresa.data_proxima_calibracao <= vencimento_ate)

    query = query.order_by(EquipamentoEmpresa.data_proxima_calibracao.nullslast())
    result = paginate(query, page, size)

    return {
        "success": True,
        "data": {
            "items": [EquipamentoEmpresaResponse.model_validate(e) for e in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    }


@router_empresa.get("/{item_id}", response_model=EquipamentoEmpresaResponse)
def get_equipamento_empresa(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Busca equipamento empresa por ID"""
    item = db.query(EquipamentoEmpresa).filter(EquipamentoEmpresa.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )
    return item


@router_empresa.post("", response_model=EquipamentoEmpresaResponse, status_code=status.HTTP_201_CREATED)
def create_equipamento_empresa(
    item: EquipamentoEmpresaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Vincula equipamento a empresa"""
    # Verificar unicidade (equipamento + número de série)
    if item.numero_serie:
        existing = db.query(EquipamentoEmpresa).filter(
            EquipamentoEmpresa.equipamento_id == item.equipamento_id,
            EquipamentoEmpresa.numero_serie == item.numero_serie
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipamento com este número de série já cadastrado"
            )

    db_item = EquipamentoEmpresa(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


@router_empresa.put("/{item_id}", response_model=EquipamentoEmpresaResponse)
def update_equipamento_empresa(
    item_id: int,
    item: EquipamentoEmpresaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Atualiza equipamento empresa"""
    db_item = db.query(EquipamentoEmpresa).filter(EquipamentoEmpresa.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )

    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)

    return db_item


@router_empresa.patch("/{item_id}/recusar-calibracao")
def recusar_calibracao(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Marca equipamento como 'não vai fazer calibração'"""
    db_item = db.query(EquipamentoEmpresa).filter(EquipamentoEmpresa.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado"
        )

    db_item.calibracao_recusada = "S" if db_item.calibracao_recusada == "N" else "N"
    db.commit()

    return {
        "success": True,
        "message": f"Calibração {'recusada' if db_item.calibracao_recusada == 'S' else 'reativada'}"
    }


@router_empresa.get("/vencimentos/proximos")
def get_vencimentos_proximos(
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista equipamentos com calibração próxima do vencimento"""
    data_limite = date.today() + timedelta(days=dias)

    equipamentos = db.query(EquipamentoEmpresa).filter(
        EquipamentoEmpresa.data_proxima_calibracao <= data_limite,
        EquipamentoEmpresa.data_proxima_calibracao >= date.today(),
        EquipamentoEmpresa.ativo == "S",
        EquipamentoEmpresa.calibracao_recusada == "N"
    ).order_by(EquipamentoEmpresa.data_proxima_calibracao).all()

    return {
        "success": True,
        "data": [EquipamentoEmpresaResponse.model_validate(e) for e in equipamentos]
    }
