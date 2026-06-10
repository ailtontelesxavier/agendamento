import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from medcare.adapters.db.connection import async_session_maker
from medcare.adapters.db.models import AppointmentDB
from medcare.domain import Appointment, AppointmentSource, AppointmentStatus


class SQLAlchemyAppointmentRepository:
    def __init__(self) -> None:
        pass

    async def add(self, appointment: Appointment) -> Appointment:
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
