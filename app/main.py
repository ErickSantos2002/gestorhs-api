"""
Aplicação FastAPI principal
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers

# Importar routers
from app.routers import auth
from app.routers import usuarios
from app.routers import empresas
from app.routers import equipamentos
from app.routers import ordens_servico
from app.routers import dashboard

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Configurar middlewares
setup_cors(app)
setup_error_handlers(app)

# Registrar routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(usuarios.router, prefix=settings.API_V1_PREFIX)
app.include_router(empresas.router, prefix=settings.API_V1_PREFIX)
app.include_router(equipamentos.router, prefix=settings.API_V1_PREFIX)
app.include_router(equipamentos.router_empresa, prefix=settings.API_V1_PREFIX)
app.include_router(ordens_servico.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "success": True,
        "message": f"Bem-vindo ao {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get("/health")
def health_check():
    """Health check"""
    return {
        "success": True,
        "status": "healthy"
    }


@app.on_event("startup")
async def startup_event():
    """Evento de inicialização"""
    logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} iniciado")
    logger.info(f"📚 Documentação: {settings.API_V1_PREFIX}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento"""
    logger.info("🛑 Aplicação encerrada")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
