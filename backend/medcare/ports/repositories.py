from typing import Protocol

from medcare.domain import Appointment


class AppointmentRepository(Protocol):
    def add(self, appointment: Appointment) -> Appointment:
        ...

    def get(self, appointment_id: str) -> Appointment | None:
        ...

    def list(
        self,
        date: str | None = None,
        doctor: str | None = None,
        status: str | None = None,
        phone: str | None = None,
    ) -> list[Appointment]:
        ...

    def update(self, appointment: Appointment) -> Appointment:
        ...


class SessionRepository(Protocol):
    def get(self, phone: str) -> dict | None:
        ...

    def set(self, phone: str, session: dict) -> None:
        ...

    def delete(self, phone: str) -> None:
        ...

    def list(self) -> dict[str, dict]:
        ...

