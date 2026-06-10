"""Adaptadores em memória para testes e fallback.

Implementam os contratos de repositório usando dicionários Python.
Úteis para testes unitários sem dependência de banco de dados.
"""
from medcare.domain import Appointment


class InMemoryAppointmentRepository:
    """Repositório de agendamentos em memória.

    Armazena agendamentos em um dict indexado por ID.
    Ideal para testes e desenvolvimento sem banco de dados.
    """

    def __init__(self) -> None:
        self._items: dict[str, Appointment] = {}

    async def add(self, appointment: Appointment) -> Appointment:
        """Insere um agendamento no dicionário interno."""
        self._items[appointment.id] = appointment
        return appointment

    async def get(self, appointment_id: str) -> Appointment | None:
        """Busca agendamento por ID."""
        return self._items.get(appointment_id)

    async def list(
        self,
        date: str | None = None,
        doctor: str | None = None,
        status: str | None = None,
        phone: str | None = None,
    ) -> list[Appointment]:
        """Lista agendamentos aplicando filtros opcionais e ordenando por data/hora."""
        appointments = list(self._items.values())
        if date:
            appointments = [item for item in appointments if item.date == date]
        if doctor:
            appointments = [item for item in appointments if item.doctor == doctor]
        if status:
            appointments = [item for item in appointments if item.status.value == status]
        if phone:
            appointments = [item for item in appointments if item.phone == phone]
        return sorted(appointments, key=lambda item: (item.date, item.time))

    async def update(self, appointment: Appointment) -> Appointment:
        """Atualiza um agendamento existente pelo ID."""
        self._items[appointment.id] = appointment
        return appointment


class InMemorySessionRepository:
    """Repositório de sessões WhatsApp em memória.

    Armazena estado da conversa bot por telefone em um dict.
    """

    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    async def get(self, phone: str) -> dict | None:
        """Recupera sessão pelo telefone. Retorna cópia ou None."""
        session = self._items.get(phone)
        return dict(session) if session else None

    async def set(self, phone: str, session: dict) -> None:
        """Armazena ou atualiza sessão do telefone."""
        self._items[phone] = dict(session)

    async def delete(self, phone: str) -> None:
        """Remove sessão do telefone."""
        self._items.pop(phone, None)

    async def list(self) -> dict[str, dict]:
        """Retorna todas as sessões ativas como dict phone->session."""
        return {phone: dict(session) for phone, session in self._items.items()}
