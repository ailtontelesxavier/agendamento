"""Gerenciamento de usuários e autenticação JWT com fastapi-users.

Fornece UserManager customizado com autenticação por CPF, configuração JWT
com Argon2, e dependências FastAPI para injeção de usuário autenticado.
"""
import os
import uuid

from fastapi import Depends, HTTPException, status
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import Argon2Hasher, PasswordHelper
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import pwdlib

from medcare.adapters.db.connection import get_async_session
from medcare.adapters.db.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE-ME-IN-PRODUCTION")

argon2_helper = PasswordHelper(pwdlib.PasswordHash((Argon2Hasher(),)))


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Gerenciador de usuários com suporte a autenticação por CPF.

    Estende o UserManager padrão do fastapi-users com:
    - get_by_cpf(): busca usuário por CPF
    - authenticate_cpf(): autentica por CPF + senha (Argon2)
    """
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY
    password_helper = argon2_helper

    async def get_by_cpf(self, cpf: str) -> User:
        from medcare.adapters.db.connection import async_session_maker

        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.cpf == cpf))
            user = result.scalar_one_or_none()
        if user is None:
            from fastapi_users import exceptions
            raise exceptions.UserNotExists("User not found")
        return user

    async def authenticate_cpf(self, cpf: str, password: str) -> User | None:
        try:
            user = await self.get_by_cpf(cpf)
        except Exception:
            self.password_helper.hash(password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            password, user.hashed_password
        )
        if not verified:
            return None
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})
        return user


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Dependência que fornece o repositório de usuários SQLAlchemy."""
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    """Dependência que fornece o UserManager com helper Argon2."""
    yield UserManager(user_db, password_helper=argon2_helper)


def get_jwt_strategy() -> JWTStrategy:
    """Estratégia JWT com expiração de 1 hora (3600s)."""
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)


transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_backend = AuthenticationBackend(name="jwt", transport=transport, get_strategy=get_jwt_strategy)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
"""Dependência FastAPI que retorna o usuário autenticado ativo. Levanta 401 se não autenticado."""
