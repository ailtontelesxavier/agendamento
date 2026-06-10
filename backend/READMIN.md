# MedCare Agendamento Backend

Backend FastAPI para agendamento de consultas, organizado em arquitetura hexagonal.

## Arquitetura

- `medcare/domain`: entidades, status e catálogo de especialidades/horários.
- `medcare/application`: casos de uso de agendamento e WhatsApp.
- `medcare/ports`: contratos de repositório usados pelos casos de uso.
- `medcare/adapters`: implementação em memória dos repositórios.
- `medcare/api`: schemas e aplicação FastAPI.
- `main.py`: entrypoint compatível com `uvicorn main:app`.

## Requisitos

- Python 3.11+
- Poetry
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

## Executar a API

```bash
poetry run uvicorn main:app --reload
```

A API sobe em `http://localhost:8000`.

## Testes

```bash
poetry run pytest
```

## Endpoints principais

- `GET /`
- `GET /specialties`
- `GET /available-slots?doctor=Dr.%20Carlos%20Silva&date=2026-06-20`
- `GET /appointments`
- `POST /appointments`
- `PATCH /appointments/{appointment_id}`
- `DELETE /appointments/{appointment_id}`
- `POST /whatsapp/webhook`
- `GET /whatsapp/sessions`
- `POST /whatsapp/reset/{phone}`
- `GET /stats`

## Exemplo de agendamento

```bash
curl -X POST http://localhost:8000/appointments \
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

