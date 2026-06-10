"""Camada de domínio do MedCare.

Exporta as entidades e enums centrais do sistema.
"""
from medcare.domain.models import Appointment, AppointmentStatus, AppointmentSource

__all__ = ["Appointment", "AppointmentStatus", "AppointmentSource"]
