from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from medcare.adapters import InMemoryAppointmentRepository, InMemorySessionRepository
from medcare.application import (
    AppointmentAlreadyBooked,
    AppointmentNotFound,
    AppointmentUseCases,
    WhatsAppUseCases,
)
from medcare.api.schemas import AppointmentCreate, AppointmentUpdate, WhatsAppMessage


def create_app(
    appointment_use_cases: AppointmentUseCases | None = None,
    whatsapp_use_cases: WhatsAppUseCases | None = None,
) -> FastAPI:
    if appointment_use_cases is None:
        appointment_repo = InMemoryAppointmentRepository()
        appointment_use_cases = AppointmentUseCases(appointment_repo)
    if whatsapp_use_cases is None:
        whatsapp_use_cases = WhatsAppUseCases(appointment_use_cases, InMemorySessionRepository())

    app = FastAPI(title="Sistema de Agendamento", version="1.0.0")
    app.state.appointments = appointment_use_cases
    app.state.whatsapp = whatsapp_use_cases

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {"status": "ok", "service": "Agendamento MedCare"}

    @app.get("/specialties")
    def list_specialties():
        return appointment_use_cases.specialties()

    @app.get("/available-slots")
    def available_slots(doctor: str, date: str):
        return appointment_use_cases.available_slots(doctor, date)

    @app.get("/appointments")
    def list_appointments(
        date: str | None = None,
        doctor: str | None = None,
        status: str | None = None,
    ):
        appointments = appointment_use_cases.list_appointments(date=date, doctor=doctor, status=status)
        return {"appointments": [item.to_dict() for item in appointments], "total": len(appointments)}

    @app.post("/appointments")
    def create_appointment(data: AppointmentCreate):
        try:
            appointment = appointment_use_cases.create_appointment(
                patient_name=data.patient_name,
                phone=data.phone,
                specialty=data.specialty,
                doctor=data.doctor,
                date=data.date,
                time=data.time,
                notes=data.notes or "",
            )
        except AppointmentAlreadyBooked as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"appointment": appointment.to_dict(), "message": "Agendamento criado com sucesso"}

    @app.patch("/appointments/{appointment_id}")
    def update_appointment(appointment_id: str, data: AppointmentUpdate):
        try:
            appointment = appointment_use_cases.update_status(appointment_id, data.status)
        except AppointmentNotFound as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Status inválido") from exc
        return {"appointment": appointment.to_dict()}

    @app.delete("/appointments/{appointment_id}")
    def delete_appointment(appointment_id: str):
        try:
            appointment_use_cases.cancel(appointment_id)
        except AppointmentNotFound as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"message": "Agendamento cancelado"}

    @app.post("/whatsapp/webhook")
    def whatsapp_webhook(data: WhatsAppMessage):
        return whatsapp_use_cases.handle_message(data.from_number, data.message)

    @app.get("/whatsapp/sessions")
    def list_sessions():
        sessions = whatsapp_use_cases.list_sessions()
        return {"sessions": sessions, "total": len(sessions)}

    @app.post("/whatsapp/reset/{phone}")
    def reset_session(phone: str):
        whatsapp_use_cases.reset(phone)
        return {"message": "Sessão reiniciada"}

    @app.get("/stats")
    def stats():
        return appointment_use_cases.stats()

    return app

