# 🏥 MedCare — Sistema de Agendamento com Flow WhatsApp

Sistema completo de agendamento de consultas médicas com calendário visual e integração de flow WhatsApp via bot conversacional.

---

## 🗂️ Estrutura

```
agendamento/
├── backend/
│   └── main.py          # FastAPI — API + flow WhatsApp
└── frontend/
    └── index.html       # Vue.js 3 (CDN, sem build)
```

---

## ⚙️ Instalação e execução

### Backend (FastAPI)

```bash
cd backend

# Instalar dependências
pip install fastapi uvicorn httpx python-dateutil

# Rodar o servidor
uvicorn main:app --reload --port 8000
```

API disponível em: `http://localhost:8000`  
Docs interativos: `http://localhost:8000/docs`

### Frontend (Vue.js 3)

Basta abrir o arquivo diretamente no navegador:

```bash
# Opção 1 — abrir direto
open frontend/index.html

# Opção 2 — servir com Python
cd frontend && python3 -m http.server 3000
# Acesse: http://localhost:3000
```

> O frontend usa Vue.js 3 via CDN, sem necessidade de Node.js ou build.

---

## 📡 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/specialties` | Lista especialidades e médicos |
| GET | `/available-slots?doctor=X&date=Y` | Horários livres |
| GET | `/appointments` | Lista agendamentos (filtros: date, doctor, status) |
| POST | `/appointments` | Criar agendamento |
| PATCH | `/appointments/{id}` | Atualizar status |
| DELETE | `/appointments/{id}` | Cancelar |
| POST | `/whatsapp/webhook` | Receber mensagem do WhatsApp |
| GET | `/whatsapp/sessions` | Listar sessões ativas |
| POST | `/whatsapp/reset/{phone}` | Resetar sessão |
| GET | `/stats` | Estatísticas gerais |

---

## 💬 Integração real com WhatsApp

Para conectar com WhatsApp real, use um dos provedores abaixo e aponte o webhook para:

```
POST http://seu-servidor:8000/whatsapp/webhook
```

Payload esperado:
```json
{
  "from_number": "556392345678",
  "message": "1"
}
```

### Provedores compatíveis

| Provedor | Tipo | Obs |
|----------|------|-----|
| **Twilio** | API oficial | Fácil de configurar, pago |
| **Z-API** | API não-oficial | Popular no Brasil, barato |
| **Evolution API** | Self-hosted | Open source, gratuito |
| **WPPConnect** | Self-hosted | Open source |
| **Meta Business** | API oficial | Gratuito (tier básico) |

### Exemplo com Z-API / Evolution API

```python
# Adicione ao main.py para enviar mensagens de volta
import httpx

ZAPI_INSTANCE = "SUA_INSTANCIA"
ZAPI_TOKEN = "SEU_TOKEN"

async def send_whatsapp(phone: str, message: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text",
            json={"phone": phone, "message": message}
        )
```

---

## 🔄 Fluxo conversacional do bot

```
Usuário envia mensagem
        ↓
[Menu principal] — 1/2/3/4
        ↓ (opção 1)
[Escolhe especialidade] — número
        ↓
[Escolhe médico] — número
        ↓
[Informa data] — DD/MM/AAAA
        ↓
[Escolhe horário] — HH:MM (lista de livres)
        ↓
[Informa nome completo]
        ↓
[Confirma] — SIM ou NÃO
        ↓
✅ Agendamento salvo + código enviado
```

---

## 🛠️ Personalização

### Adicionar especialidade/médico
No `main.py`, edite o dicionário `SPECIALTIES`:
```python
SPECIALTIES = {
    "Neurologia": ["Dr. Paulo Ramos", "Dra. Sofia Andrade"],
    ...
}
```

### Alterar horários disponíveis
```python
SLOTS = ["07:00","07:30","08:00",...]
```

### Banco de dados
Para produção, substitua o dict `appointments` por SQLAlchemy + PostgreSQL:
```bash
pip install sqlalchemy asyncpg alembic
```

---

## 🚀 Deploy sugerido

| Camada | Opção |
|--------|-------|
| Backend | Railway, Render, ou VPS com Docker |
| Frontend | Vercel, Netlify, ou mesmo S3 |
| DB | Supabase (PostgreSQL gratuito) |
| WhatsApp | Evolution API no mesmo VPS |
