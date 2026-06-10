"""Camada de casos de uso (application layer).

Coordena a lógica de negócio entre as rotas da API e os repositórios.
"""
from medcare.application.use_cases import (
    AppointmentAlreadyBooked,
    AppointmentNotFound,
    AppointmentUseCases,
    WhatsAppUseCases,
)

__all__ = [
    "AppointmentAlreadyBooked",
    "AppointmentNotFound",
    "AppointmentUseCases",
    "WhatsAppUseCases",
]

