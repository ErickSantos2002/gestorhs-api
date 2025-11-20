"""
Script para inicializar banco de dados com dados essenciais
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.usuario import Usuario
from app.models.auxiliares import FaseOS
from app.utils.security import hash_password, verify_password


def init_fases_os(db: Session):
    """Cria as 8 fases do workflow de Ordem de Serviço"""
    fases = [
        {"nome": "Solicitado", "descricao": "OS criada, aguardando envio", "ordem": 1, "cor": "#FFA500"},
        {"nome": "Enviado", "descricao": "Equipamento enviado para calibração", "ordem": 2, "cor": "#4169E1"},
        {"nome": "Recebido", "descricao": "Equipamento recebido no laboratório", "ordem": 3, "cor": "#9370DB"},
        {"nome": "Em Calibração", "descricao": "Calibração em andamento", "ordem": 4, "cor": "#FF8C00"},
        {"nome": "Calibrado", "descricao": "Calibração concluída", "ordem": 5, "cor": "#32CD32"},
        {"nome": "Retornando", "descricao": "Equipamento retornando ao cliente", "ordem": 6, "cor": "#1E90FF"},
        {"nome": "Entregue", "descricao": "Equipamento entregue ao cliente", "ordem": 7, "cor": "#228B22"},
        {"nome": "Cancelado", "descricao": "Ordem de serviço cancelada", "ordem": 8, "cor": "#DC143C"},
    ]

    for fase_data in fases:
        fase = db.query(FaseOS).filter(FaseOS.nome == fase_data["nome"]).first()
        if not fase:
            fase = FaseOS(**fase_data)
            db.add(fase)
            print(f"✅ Fase criada: {fase_data['nome']}")

    db.commit()


def init_admin_user(db: Session):
    """Cria usuario administrador padrao"""
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
        print("✅ Usuario admin criado")
        print("   Login: admin")
        print("   Senha: admin123")
        print("   ⚠️  IMPORTANTE: Altere a senha em producao!")
    else:
        print("ℹ️  Usuario admin ja existe")
        # Verificar se a senha esta valida
        if not verify_password("admin123", admin.senha):
            print("⚠️  Senha do admin esta invalida/corrompida. Resetando...")
            admin.senha = hash_password("admin123")
            db.commit()
            print("✅ Senha do admin resetada para: admin123")


def init_database():
    """Inicializa banco de dados"""
    print("🚀 Inicializando banco de dados...")

    # Criar tabelas
    print("📦 Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas")

    # Inicializar dados essenciais
    db = SessionLocal()
    try:
        print("\n📝 Criando dados iniciais...")
        init_fases_os(db)
        init_admin_user(db)
        print("\n✅ Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
