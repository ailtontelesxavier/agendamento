from typing import Optional

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    patient_name: str
    phone: str
    specialty: str
    doctor: str
    date: str
    time: str
    notes: Optional[str] = ""


class AppointmentUpdate(BaseModel):
    status: str


class WhatsAppMessage(BaseModel):
    from_number: str
    message: str
    session_id: Optional[str] = None

