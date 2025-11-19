"""
Aplicacao FastAPI principal
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

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

# Criar aplicacao FastAPI
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
    """Health check basico"""
    return {
        "success": True,
        "status": "healthy"
    }


@app.get("/health/detailed")
def health_check_detailed():
    """Health check detalhado com diagnostico"""
    from app.database import SessionLocal
    from sqlalchemy import text

    health = {
        "api": "ok",
        "database": "unknown",
        "fases_os": "unknown",
        "cors_origins_raw": settings.CORS_ORIGINS,
        "cors_origins_list": settings.cors_origins_list,
        "debug": settings.DEBUG
    }

    # Testar conexao com banco
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        health["database"] = "ok"

        # Testar se fases_os existem
        from app.models.auxiliares import FaseOS
        fases_count = db.query(FaseOS).count()
        health["fases_os"] = f"{fases_count} fases cadastradas"

        db.close()
    except Exception as e:
        health["database"] = f"error: {str(e)}"

    return {
        "success": True,
        "health": health
    }


@app.get("/cors-test")
def cors_test():
    """
    Endpoint simples para testar CORS
    Chame este endpoint do frontend para verificar se CORS funciona
    """
    return {
        "success": True,
        "message": "CORS funcionando!",
        "timestamp": datetime.utcnow().isoformat(),
        "cors_origins": settings.cors_origins_list
    }


@app.options("/cors-test")
def cors_test_options():
    """OPTIONS para teste de CORS"""
    return {}


@app.on_event("startup")
async def startup_event():
    """Evento de inicializacao"""
    logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} iniciado")
    logger.info(f"📚 Documentacao: {settings.API_V1_PREFIX}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento"""
    logger.info("🛑 Aplicacao encerrada")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
