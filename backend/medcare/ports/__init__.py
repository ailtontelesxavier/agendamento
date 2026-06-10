"""Portas do domínio MedCare.

Exporta os contratos de repositório usados pelos casos de uso.
"""
from medcare.ports.repositories import AppointmentRepository, SessionRepository

__all__ = ["AppointmentRepository", "SessionRepository"]
