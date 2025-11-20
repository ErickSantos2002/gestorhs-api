"""
Router de Empresas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.empresa import Empresa, EmpresaHistorico
from app.models.usuario import Usuario
from app.schemas.empresa import (
    EmpresaCreate,
    EmpresaUpdate,
    EmpresaResponse,
    EmpresaListResponse,
    EmpresaHistoricoResponse
)
from app.utils.dependencies import get_current_active_user
from app.utils.pagination import paginate

router = APIRouter(prefix="/empresas", tags=["Empresas"])


def criar_historico(db: Session, empresa: Empresa, usuario_id: int, tipo_operacao: str):
    """Cria registro de histórico da empresa"""
    historico = EmpresaHistorico(
        empresa_id=empresa.id,
        tipo_pessoa=empresa.tipo_pessoa,
        cnpj=empresa.cnpj,
        cpf=empresa.cpf,
        inscricao_estadual=empresa.inscricao_estadual,
        inscricao_municipal=empresa.inscricao_municipal,
        razao_social=empresa.razao_social,
        nome_fantasia=empresa.nome_fantasia,
        cep=empresa.cep,
        logradouro=empresa.logradouro,
        numero=empresa.numero,
        complemento=empresa.complemento,
        bairro=empresa.bairro,
        cidade=empresa.cidade,
        estado=empresa.estado,
        contato_nome=empresa.contato_nome,
        telefone=empresa.telefone,
        telefone_2=empresa.telefone_2,
        celular=empresa.celular,
        whatsapp=empresa.whatsapp,
        whatsapp_2=empresa.whatsapp_2,
        email=empresa.email,
        site=empresa.site,
        observacoes=empresa.observacoes,
        palavras_chave=empresa.palavras_chave,
        imagem=empresa.imagem,
        ativo=empresa.ativo,
        status_contato=empresa.status_contato,
        data_cadastro=empresa.data_cadastro,
        data_ultima_visita=empresa.data_ultima_visita,
        usuario_cadastro_id=empresa.usuario_cadastro_id,
        usuario_modificacao_id=usuario_id,
        tipo_operacao=tipo_operacao
    )
    db.add(historico)


@router.get("", response_model=dict)
def list_empresas(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    razao_social: Optional[str] = None,
    cnpj: Optional[str] = None,
    cpf: Optional[str] = None,
    tipo_pessoa: Optional[str] = Query(None, pattern="^[JF]$"),
    ativo: Optional[str] = Query(None, pattern="^[SN]$"),
    status_contato: Optional[str] = None,
    cidade: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Lista empresas com filtros e paginação"""
    query = db.query(Empresa)

    # Aplicar filtros
    if razao_social:
        query = query.filter(Empresa.razao_social.ilike(f"%{razao_social}%"))
    if cnpj:
        query = query.filter(Empresa.cnpj == cnpj)
    if cpf:
        query = query.filter(Empresa.cpf == cpf)
    if tipo_pessoa:
        query = query.filter(Empresa.tipo_pessoa == tipo_pessoa)
    if ativo:
        query = query.filter(Empresa.ativo == ativo)
    if status_contato:
        query = query.filter(Empresa.status_contato == status_contato)
    if cidade:
        query = query.filter(Empresa.cidade.ilike(f"%{cidade}%"))
    if estado:
        query = query.filter(Empresa.estado == estado)

    # Ordenar por razão social
    query = query.order_by(Empresa.razao_social)

    # Paginar
    result = paginate(query, page, size)

    return {
        "success": True,
        "data": {
            "items": [EmpresaListResponse.model_validate(e) for e in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    }


@router.get("/{empresa_id}", response_model=EmpresaResponse)
def get_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Busca empresa por ID"""
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    return empresa


@router.post("", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def create_empresa(
    empresa: EmpresaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Cria nova empresa"""
    # Verificar documento único
    if empresa.cnpj and db.query(Empresa).filter(Empresa.cnpj == empresa.cnpj).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado"
        )
    if empresa.cpf and db.query(Empresa).filter(Empresa.cpf == empresa.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )

    # Criar empresa
    empresa_data = empresa.model_dump(exclude={'usuario_cadastro_id'})
    db_empresa = Empresa(
        **empresa_data,
        usuario_cadastro_id=current_user.id
    )
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)

    # Criar histórico
    criar_historico(db, db_empresa, current_user.id, "INSERT")
    db.commit()

    return db_empresa


@router.put("/{empresa_id}", response_model=EmpresaResponse)
def update_empresa(
    empresa_id: int,
    empresa: EmpresaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Atualiza empresa"""
    db_empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not db_empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    # Verificar documento único se alterado
    if empresa.cnpj and empresa.cnpj != db_empresa.cnpj:
        if db.query(Empresa).filter(Empresa.cnpj == empresa.cnpj).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado"
            )
    if empresa.cpf and empresa.cpf != db_empresa.cpf:
        if db.query(Empresa).filter(Empresa.cpf == empresa.cpf).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )

    # Atualizar campos
    update_data = empresa.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_empresa, field, value)

    db.commit()
    db.refresh(db_empresa)

    # Criar histórico
    criar_historico(db, db_empresa, current_user.id, "UPDATE")
    db.commit()

    return db_empresa


@router.delete("/{empresa_id}")
def delete_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Deleta empresa (soft delete)"""
    db_empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not db_empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    # Soft delete
    db_empresa.ativo = "N"
    db.commit()

    # Criar histórico
    criar_historico(db, db_empresa, current_user.id, "DELETE")
    db.commit()

    return {
        "success": True,
        "message": "Empresa deletada com sucesso"
    }


@router.patch("/{empresa_id}/ativar")
def toggle_ativo(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Ativa/Desativa empresa"""
    db_empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not db_empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    db_empresa.ativo = "S" if db_empresa.ativo == "N" else "N"
    db.commit()

    criar_historico(db, db_empresa, current_user.id, "UPDATE")
    db.commit()

    return {
        "success": True,
        "message": f"Empresa {'ativada' if db_empresa.ativo == 'S' else 'desativada'} com sucesso"
    }


@router.get("/{empresa_id}/historico")
def get_historico(
    empresa_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Busca histórico de alterações da empresa"""
    # Verificar se empresa existe
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    # Buscar histórico
    query = db.query(EmpresaHistorico).filter(
        EmpresaHistorico.empresa_id == empresa_id
    ).order_by(EmpresaHistorico.data_modificacao.desc())

    result = paginate(query, page, size)

    return {
        "success": True,
        "data": {
            "items": [EmpresaHistoricoResponse.model_validate(h) for h in result.items],
            "pagination": {
                "total": result.total,
                "page": result.page,
                "size": result.size,
                "pages": result.pages
            }
        }
    }


@router.patch("/{empresa_id}/status-contato")
def update_status_contato(
    empresa_id: int,
    status_contato: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Atualiza status de contato da empresa"""
    db_empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not db_empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    db_empresa.status_contato = status_contato
    db.commit()

    return {
        "success": True,
        "message": "Status de contato atualizado com sucesso"
    }
