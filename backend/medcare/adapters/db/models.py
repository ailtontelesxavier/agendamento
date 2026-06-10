import uuid
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    email: Mapped[str | None] = mapped_column(
        String(length=320), unique=True, index=True, nullable=True
    )
    cpf: Mapped[str] = mapped_column(String(11), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    appointments: Mapped[list["AppointmentDB"]] = relationship(
        back_populates="user", lazy="selectin"
    )


class AppointmentDB(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    doctor: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False)
    time: Mapped[str] = mapped_column(String(5), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    source: Mapped[str] = mapped_column(String(20), default="web")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    user: Mapped["User | None"] = relationship(back_populates="appointments")
