import os
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from medcare.adapters import InMemoryAppointmentRepository, InMemorySessionRepository
from medcare.api.schemas import AppointmentCreate, AppointmentUpdate, WhatsAppMessage
from medcare.application import (
    AppointmentAlreadyBooked,
    AppointmentNotFound,
    AppointmentUseCases,
    WhatsAppUseCases,
)


def _load_database_repository():
    try:
        from medcare.adapters.sqlalchemy_repo import SQLAlchemyAppointmentRepository
    except ModuleNotFoundError as exc:
        if exc.name == "sqlalchemy":
            raise RuntimeError(
                "DATABASE_URL foi configurado, mas SQLAlchemy não está instalado. "
                "Execute `poetry install` ou remova DATABASE_URL para usar o repositório em memória."
            ) from exc
        raise
    return SQLAlchemyAppointmentRepository()


def create_app(
    appointment_use_cases: AppointmentUseCases | None = None,
    whatsapp_use_cases: WhatsAppUseCases | None = None,
) -> FastAPI:
    use_database = os.getenv("DATABASE_URL") is not None

    if appointment_use_cases is None:
        if use_database:
            repo = _load_database_repository()
        else:
            repo = InMemoryAppointmentRepository()
        appointment_use_cases = AppointmentUseCases(repo)

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

    require_auth = None
    if use_database:
        try:
            from medcare.api.auth import router as auth_router
            from medcare.adapters.db.user_manager import current_active_user
        except ModuleNotFoundError as exc:
            if exc.name in {"sqlalchemy", "fastapi_users"}:
                raise RuntimeError(
                    "DATABASE_URL foi configurado, mas dependências de banco/autenticação "
                    "não estão instaladas. Execute `poetry install`."
                ) from exc
            raise
        app.include_router(auth_router)

        async def _require_auth(user=Depends(current_active_user)):
            if user is None:
                raise HTTPException(status_code=401, detail="Não autenticado")
            return user

        require_auth = _require_auth

    def _dep() -> Any:
        return require_auth

    @app.get("/")
    async def root():
        return {"status": "ok", "service": "Agendamento MedCare"}

    @app.get("/specialties")
    async def list_specialties():
        return appointment_use_cases.specialties()

    @app.get("/available-slots")
    async def available_slots(doctor: str, date: str):
        return await appointment_use_cases.available_slots(doctor, date)

    async def _auth(user: Annotated[Any, Depends(_dep)] = None):
        return user

    @app.get("/appointments")
    async def list_appointments(
        date: str | None = None,
        doctor: str | None = None,
        status: str | None = None,
        user: Annotated[Any, Depends(_dep)] = None,
    ):
        if require_auth is not None and user is None:
            raise HTTPException(status_code=401, detail="Não autenticado")
        appointments = await appointment_use_cases.list_appointments(date=date, doctor=doctor, status=status)
        return {"appointments": [item.to_dict() for item in appointments], "total": len(appointments)}

    @app.post("/appointments")
    async def create_appointment(
        data: AppointmentCreate,
        user: Annotated[Any, Depends(_dep)] = None,
    ):
        if require_auth is not None and user is None:
            raise HTTPException(status_code=401, detail="Não autenticado")
        try:
            appointment = await appointment_use_cases.create_appointment(
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
    async def update_appointment(
        appointment_id: str,
        data: AppointmentUpdate,
        user: Annotated[Any, Depends(_dep)] = None,
    ):
        if require_auth is not None and user is None:
            raise HTTPException(status_code=401, detail="Não autenticado")
        try:
            appointment = await appointment_use_cases.update_status(appointment_id, data.status)
        except AppointmentNotFound as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Status inválido") from exc
        return {"appointment": appointment.to_dict()}

    @app.delete("/appointments/{appointment_id}")
    async def delete_appointment(
        appointment_id: str,
        user: Annotated[Any, Depends(_dep)] = None,
    ):
        if require_auth is not None and user is None:
            raise HTTPException(status_code=401, detail="Não autenticado")
        try:
            await appointment_use_cases.cancel(appointment_id)
        except AppointmentNotFound as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"message": "Agendamento cancelado"}

    @app.post("/whatsapp/webhook")
    async def whatsapp_webhook(data: WhatsAppMessage):
        return await whatsapp_use_cases.handle_message(data.from_number, data.message)

    @app.get("/whatsapp/sessions")
    async def list_sessions(user: Annotated[Any, Depends(_dep)] = None):
        if require_auth is not None and user is None:
            raise HTTPException(status_code=401, detail="Não autenticado")
        sessions = await whatsapp_use_cases.list_sessions()
        return {"sessions": sessions, "total": len(sessions)}

    @app.post("/whatsapp/reset/{phone}")
    async def reset_session(phone: str, user: Annotated[Any, Depends(_dep)] = None):
        if require_auth is not None and user is None:
            raise HTTPException(status_code=401, detail="Não autenticado")
        await whatsapp_use_cases.reset(phone)
        return {"message": "Sessão reiniciada"}

    @app.get("/stats")
    async def stats(user: Annotated[Any, Depends(_dep)] = None):
        if require_auth is not None and user is None:
            raise HTTPException(status_code=401, detail="Não autenticado")
        return await appointment_use_cases.stats()

    return app
