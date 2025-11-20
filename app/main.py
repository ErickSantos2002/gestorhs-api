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
from app.routers import categorias
from app.routers import marcas

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
# IMPORTANTE: Categorias e Marcas ANTES de Equipamentos (para não conflitar com /{equipamento_id})
app.include_router(categorias.router, prefix=settings.API_V1_PREFIX)
app.include_router(marcas.router, prefix=settings.API_V1_PREFIX)
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


@app.post("/reset-admin-password")
def reset_admin_password(secret: str = None):
    """
    Endpoint para resetar senha do usuario admin (sem autenticacao)
    Util quando a senha esta corrompida ou em hash incompativel (PHP vs Python)
    Requer SECRET_KEY como parametro de seguranca

    Exemplo: POST /reset-admin-password?secret=sua-secret-key
    """
    from app.database import SessionLocal
    from app.models.usuario import Usuario
    from app.utils.security import hash_password

    # Validar secret key
    if secret != settings.SECRET_KEY:
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": "Secret key invalida. Use ?secret=SUA_SECRET_KEY"
            }
        )

    try:
        db = SessionLocal()
        admin = db.query(Usuario).filter(Usuario.login == "admin").first()

        if not admin:
            db.close()
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "Usuario admin nao encontrado no banco"
                }
            )

        # Resetar senha
        hash_antigo = admin.senha
        nova_senha_hash = hash_password("admin123")
        admin.senha = nova_senha_hash
        db.commit()
        db.close()

        return {
            "success": True,
            "message": "Senha do admin resetada com sucesso!",
            "login": "admin",
            "senha": "admin123",
            "hash_antigo": hash_antigo[:30] + "...",
            "hash_novo": nova_senha_hash[:30] + "...",
            "warning": "IMPORTANTE: Altere esta senha apos o primeiro login!"
        }

    except Exception as e:
        logger.error(f"Erro ao resetar senha: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.post("/init-db")
def init_database_endpoint(secret: str = None):
    """
    Endpoint para inicializar banco de dados (apenas para setup inicial)
    Requer SECRET_KEY como parametro de seguranca

    Exemplo: POST /init-db?secret=sua-secret-key
    """
    from app.database import SessionLocal, Base, engine
    from app.models.usuario import Usuario
    from app.models.auxiliares import FaseOS
    from app.utils.security import hash_password, verify_password

    # Validar secret key
    if secret != settings.SECRET_KEY:
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": "Secret key invalida. Use ?secret=SUA_SECRET_KEY"
            }
        )

    results = {
        "tabelas": "unknown",
        "fases": "unknown",
        "admin": "unknown"
    }

    try:
        # Criar tabelas
        Base.metadata.create_all(bind=engine)
        results["tabelas"] = "criadas"

        db = SessionLocal()

        # Criar fases OS
        fases = [
            {"nome": "Solicitado", "descricao": "OS criada, aguardando envio", "ordem": 1, "cor": "#FFA500"},
            {"nome": "Enviado", "descricao": "Equipamento enviado para calibracao", "ordem": 2, "cor": "#4169E1"},
            {"nome": "Recebido", "descricao": "Equipamento recebido no laboratorio", "ordem": 3, "cor": "#9370DB"},
            {"nome": "Em Calibracao", "descricao": "Calibracao em andamento", "ordem": 4, "cor": "#FF8C00"},
            {"nome": "Calibrado", "descricao": "Calibracao concluida", "ordem": 5, "cor": "#32CD32"},
            {"nome": "Retornando", "descricao": "Equipamento retornando ao cliente", "ordem": 6, "cor": "#1E90FF"},
            {"nome": "Entregue", "descricao": "Equipamento entregue ao cliente", "ordem": 7, "cor": "#228B22"},
            {"nome": "Cancelado", "descricao": "Ordem de servico cancelada", "ordem": 8, "cor": "#DC143C"},
        ]

        fases_criadas = 0
        for fase_data in fases:
            fase = db.query(FaseOS).filter(FaseOS.nome == fase_data["nome"]).first()
            if not fase:
                fase = FaseOS(**fase_data)
                db.add(fase)
                fases_criadas += 1

        db.commit()
        results["fases"] = f"{fases_criadas} fases criadas (total: {len(fases)})"

        # Criar/resetar usuario admin
        admin = db.query(Usuario).filter(Usuario.login == "admin").first()

        if not admin:
            admin = Usuario(
                nome="Administrador",
                email="admin@sistema.com",
                login="admin",
                senha=hash_password("admin123"),
                perfil="admin",
                ativo="S"
            )
            db.add(admin)
            db.commit()
            results["admin"] = "criado (login: admin, senha: admin123)"
        else:
            # Verificar e resetar senha se necessario
            if not verify_password("admin123", admin.senha):
                admin.senha = hash_password("admin123")
                db.commit()
                results["admin"] = "senha resetada para admin123"
            else:
                results["admin"] = "ja existe (login: admin, senha: admin123)"

        db.close()

        return {
            "success": True,
            "message": "Banco de dados inicializado com sucesso!",
            "results": results,
            "warning": "IMPORTANTE: Altere a senha do admin em producao!"
        }

    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "results": results
            }
        )


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
