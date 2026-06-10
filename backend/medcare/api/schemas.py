from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

try:
    from fastapi_users.schemas import BaseUserCreate, BaseUserUpdate
except ModuleNotFoundError:
    BaseUserCreate = BaseModel
    BaseUserUpdate = BaseModel


class UserRead(BaseModel):
    id: UUID
    cpf: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = {"from_attributes": True}


class UserCreate(BaseUserCreate):
    cpf: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")


class UserUpdate(BaseUserUpdate):
    cpf: Optional[str] = Field(None, min_length=11, max_length=11, pattern=r"^\d{11}$")


class CPFLoginRequest(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")
    password: str


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
