"""
Utilitários de paginação
"""
from typing import TypeVar, Generic, List
from sqlalchemy.orm import Query
from pydantic import BaseModel
from math import ceil

T = TypeVar('T')


class Page(BaseModel, Generic[T]):
    """Resposta paginada"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


def paginate(query: Query, page: int = 1, size: int = 20) -> Page:
    """
    Pagina uma query do SQLAlchemy

    Args:
        query: Query a ser paginada
        page: Número da página (começa em 1)
        size: Tamanho da página

    Returns:
        Objeto Page com items e metadados
    """
    if page < 1:
        page = 1
    if size < 1:
        size = 20
    if size > 100:
        size = 100

    total = query.count()
    pages = ceil(total / size) if total > 0 else 1

    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()

    return Page(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )
