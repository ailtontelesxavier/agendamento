from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class AppointmentStatus(StrEnum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    PENDING = "pending"


class AppointmentSource(StrEnum):
    WEB = "web"
    WHATSAPP = "whatsapp"


@dataclass(slots=True)
class Appointment:
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

