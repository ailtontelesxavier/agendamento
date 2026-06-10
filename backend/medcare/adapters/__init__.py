"""Adaptadores de persistência.

Implementações dos repositórios: em memória (in_memory.py) e SQLAlchemy (sqlalchemy_repo.py).
"""
from medcare.adapters.in_memory import InMemoryAppointmentRepository, InMemorySessionRepository

__all__ = [
    "InMemoryAppointmentRepository",
    "InMemorySessionRepository",
    "SQLAlchemyAppointmentRepository",
]


def __getattr__(name: str):
    """Lazy import para SQLAlchemyAppointmentRepository (evita erro sem sqlalchemy)."""
    if name == "SQLAlchemyAppointmentRepository":
        from medcare.adapters.sqlalchemy_repo import SQLAlchemyAppointmentRepository
        return SQLAlchemyAppointmentRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
