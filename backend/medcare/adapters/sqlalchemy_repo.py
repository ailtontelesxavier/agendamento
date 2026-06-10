"""Adaptador SQLAlchemy async para repositório de agendamentos.

Implementa o contrato AppointmentRepository usando SQLAlchemy 2 com asyncpg.
Cada operação abre uma sessão async independente.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from medcare.adapters.db.connection import async_session_maker
from medcare.adapters.db.models import AppointmentDB
from medcare.domain import Appointment, AppointmentSource, AppointmentStatus


class SQLAlchemyAppointmentRepository:
    """Repositório de agendamentos persistido em PostgreSQL.

    Usa SQLAlchemy 2 async com asyncpg como driver.
    Cada método cria uma sessão via async_session_maker.
    """

    def __init__(self) -> None:
        pass

    async def add(self, appointment: Appointment) -> Appointment:
        """Insere um novo agendamento no banco de dados.

        Args:
            appointment: Entidade de agendamento a ser persistida.

        Returns:
            A mesma entidade com o ID gerado.
        """
        async with async_session_maker() as session:
            db_appt = AppointmentDB(
                id=uuid.UUID(appointment.id),
                patient_name=appointment.patient_name,
                phone=appointment.phone,
                specialty=appointment.specialty,
                doctor=appointment.doctor,
                date=appointment.date,
                time=appointment.time,
                notes=appointment.notes,
                status=appointment.status.value,
                source=appointment.source.value,
                created_at=appointment.created_at,
            )
            session.add(db_appt)
            await session.commit()
        return appointment

    async def get(self, appointment_id: str) -> Appointment | None:
        """Busca um agendamento pelo UUID.

        Args:
            appointment_id: UUID do agendamento como string.

        Returns:
            Entidade Appointment ou None se não encontrado.
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(AppointmentDB).where(AppointmentDB.id == uuid.UUID(appointment_id))
            )
            db_appt = result.scalar_one_or_none()
            if db_appt is None:
                return None
            return self._to_domain(db_appt)

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
            doctor: Filtrar por médico.
            status: Filtrar por status.
            phone: Filtrar por telefone.

        Returns:
            Lista ordenada por data e horário.
        """
        async with async_session_maker() as session:
            stmt = select(AppointmentDB)
            if date:
                stmt = stmt.where(AppointmentDB.date == date)
            if doctor:
                stmt = stmt.where(AppointmentDB.doctor == doctor)
            if status:
                stmt = stmt.where(AppointmentDB.status == status)
            if phone:
                stmt = stmt.where(AppointmentDB.phone == phone)
            stmt = stmt.order_by(AppointmentDB.date, AppointmentDB.time)
            result = await session.execute(stmt)
            return [self._to_domain(row) for row in result.scalars().all()]

    async def update(self, appointment: Appointment) -> Appointment:
        """Atualiza um agendamento existente.

        Args:
            appointment: Entidade com dados atualizados.

        Returns:
            A entidade atualizada.
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(AppointmentDB).where(AppointmentDB.id == uuid.UUID(appointment.id))
            )
            db_appt = result.scalar_one()
            db_appt.patient_name = appointment.patient_name
            db_appt.phone = appointment.phone
            db_appt.specialty = appointment.specialty
            db_appt.doctor = appointment.doctor
            db_appt.date = appointment.date
            db_appt.time = appointment.time
            db_appt.notes = appointment.notes
            db_appt.status = appointment.status.value
            db_appt.source = appointment.source.value
            await session.commit()
        return appointment

    @staticmethod
    def _to_domain(db_appt: AppointmentDB) -> Appointment:
        """Converte um registro do banco para entidade de domínio."""
        return Appointment(
            id=str(db_appt.id),
            patient_name=db_appt.patient_name,
            phone=db_appt.phone,
            specialty=db_appt.specialty,
            doctor=db_appt.doctor,
            date=db_appt.date,
            time=db_appt.time,
            notes=db_appt.notes or "",
            status=AppointmentStatus(db_appt.status),
            source=AppointmentSource(db_appt.source),
            created_at=db_appt.created_at,
        )
