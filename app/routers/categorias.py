"""
Router de Categorias
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.auxiliares import Categoria
from app.models.usuario import Usuario
from app.schemas.auxiliares import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaResponse
)
from app.utils.dependencies import get_current_active_user
from app.utils.pagination import paginate

router = APIRouter(prefix="/equipamentos/categorias", tags=["Categorias"])


@router.get("", response_model=dict)
def list_categorias(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    ativo: Optional[str] = Query(None, pattern="^[SN]$"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista categorias com filtros e paginação"""
    query = db.query(Categoria)

    # Aplicar filtros
    if search:
        query = query.filter(Categoria.nome.ilike(f"%{search}%"))
    if ativo:
        query = query.filter(Categoria.ativo == ativo)

    # Ordenar por nome
    query = query.order_by(Categoria.nome)

    # Paginar
    result = paginate(query, page, size)

    return {
        "success": True,
        "data": {
            "items": [CategoriaResponse.model_validate(c) for c in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    }


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def get_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Busca categoria por ID"""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    return categoria


@router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def create_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Cria nova categoria"""
    # Verificar nome único
    if db.query(Categoria).filter(Categoria.nome == categoria.nome).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma categoria com este nome"
        )

    # Criar categoria
    db_categoria = Categoria(
        **categoria.model_dump(),
        data_cadastro=date.today()
    )
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)

    return db_categoria


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def update_categoria(
    categoria_id: int,
    categoria: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Atualiza categoria"""
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )

    # Verificar nome único se alterado
    if categoria.nome and categoria.nome != db_categoria.nome:
        if db.query(Categoria).filter(Categoria.nome == categoria.nome).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma categoria com este nome"
            )

    # Atualizar campos
    update_data = categoria.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_categoria, field, value)

    db.commit()
    db.refresh(db_categoria)

    return db_categoria


@router.patch("/{categoria_id}/toggle-status")
def toggle_status_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Ativa/Desativa categoria"""
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )

    db_categoria.ativo = "S" if db_categoria.ativo == "N" else "N"
    db.commit()

    return {
        "success": True,
        "message": f"Categoria {'ativada' if db_categoria.ativo == 'S' else 'desativada'} com sucesso"
    }


@router.delete("/{categoria_id}")
def delete_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Deleta categoria permanentemente do banco de dados"""
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )

    # Verificar se há equipamentos usando esta categoria
    if db_categoria.equipamentos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar categoria que possui equipamentos vinculados"
        )

    # Hard delete
    db.delete(db_categoria)
    db.commit()

    return {
        "success": True,
        "message": "Categoria deletada com sucesso"
    }
