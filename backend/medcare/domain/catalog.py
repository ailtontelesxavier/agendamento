"""Catálogo estático de especialidades médicas e horários disponíveis.

Este módulo contém os dados fixos utilizados pelo sistema de agendamento.
"""

SPECIALTIES: dict[str, list[str]] = {
    "Clínica Geral": ["Dr. Carlos Silva", "Dra. Ana Costa"],
    "Cardiologia": ["Dr. Roberto Melo", "Dra. Lucia Ferreira"],
    "Dermatologia": ["Dra. Patrícia Nunes", "Dr. Eduardo Lima"],
    "Ortopedia": ["Dr. Marcos Souza", "Dra. Juliana Rocha"],
    "Pediatria": ["Dra. Fernanda Alves", "Dr. Thiago Martins"],
}
"""Mapping de especialidades para lista de médicos disponíveis."""

SLOTS: list[str] = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
]
"""Lista de horários disponíveis para agendamento (08:00–17:00 com intervalo para almoço)."""
