"""Configuração de conexão async com PostgreSQL via SQLAlchemy 2.

Fornece o engine async, factory de sessões e dependência FastAPI para injeção.
"""
import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://medcare:medcare@database:5432/medcare")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependência FastAPI que fornece uma sessão async por request.

    Uso: ``Depends(get_async_session)`` em rotas ou repositórios.
    """
    async with async_session_maker() as session:
        yield session
