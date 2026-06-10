from medcare.adapters.in_memory import InMemoryAppointmentRepository, InMemorySessionRepository

__all__ = [
    "InMemoryAppointmentRepository",
    "InMemorySessionRepository",
]


def __getattr__(name: str):
    if name == "SQLAlchemyAppointmentRepository":
        from medcare.adapters.sqlalchemy_repo import SQLAlchemyAppointmentRepository

        return SQLAlchemyAppointmentRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
