from __future__ import annotations

import argparse
import asyncio
import getpass
import os
import sys
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from medcare.adapters.db.models import Base, User
from medcare.adapters.db.user_manager import argon2_helper

DEFAULT_DATABASE_URL = "postgresql+asyncpg://medcare:medcare@database:5432/medcare"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cria um usuário no banco MedCare.")
    parser.add_argument("--cpf", required=True, help="CPF com 11 dígitos, somente números.")
    parser.add_argument("--email", default=None, help="E-mail do usuário. Opcional para login por CPF.")
    parser.add_argument("--password", default=None, help="Senha. Se omitida, será solicitada no terminal.")
    parser.add_argument(
        "--database-url",
        default=None,
        help="URL async do banco. Padrão: DATABASE_URL do ambiente ou valor local do projeto.",
    )
    parser.add_argument("--env-file", default=".env", help="Arquivo .env para carregar antes de conectar.")
    parser.add_argument("--create-tables", action="store_true", help="Cria as tabelas antes de inserir.")
    parser.add_argument("--inactive", action="store_true", help="Cria usuário inativo.")
    parser.add_argument("--superuser", action="store_true", help="Cria usuário com permissão de superuser.")
    parser.add_argument("--verified", action="store_true", help="Marca usuário como verificado.")
    return parser


def get_password(args: argparse.Namespace) -> str:
    if args.password:
        return args.password

    password = getpass.getpass("Senha: ")
    confirmation = getpass.getpass("Confirme a senha: ")
    if password != confirmation:
        raise ValueError("As senhas não conferem.")
    if not password:
        raise ValueError("A senha não pode ser vazia.")
    return password


def validate_cpf(cpf: str) -> str:
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValueError("CPF deve conter exatamente 11 dígitos.")
    return cpf


async def create_user(args: argparse.Namespace) -> User:
    load_env_file(Path(args.env_file))

    cpf = validate_cpf(args.cpf)
    password = get_password(args)
    database_url = args.database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with engine.begin() as conn:
            if args.create_tables:
                await conn.run_sync(Base.metadata.create_all)

        async with async_session_maker() as session:
            duplicate_filters = [User.cpf == cpf]
            if args.email:
                duplicate_filters.append(User.email == args.email)

            existing = await session.execute(select(User).where(or_(*duplicate_filters)))
            if existing.scalar_one_or_none() is not None:
                raise ValueError("Já existe usuário com este CPF ou e-mail.")

            user = User(
                cpf=cpf,
                email=args.email,
                hashed_password=argon2_helper.hash(password),
                is_active=not args.inactive,
                is_superuser=args.superuser,
                is_verified=args.verified,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    except IntegrityError as exc:
        raise ValueError("Não foi possível criar o usuário: CPF ou e-mail já cadastrado.") from exc
    finally:
        await engine.dispose()


async def async_main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        user = await create_user(args)
    except Exception as exc:
        print(f"Erro ao criar usuário: {exc}", file=sys.stderr)
        return 1

    print(f"Usuário criado: id={user.id} cpf={user.cpf} email={user.email or '-'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    return asyncio.run(async_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
