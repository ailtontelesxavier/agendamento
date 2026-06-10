import pytest

from medcare.application import AppointmentAlreadyBooked
from medcare.domain import AppointmentStatus


@pytest.mark.asyncio
async def test_create_and_list_appointment(appointment_use_cases):
    appointment = await appointment_use_cases.create_appointment(
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
    items = await appointment_use_cases.list_appointments()
    assert [item.id for item in items] == [appointment.id]


@pytest.mark.asyncio
async def test_rejects_booked_slot(appointment_use_cases):
    payload = {
        "patient_name": "Maria Souza",
        "phone": "5599999999999",
        "specialty": "Clínica Geral",
        "doctor": "Dr. Carlos Silva",
        "date": "2026-06-20",
        "time": "08:00",
    }
    await appointment_use_cases.create_appointment(**payload)

    with pytest.raises(AppointmentAlreadyBooked, match="Horário já ocupado"):
        await appointment_use_cases.create_appointment(**(payload | {"patient_name": "João Lima"}))


@pytest.mark.asyncio
async def test_cancel_appointment_removes_slot_from_booked_slots(appointment_use_cases):
    appointment = await appointment_use_cases.create_appointment(
        patient_name="Maria Souza",
        phone="5599999999999",
        specialty="Clínica Geral",
        doctor="Dr. Carlos Silva",
        date="2026-06-20",
        time="08:00",
    )

    await appointment_use_cases.cancel(appointment.id)

    items = await appointment_use_cases.list_appointments()
    assert items[0].status == AppointmentStatus.CANCELLED
    slots = await appointment_use_cases.available_slots("Dr. Carlos Silva", "2026-06-20")
    assert "08:00" in slots["slots"]
