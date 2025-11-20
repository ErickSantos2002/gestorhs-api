# 🔧 Sistema de Calibração - API REST

API REST completa para gerenciamento de calibração de equipamentos (bafômetros e detectores) desenvolvida com **FastAPI** e **PostgreSQL**.

## 🚀 Tecnologias

- **FastAPI** 0.104+ - Framework web moderno e rápido
- **PostgreSQL** 16+ - Banco de dados relacional
- **SQLAlchemy** 2.0+ - ORM
- **Alembic** - Migrations
- **Pydantic** v2 - Validação de dados
- **JWT** - Autenticação
- **Bcrypt** - Hash de senhas
- **Docker** - Containerização

## 📋 Funcionalidades

### ✅ Autenticação e Autorização
- Login com JWT (Access Token + Refresh Token)
- 4 níveis de permissão: Admin, Gerente, Técnico, Atendente
- Refresh token para renovação automática
- Middleware de autenticação

### ✅ Gestão de Usuários
- CRUD completo
- Controle de permissões por perfil
- Soft delete
- Histórico de acessos

### ✅ Gestão de Empresas (Clientes)
- CRUD completo com validação de CNPJ/CPF
- Suporte para Pessoa Física e Jurídica
- Histórico completo de alterações (audit trail)
- Status de contato (ativo, sem_contato, inativo, perdido)
- Endereço completo e múltiplos contatos

### ✅ Catálogo de Equipamentos
- CRUD de equipamentos
- Categorias e marcas
- Controle de estoque
- Período de calibração configurável
- Fotos e documentos anexáveis

### ✅ Equipamentos da Empresa
- Vinculação de equipamentos às empresas
- Controle de números de série e patrimônio
- Rastreamento de datas de calibração
- Status: Ativo, Inativo, Manutenção, Baixado
- Opção "não vai fazer calibração"

### ✅ Ordens de Serviço
- Criação automática com chave de acesso única
- Workflow com 8 fases: Solicitado → Enviado → Recebido → Em Calibração → Calibrado → Retornando → Entregue | Cancelado
- Atualização automática de timestamps por fase
- Finalização com dados de calibração
- Atualização automática do equipamento ao finalizar
- Cálculo automático de próxima calibração
- Controle financeiro (valores, pagamento)
- Histórico completo de mudanças (logs)

### ✅ Dashboard em Tempo Real
- 7 cards principais:
  - Ordens em andamento
  - Clientes atrasados
  - Calibrações atrasadas
  - Calibrações próximas (30 dias)
  - Ordens finalizadas (30 dias)
  - Calibrações recusadas
  - Clientes perdidos
- Detalhes de cada card com filtros
- Gráficos mensais de OSs e faturamento

### ✅ Sistema de Logs e Auditoria
- Log geral do sistema
- Log específico de ordens de serviço
- Histórico de alterações de empresas
- Rastreamento de ações por usuário

## 📁 Estrutura do Projeto

```
gestorhs-api/
├── app/
│   ├── models/          # SQLAlchemy Models
│   ├── schemas/         # Pydantic Schemas
│   ├── routers/         # Endpoints da API
│   ├── services/        # Lógica de negócio
│   ├── utils/           # Utilitários (JWT, segurança, paginação)
│   ├── middleware/      # Middlewares (CORS, errors)
│   ├── config.py        # Configurações
│   ├── database.py      # Conexão do banco
│   └── main.py          # Aplicação FastAPI
├── alembic/             # Migrations
├── tests/               # Testes
├── uploads/             # Arquivos uploadados
├── logs/                # Logs da aplicação
├── .env                 # Variáveis de ambiente
├── requirements.txt     # Dependências Python
├── docker-compose.yml   # Docker Compose
└── README.md
```

## 🔧 Instalação e Execução

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd gestorhs-api

# Inicie os containers
docker-compose up -d

# Execute as migrations
docker-compose exec api alembic upgrade head

# API disponível em http://localhost:8000
```

### Opção 2: Instalação Local

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd gestorhs-api

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure o .env (copie de .env.example)
cp .env.example .env
# Edite o .env com suas configurações

# Execute as migrations
alembic upgrade head

# Inicie o servidor
uvicorn app.main:app --reload

# API disponível em http://localhost:8000
```

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 🔑 Endpoints Principais

### Autenticação
```
POST   /api/v1/auth/login          # Login
POST   /api/v1/auth/refresh         # Renovar token
POST   /api/v1/auth/logout          # Logout
GET    /api/v1/auth/me              # Usuário atual
```

### Usuários
```
GET    /api/v1/usuarios             # Listar
GET    /api/v1/usuarios/{id}        # Buscar
POST   /api/v1/usuarios             # Criar
PUT    /api/v1/usuarios/{id}        # Atualizar
DELETE /api/v1/usuarios/{id}        # Deletar
PATCH  /api/v1/usuarios/{id}/senha  # Alterar senha
```

### Empresas
```
GET    /api/v1/empresas                    # Listar
GET    /api/v1/empresas/{id}               # Buscar
POST   /api/v1/empresas                    # Criar
PUT    /api/v1/empresas/{id}               # Atualizar
DELETE /api/v1/empresas/{id}               # Deletar
GET    /api/v1/empresas/{id}/historico     # Histórico
```

### Equipamentos
```
GET    /api/v1/equipamentos                # Listar catálogo
GET    /api/v1/equipamentos/{id}           # Buscar
POST   /api/v1/equipamentos                # Criar
PUT    /api/v1/equipamentos/{id}           # Atualizar
DELETE /api/v1/equipamentos/{id}           # Deletar
```

### Equipamentos Empresa
```
GET    /api/v1/equipamentos-empresa        # Listar
POST   /api/v1/equipamentos-empresa        # Vincular
GET    /api/v1/equipamentos-empresa/vencimentos/proximos  # Vencimentos
```

### Ordens de Serviço
```
GET    /api/v1/ordens-servico              # Listar
GET    /api/v1/ordens-servico/{id}         # Buscar
POST   /api/v1/ordens-servico              # Criar
PUT    /api/v1/ordens-servico/{id}         # Atualizar
DELETE /api/v1/ordens-servico/{id}         # Cancelar
PATCH  /api/v1/ordens-servico/{id}/fase    # Mudar fase
POST   /api/v1/ordens-servico/{id}/finalizar # Finalizar
GET    /api/v1/ordens-servico/chave/{chave} # Buscar por chave (público)
```

### Dashboard
```
GET    /api/v1/dashboard/principal             # Métricas principais
GET    /api/v1/dashboard/andamento             # OSs em andamento
GET    /api/v1/dashboard/calibracoes-atrasadas # Vencidas
GET    /api/v1/dashboard/calibracoes-proximas  # Próximas
GET    /api/v1/dashboard/finalizadas           # Finalizadas
GET    /api/v1/dashboard/grafico-mensal        # Gráfico mensal
```

## 🗄️ Banco de Dados

O sistema utiliza **PostgreSQL** com as seguintes tabelas principais:

- **usuarios** - Usuários do sistema
- **empresas** / **empresas_historico** - Clientes e histórico
- **equipamentos** - Catálogo de produtos
- **equipamentos_empresa** - Equipamentos dos clientes
- **ordens_servico** - Ordens de serviço
- **caixas** - Organização em lotes
- **categorias**, **marcas**, **setores** - Auxiliares
- **fases_os** - Fases do workflow
- **tipos_calibracao** - Tipos de calibração
- **documentos**, **fotos**, **logos_empresas** - Anexos
- **logs_sistema**, **logs_ordens_servico** - Auditoria

## 🔐 Segurança

- Senhas hasheadas com **bcrypt** (rounds=12)
- Tokens **JWT** com expiração
- Validação de entrada com **Pydantic**
- Proteção contra **SQL Injection** (ORM)
- **CORS** configurável
- Soft delete para preservar dados
- Audit trail completo

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=app tests/

# Teste específico
pytest tests/test_auth.py -v
```

## 📝 Migrations

```bash
# Gerar nova migration
alembic revision --autogenerate -m "descrição"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Ver histórico
alembic history
```

## 🛠️ Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements.txt

# Ativar modo debug no .env
DEBUG=True

# Rodar com reload automático
uvicorn app.main:app --reload

# Formatar código
black app/
isort app/
```

## 📊 Variáveis de Ambiente

Principais variáveis no `.env`:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# JWT
SECRET_KEY=sua-chave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
DEBUG=False
CORS_ORIGINS=http://localhost:3000

# Upload
MAX_FILE_SIZE=10485760  # 10MB
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é propriedade de **Health & Safety**.

## 👥 Contato

**Desenvolvedor:** Health & Safety Team
**Email:** contato@healthsafety.com.br

---

**🔧 Sistema de Calibração v1.0.0** - FastAPI + PostgreSQL
