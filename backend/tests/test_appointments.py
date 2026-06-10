import pytest

from medcare.application import AppointmentAlreadyBooked
from medcare.domain import AppointmentStatus


def test_create_and_list_appointment(appointment_use_cases):
    appointment = appointment_use_cases.create_appointment(
        patient_name="Maria Souza",
        phone="5599999999999",
        specialty="Clínica Geral",
        doctor="Dr. Carlos Silva",
        date="2026-06-20",
        time="08:00",
        notes="Primeira consulta",
    )

    assert appointment.patient_name == "Maria Souza"
    assert appointment.source.value == "web"
    assert [item.id for item in appointment_use_cases.list_appointments()] == [appointment.id]


def test_rejects_booked_slot(appointment_use_cases):
    payload = {
        "patient_name": "Maria Souza",
        "phone": "5599999999999",
        "specialty": "Clínica Geral",
        "doctor": "Dr. Carlos Silva",
        "date": "2026-06-20",
        "time": "08:00",
    }
    appointment_use_cases.create_appointment(**payload)

    with pytest.raises(AppointmentAlreadyBooked, match="Horário já ocupado"):
        appointment_use_cases.create_appointment(**(payload | {"patient_name": "João Lima"}))


def test_cancel_appointment_removes_slot_from_booked_slots(appointment_use_cases):
    appointment = appointment_use_cases.create_appointment(
        patient_name="Maria Souza",
        phone="5599999999999",
        specialty="Clínica Geral",
        doctor="Dr. Carlos Silva",
        date="2026-06-20",
        time="08:00",
    )

    appointment_use_cases.cancel(appointment.id)

    assert appointment_use_cases.list_appointments()[0].status == AppointmentStatus.CANCELLED
    assert "08:00" in appointment_use_cases.available_slots("Dr. Carlos Silva", "2026-06-20")["slots"]
