# MedCare Agendamento Backend

Backend FastAPI para agendamento de consultas, organizado em arquitetura hexagonal.

## Arquitetura

- `medcare/domain`: entidades, status e catálogo de especialidades/horários.
- `medcare/application`: casos de uso de agendamento e WhatsApp.
- `medcare/ports`: contratos de repositório (async) usados pelos casos de uso.
- `medcare/adapters/in_memory.py`: implementação em memória dos repositórios (fallback/testes).
- `medcare/adapters/sqlalchemy_repo.py`: implementação async com SQLAlchemy 2 + PostgreSQL.
- `medcare/adapters/db/models.py`: modelos SQLAlchemy (User, AppointmentDB).
- `medcare/adapters/db/connection.py`: engine async e session maker.
- `medcare/adapters/db/user_manager.py`: UserManager com autenticação CPF + Argon2.
- `medcare/api/schemas.py`: schemas Pydantic (usuários e agendamentos).
- `medcare/api/auth.py`: rotas de autenticação (JWT, registro, CPF login).
- `medcare/api/app.py`: aplicação FastAPI com rotas e dependências.
- `alembic/`: migrações do banco de dados.
- `main.py`: entrypoint compatível com `uvicorn main:app`.

## Requisitos

- Python 3.13+
- Poetry
- PostgreSQL 18 (via Docker ou local)
- Plugin `poetry-plugin-shell`

Instalação do plugin:

```bash
poetry self add poetry-plugin-shell
```

## Setup

```bash
poetry install
poetry shell
```

## Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste:

```bash
DATABASE_URL=postgresql+asyncpg://medcare:changeme@localhost:5432/medcare
SECRET_KEY=sua-chave-secreta-aqui
```

## Banco de Dados

### Com Docker (recomendado)

```bash
docker compose up -d database
```

### Migrações

```bash
poetry run alembic upgrade heads
```

### Criar migration após alterar modelos

```bash
poetry run alembic revision --autogenerate -m "descrição"
poetry run alembic upgrade heads
```

## Executar a API

```bash
poetry run uvicorn main:app --reload
```

A API sobe em `http://localhost:8000`.

Quando `DATABASE_URL` está configurado, o backend usa PostgreSQL + autenticação JWT.
Sem `DATABASE_URL`, usa repositórios em memória (sem auth).

## Testes

```bash
poetry run pytest
```

## Autenticação

### Login por CPF

```bash
curl -X POST http://localhost:8000/auth/cpf-login \
  -H 'Content-Type: application/json' \
  -d '{"cpf": "12345678901", "password": "senha123"}'
```

Resposta:

```json
{"access_token": "<jwt_token>", "token_type": "bearer"}
```

### Usar token em requisições protegidas

```bash
curl -H "Authorization: Bearer <jwt_token>" http://localhost:8000/appointments
```

### Registro de usuário

```bash
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"cpf": "12345678901", "password": "senha123"}'
```

## Endpoints

### Públicos

- `GET /` — health check
- `GET /specialties` — lista especialidades e médicos
- `GET /available-slots?doctor=Dr.%20Carlos%20Silva&date=2026-06-20` — horários disponíveis
- `POST /auth/cpf-login` — login com CPF + senha (retorna JWT)
- `POST /auth/register` — registro de usuário
- `POST /whatsapp/webhook` — webhook externo do WhatsApp

### Protegidas (requer JWT)

- `GET /appointments` — listar agendamentos
- `POST /appointments` — criar agendamento
- `PATCH /appointments/{appointment_id}` — atualizar status
- `DELETE /appointments/{appointment_id}` — cancelar agendamento
- `GET /stats` — estatísticas
- `GET /whatsapp/sessions` — sessões ativas
- `POST /whatsapp/reset/{phone}` — resetar sessão

### Auth (fastapi-users)

- `POST /auth/jwt/login` — login OAuth2 (email + senha)
- `POST /auth/jwt/logout` — logout
- `GET /auth/users/me` — perfil do usuário logado
- `GET /auth/users/` — listar usuários
- `GET /auth/users/{id}` — buscar usuário por ID
- `PATCH /auth/users/{id}` — atualizar usuário
- `DELETE /auth/users/{id}` — deletar usuário

## Exemplo de agendamento

```bash
curl -X POST http://localhost:8000/appointments \
  -H "Authorization: Bearer <jwt_token>" \
  -H 'Content-Type: application/json' \
  -d '{
    "patient_name": "Maria Souza",
    "phone": "5599999999999",
    "specialty": "Clínica Geral",
    "doctor": "Dr. Carlos Silva",
    "date": "2026-06-20",
    "time": "08:00",
    "notes": "Primeira consulta"
  }'
```

## Docker

### Produção

```bash
docker compose -f compose.prod.yaml up -d
```

### Serviços

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| app-backend | 8004 | API FastAPI |
| database | 5432 | PostgreSQL 18 |
| redis | 6379 | Cache |
| otel | 3000/4317/4318 | Observabilidade |
| nginx2 | 80/443 | Reverse proxy |

## Tecnologias

- **Framework**: FastAPI (async)
- **Banco**: PostgreSQL 18 + SQLAlchemy 2 (asyncpg)
- **Auth**: fastapi-users + JWT + CPF login
- **Senhas**: Argon2 (pwdlib)
- **Migrações**: Alembic
- **Testes**: pytest + pytest-asyncio + httpx
- **Container**: Docker + Docker Compose
