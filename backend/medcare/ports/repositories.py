from typing import Protocol

from medcare.domain import Appointment


class AppointmentRepository(Protocol):
    async def add(self, appointment: Appointment) -> Appointment: ...

    async def get(self, appointment_id: str) -> Appointment | None: ...

    async def list(
        self,
        date: str | None = None,
        doctor: str | None = None,
        status: str | None = None,
        phone: str | None = None,
    ) -> list[Appointment]: ...

    async def update(self, appointment: Appointment) -> Appointment: ...


class SessionRepository(Protocol):
    async def get(self, phone: str) -> dict | None: ...

    async def set(self, phone: str, session: dict) -> None: ...

    async def delete(self, phone: str) -> None: ...

    async def list(self) -> dict[str, dict]: ...
