"""
Router de Usuários
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioUpdateSenha,
    UsuarioResponse,
    UsuarioListResponse
)
from app.utils.dependencies import get_current_active_user, require_admin
from app.utils.security import hash_password, verify_password
from app.utils.pagination import paginate

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("", response_model=dict)
def list_usuarios(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    nome: Optional[str] = None,
    email: Optional[str] = None,
    perfil: Optional[str] = None,
    ativo: Optional[str] = Query(None, pattern="^[SN]$"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Lista usuários com filtros e paginação
    """
    query = db.query(Usuario)

    # Aplicar filtros
    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))
    if email:
        query = query.filter(Usuario.email.ilike(f"%{email}%"))
    if perfil:
        query = query.filter(Usuario.perfil == perfil)
    if ativo:
        query = query.filter(Usuario.ativo == ativo)

    # Ordenar por nome
    query = query.order_by(Usuario.nome)

    # Paginar
    result = paginate(query, page, size)

    return {
        "success": True,
        "data": {
            "items": [UsuarioListResponse.model_validate(u) for u in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    }


@router.get("/{user_id}", response_model=UsuarioResponse)
def get_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Busca usuário por ID
    """
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Cria novo usuário (apenas admin)
    """
    # Verificar se login já existe
    if db.query(Usuario).filter(Usuario.login == usuario.login).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login já cadastrado"
        )

    # Verificar se email já existe
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Criar usuário
    db_usuario = Usuario(
        **usuario.model_dump(exclude={"senha"}),
        senha=hash_password(usuario.senha)
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    return db_usuario


@router.put("/{user_id}", response_model=UsuarioResponse)
def update_usuario(
    user_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Atualiza usuário (apenas admin)
    """
    db_usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Verificar email único se estiver sendo alterado
    if usuario.email and usuario.email != db_usuario.email:
        if db.query(Usuario).filter(Usuario.email == usuario.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )

    # Atualizar campos
    update_data = usuario.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_usuario, field, value)

    db.commit()
    db.refresh(db_usuario)

    return db_usuario


@router.delete("/{user_id}")
def delete_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Deleta usuário (soft delete - apenas admin)
    """
    db_usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Não permitir deletar a si mesmo
    if db_usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar seu próprio usuário"
        )

    # Soft delete
    db_usuario.ativo = "N"
    db.commit()

    return {
        "success": True,
        "message": "Usuário deletado com sucesso"
    }


@router.patch("/{user_id}/ativar")
def toggle_ativo(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Ativa/Desativa usuário
    """
    db_usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Toggle ativo
    db_usuario.ativo = "S" if db_usuario.ativo == "N" else "N"
    db.commit()

    return {
        "success": True,
        "message": f"Usuário {'ativado' if db_usuario.ativo == 'S' else 'desativado'} com sucesso"
    }


@router.patch("/{user_id}/senha")
def update_senha(
    user_id: int,
    senha_data: UsuarioUpdateSenha,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Altera senha do usuário
    """
    # Permitir alterar apenas própria senha (ou admin pode alterar qualquer uma)
    if current_user.id != user_id and current_user.perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar sua própria senha"
        )

    db_usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Verificar senha atual (exceto se admin alterando outro usuário)
    if current_user.id == user_id:
        if not verify_password(senha_data.senha_atual, db_usuario.senha):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )

    # Atualizar senha
    db_usuario.senha = hash_password(senha_data.senha_nova)
    db.commit()

    return {
        "success": True,
        "message": "Senha alterada com sucesso"
    }
