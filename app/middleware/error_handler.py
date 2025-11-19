"""
Middleware de tratamento de erros
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação do Pydantic"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])  # Ignora 'body'
        errors.append({
            "field": field,
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dados inválidos",
                "details": errors
            }
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handler para erros de integridade do banco"""
    logger.error(f"Integrity error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": {
                "code": "INTEGRITY_ERROR",
                "message": "Erro de integridade no banco de dados"
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handler genérico para exceções não tratadas"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Erro interno do servidor"
            }
        }
    )


def setup_error_handlers(app):
    """Configura handlers de erro"""
    from fastapi.exceptions import RequestValidationError
    from sqlalchemy.exc import IntegrityError

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
