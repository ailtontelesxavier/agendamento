def test_whatsapp_creates_appointment_without_datetime_scope_error(appointment_use_cases, whatsapp_use_cases):
    response = None
    for message in ["1", "1", "1", "20/06/2026", "08:00", "Ana Pereira", "SIM"]:
        response = whatsapp_use_cases.handle_message("+55 99 99999-9999", message)

    assert response is not None
    assert response["session_step"] == "done"

    created = appointment_use_cases.list_appointments()
    assert len(created) == 1
    assert created[0].patient_name == "Ana Pereira"
    assert created[0].source.value == "whatsapp"


def test_whatsapp_lists_user_appointments(appointment_use_cases, whatsapp_use_cases):
    appointment_use_cases.create_appointment(
        patient_name="Ana Pereira",
        phone="5599999999999",
        specialty="Clínica Geral",
        doctor="Dr. Carlos Silva",
        date="2026-06-20",
        time="08:00",
    )

    response = whatsapp_use_cases.handle_message("+55 99 99999-9999", "2")

    assert response["session_step"] == "list_appointments"
    assert "Dr. Carlos Silva" in response["message"]
