"""Modelos de domínio do sistema de agendamento MedCare.

Contém as entidades centrais, enums de status e fonte de agendamento.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class AppointmentStatus(StrEnum):
    """Status possíveis de um agendamento."""

    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    PENDING = "pending"


class AppointmentSource(StrEnum):
    """Origem do agendamento (web ou WhatsApp)."""

    WEB = "web"
    WHATSAPP = "whatsapp"


@dataclass(slots=True)
class Appointment:
    """Entidade de agendamento de consulta médica.

    Attributes:
        id: Identificador único do agendamento (UUID como string).
        patient_name: Nome completo do paciente.
        phone: Telefone do paciente com código do país.
        specialty: Especialidade médica (ex: "Clínica Geral").
        doctor: Nome do médico responsável.
        date: Data do agendamento no formato ISO (YYYY-MM-DD).
        time: Horário do agendamento no formato HH:MM.
        notes: Observações adicionais sobre o agendamento.
        status: Status atual do agendamento.
        source: Origem do agendamento (web ou WhatsApp).
        created_at: Data e hora de criação do registro.
    """

    id: str
    patient_name: str
    phone: str
    specialty: str
    doctor: str
    date: str
    time: str
    notes: str = ""
    status: AppointmentStatus = AppointmentStatus.CONFIRMED
    source: AppointmentSource = AppointmentSource.WEB
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Serializa o agendamento para dicionário.

        Returns:
            Dict com todos os campos do agendamento serializados.
        """
        return {
            "id": self.id,
            "patient_name": self.patient_name,
            "phone": self.phone,
            "specialty": self.specialty,
            "doctor": self.doctor,
            "date": self.date,
            "time": self.time,
            "notes": self.notes,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "source": self.source.value,
        }
