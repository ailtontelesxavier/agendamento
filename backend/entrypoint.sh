#!/bin/sh

# seta o usuário do banco de dados pois o padrão é root
export USER="app_user"
# Executa as migrações do banco de dados
poetry run alembic upgrade heads
# Instala o OpenTelemetry Bootstrap para instrumentação automática
poetry run opentelemetry-bootstrap -a install

# Gera par RSA compartilhado entre todos os workers (executado uma vez)
poetry run python3 -c "
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

priv_path = Path('/app/rsa_private.pem')
pub_path = Path('/app/rsa_public.pem')

if not priv_path.exists():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_path.write_bytes(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    pub_path.write_bytes(key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    print('RSA key pair generated at /app/')
else:
    print('RSA key pair already exists, skipping generation')
"

# Inicia a aplicação
#poetry run uvicorn --host 0.0.0.0 --port 8004 --workers 3 backend.main:app --proxy-headers --forwarded-allow-ips="*" --log-level debug
poetry run uvicorn --host 0.0.0.0 --port 8004 --workers 5 backend.main:app --proxy-headers
#python manage.py migrate
#python run uvicorn --host 0.0.0.0 --port 8004 --workers 10 app.main:app
