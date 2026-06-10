"""Portas (interfaces) de repositório para o domínio de agendamento.

Define os contratos abstratos que os adaptadores devem implementar.
"""
from typing import Protocol

from medcare.domain import Appointment


class AppointmentRepository(Protocol):
    """Contrato para repositório de agendamentos.

    Implementações podem ser em memória (testes) ou PostgreSQL (produção).
    Todos os métodos são assíncronos para compatibilidade com drivers async.
    """

    async def add(self, appointment: Appointment) -> Appointment:
        """Insere um novo agendamento."""
        ...

    async def get(self, appointment_id: str) -> Appointment | None:
        """Busca um agendamento pelo ID. Retorna None se não encontrado."""
        ...

    async def list(
        self,
        date: str | None = None,
        doctor: str | None = None,
        status: str | None = None,
        phone: str | None = None,
    ) -> list[Appointment]:
        """Lista agendamentos com filtros opcionais.

        Args:
            date: Filtrar por data (YYYY-MM-DD).
            doctor: Filtrar por nome do médico.
            status: Filtrar por status (confirmed, cancelled, etc).
            phone: Filtrar por telefone do paciente.

        Returns:
            Lista de agendamentos ordenados por data e horário.
        """
        ...

    async def update(self, appointment: Appointment) -> Appointment:
        """Atualiza um agendamento existente."""
        ...


class SessionRepository(Protocol):
    """Contrato para repositório de sessões do WhatsApp.

    Gerencia o estado da conversa bot por telefone.
    """

    async def get(self, phone: str) -> dict | None:
        """Recupera a sessão ativa de um telefone. Retorna None se não existe."""
        ...

    async def set(self, phone: str, session: dict) -> None:
        """Cria ou atualiza a sessão de um telefone."""
        ...

    async def delete(self, phone: str) -> None:
        """Remove a sessão de um telefone."""
        ...

    async def list(self) -> dict[str, dict]:
        """Retorna todas as sessões ativas mapeadas por telefone."""
        ...
