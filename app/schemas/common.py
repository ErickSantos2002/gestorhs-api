"""
Schemas comuns e reutilizáveis
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional
from datetime import datetime


# Schema genérico para respostas de sucesso
class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operação realizada com sucesso"
    data: Optional[dict] = None


# Schema genérico para erros
class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict


# Schema de paginação
T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    pagination: dict

    class Config:
        from_attributes = True


# Schema base com timestamps
class TimestampMixin(BaseModel):
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True
