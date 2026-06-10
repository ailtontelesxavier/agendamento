"""Schemas Pydantic para request/response da API.

Define os modelos de validação de entrada e saída para autenticação,
agendamentos e mensagens WhatsApp.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

try:
    from fastapi_users.schemas import BaseUserCreate, BaseUserUpdate
except ModuleNotFoundError:
    BaseUserCreate = BaseModel
    BaseUserUpdate = BaseModel


class UserRead(BaseModel):
    """Schema de leitura de usuário retornado pela API."""
    id: UUID
    cpf: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = {"from_attributes": True}


class UserCreate(BaseUserCreate):
    """Schema para registro de novo usuário. Requer CPF de 11 dígitos."""
    cpf: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")


class UserUpdate(BaseUserUpdate):
    """Schema para atualização de dados do usuário."""
    cpf: Optional[str] = Field(None, min_length=11, max_length=11, pattern=r"^\d{11}$")


class CPFLoginRequest(BaseModel):
    """Schema para login por CPF + senha."""
    cpf: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")
    password: str


class AppointmentCreate(BaseModel):
    """Schema para criação de agendamento."""
    patient_name: str
    phone: str
    specialty: str
    doctor: str
    date: str
    time: str
    notes: Optional[str] = ""


class AppointmentUpdate(BaseModel):
    """Schema para atualização de status de agendamento."""
    status: str


class WhatsAppMessage(BaseModel):
    """Schema para mensagem recebida do webhook WhatsApp."""
    from_number: str
    message: str
    session_id: Optional[str] = None
