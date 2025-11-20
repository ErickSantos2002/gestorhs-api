"""
Router de Marcas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.auxiliares import Marca
from app.models.usuario import Usuario
from app.schemas.auxiliares import (
    MarcaCreate,
    MarcaUpdate,
    MarcaResponse
)
from app.utils.dependencies import get_current_active_user
from app.utils.pagination import paginate

router = APIRouter(prefix="/equipamentos/marcas", tags=["Marcas"])


@router.get("", response_model=dict)
def list_marcas(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    ativo: Optional[str] = Query(None, pattern="^[SN]$"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista marcas com filtros e paginação"""
    query = db.query(Marca)

    # Aplicar filtros
    if search:
        query = query.filter(Marca.nome.ilike(f"%{search}%"))
    if ativo:
        query = query.filter(Marca.ativo == ativo)

    # Ordenar por nome
    query = query.order_by(Marca.nome)

    # Paginar
    result = paginate(query, page, size)

    return {
        "success": True,
        "data": {
            "items": [MarcaResponse.model_validate(m) for m in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    }


@router.get("/{marca_id}", response_model=MarcaResponse)
def get_marca(
    marca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Busca marca por ID"""
    marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca não encontrada"
        )
    return marca


@router.post("", response_model=MarcaResponse, status_code=status.HTTP_201_CREATED)
def create_marca(
    marca: MarcaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Cria nova marca"""
    # Verificar nome único
    if db.query(Marca).filter(Marca.nome == marca.nome).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma marca com este nome"
        )

    # Criar marca
    db_marca = Marca(
        **marca.model_dump(),
        data_cadastro=date.today()
    )
    db.add(db_marca)
    db.commit()
    db.refresh(db_marca)

    return db_marca


@router.put("/{marca_id}", response_model=MarcaResponse)
def update_marca(
    marca_id: int,
    marca: MarcaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Atualiza marca"""
    db_marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not db_marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca não encontrada"
        )

    # Verificar nome único se alterado
    if marca.nome and marca.nome != db_marca.nome:
        if db.query(Marca).filter(Marca.nome == marca.nome).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma marca com este nome"
            )

    # Atualizar campos
    update_data = marca.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_marca, field, value)

    db.commit()
    db.refresh(db_marca)

    return db_marca


@router.patch("/{marca_id}/toggle-status")
def toggle_status_marca(
    marca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Ativa/Desativa marca"""
    db_marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not db_marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca não encontrada"
        )

    db_marca.ativo = "S" if db_marca.ativo == "N" else "N"
    db.commit()

    return {
        "success": True,
        "message": f"Marca {'ativada' if db_marca.ativo == 'S' else 'desativada'} com sucesso"
    }


@router.delete("/{marca_id}")
def delete_marca(
    marca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Deleta marca permanentemente do banco de dados"""
    db_marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not db_marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca não encontrada"
        )

    # Verificar se há equipamentos usando esta marca
    if db_marca.equipamentos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar marca que possui equipamentos vinculados"
        )

    # Hard delete
    db.delete(db_marca)
    db.commit()

    return {
        "success": True,
        "message": "Marca deletada com sucesso"
    }
