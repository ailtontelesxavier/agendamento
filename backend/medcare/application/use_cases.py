"""Casos de uso do sistema de agendamento.

Implementa a lógica de negócio para agendamentos e conversas WhatsApp.
Todos os métodos de acesso a dados são assíncronos.
"""
from datetime import datetime
import uuid

from medcare.domain import Appointment, AppointmentSource, AppointmentStatus
from medcare.domain.catalog import SLOTS, SPECIALTIES
from medcare.ports import AppointmentRepository, SessionRepository


class AppointmentAlreadyBooked(Exception):
    """Lançado quando o horário escolhido já está ocupado."""
    pass


class AppointmentNotFound(Exception):
    """Lançado quando o agendamento não é encontrado pelo ID."""
    pass


class AppointmentUseCases:
    """Casos de uso para operações de agendamento.

    Fornece métodos para criar, listar, atualizar e cancelar consultas,
    além de consultar horários disponíveis e estatísticas.
    """

    def __init__(self, appointments: AppointmentRepository) -> None:
        """Inicializa com um repositório de agendamentos (in_memory ou SQLAlchemy)."""
        self.appointments = appointments

    def specialties(self) -> dict:
        """Retorna a lista de especialidades e seus médicos."""
        return {"specialties": list(SPECIALTIES.keys()), "doctors": SPECIALTIES}

    async def booked_slots(self, doctor: str, date: str) -> list[str]:
        """Retorna os horários já ocupados para um médico em uma data específica."""
        appointments = await self.appointments.list(date=date, doctor=doctor)
        return [
            appointment.time
            for appointment in appointments
            if appointment.status != AppointmentStatus.CANCELLED
        ]

    async def available_slots(self, doctor: str, date: str) -> dict:
        """Retorna horários disponíveis e ocupados para um médico/data."""
        booked = await self.booked_slots(doctor, date)
        return {"slots": [slot for slot in SLOTS if slot not in booked], "booked": booked}

    async def list_appointments(
        self,
        date: str | None = None,
        doctor: str | None = None,
        status: str | None = None,
    ) -> list[Appointment]:
        """Lista agendamentos com filtros opcionais (data, médico, status)."""
        return await self.appointments.list(date=date, doctor=doctor, status=status)

    async def create_appointment(
        self,
        patient_name: str,
        phone: str,
        specialty: str,
        doctor: str,
        date: str,
        time: str,
        notes: str = "",
        source: AppointmentSource = AppointmentSource.WEB,
    ) -> Appointment:
        """Cria um novo agendamento. Levanta AppointmentAlreadyBooked se o horário estiver ocupado."""
        booked = await self.booked_slots(doctor, date)
        if time in booked:
            raise AppointmentAlreadyBooked("Horário já ocupado")

        appointment = Appointment(
            id=str(uuid.uuid4()),
            patient_name=patient_name,
            phone=phone,
            specialty=specialty,
            doctor=doctor,
            date=date,
            time=time,
            notes=notes,
            source=source,
        )
        return await self.appointments.add(appointment)

    async def update_status(self, appointment_id: str, status: str) -> Appointment:
        """Atualiza o status de um agendamento. Levanta AppointmentNotFound se não existir."""
        appointment = await self.appointments.get(appointment_id)
        if not appointment:
            raise AppointmentNotFound("Agendamento não encontrado")
        appointment.status = AppointmentStatus(status)
        return await self.appointments.update(appointment)

    async def cancel(self, appointment_id: str) -> None:
        """Cancela um agendamento pelo ID."""
        await self.update_status(appointment_id, AppointmentStatus.CANCELLED.value)

    async def stats(self) -> dict:
        """Retorna estatísticas gerais: total, confirmados, cancelados, por fonte."""
        appointments = await self.appointments.list()
        return {
            "total": len(appointments),
            "confirmed": sum(1 for item in appointments if item.status == AppointmentStatus.CONFIRMED),
            "cancelled": sum(1 for item in appointments if item.status == AppointmentStatus.CANCELLED),
            "completed": sum(1 for item in appointments if item.status == AppointmentStatus.COMPLETED),
            "via_whatsapp": sum(1 for item in appointments if item.source == AppointmentSource.WHATSAPP),
            "via_web": sum(1 for item in appointments if item.source == AppointmentSource.WEB),
        }


class WhatsAppUseCases:
    """Casos de uso para o bot de agendamento via WhatsApp.

    Gerencia conversas guiadas por etapas (step-by-step) para agendar consultas
    ou listar agendamentos existentes do usuário.
    """

    def __init__(self, appointments: AppointmentUseCases, sessions: SessionRepository) -> None:
        """Inicializa com casos de uso de agendamento e repositório de sessões."""
        self.appointments = appointments
        self.sessions = sessions

    def normalize_phone(self, phone: str) -> str:
        """Normaliza o telefone removendo caracteres especiais (+, espaço, hífen)."""
        return phone.replace("+", "").replace(" ", "").replace("-", "")

    async def handle_message(self, phone: str, message: str) -> dict:
        """Processa uma mensagem recebida do WhatsApp e retorna a resposta."""
        phone = self.normalize_phone(phone)
        session = await self.sessions.get(phone) or {"step": "start", "phone": phone}
        session = await self.process_message(phone, message, session)
        await self.sessions.set(phone, session)
        return {
            "to": phone,
            "message": self.format_response(session),
            "session_step": session.get("step"),
        }

    async def reset(self, phone: str) -> None:
        """Reinicia a sessão de conversa de um telefone."""
        await self.sessions.delete(phone)

    async def list_sessions(self) -> dict[str, dict]:
        """Retorna todas as sessões ativas do WhatsApp."""
        return await self.sessions.list()

    async def process_message(self, phone: str, message: str, session: dict) -> dict:
        """Máquina de estados que processa a mensagem e atualiza a sessão."""
        msg = message.strip()
        step = session.get("step", "start")

        if msg.lower() in ["oi", "olá", "ola", "inicio", "início", "menu"]:
            return {"step": "start", "phone": phone}

        if step == "start":
            if msg == "1":
                session["step"] = "choose_specialty"
            elif msg == "2":
                user_appointments = await self.appointments.appointments.list(phone=phone)
                session["step"] = "list_appointments"
                session["user_appointments"] = [item.to_dict() for item in user_appointments]
            else:
                session["step"] = "start"

        elif step == "choose_specialty":
            specs = list(SPECIALTIES.keys())
            try:
                idx = int(msg) - 1
                if 0 <= idx < len(specs):
                    session["specialty"] = specs[idx]
                    session["step"] = "choose_doctor"
            except ValueError:
                pass

        elif step == "choose_doctor":
            spec = session.get("specialty", "")
            docs = SPECIALTIES.get(spec, [])
            try:
                idx = int(msg) - 1
                if 0 <= idx < len(docs):
                    session["doctor"] = docs[idx]
                    session["step"] = "choose_date"
            except ValueError:
                pass

        elif step == "choose_date":
            try:
                dt = datetime.strptime(msg, "%d/%m/%Y")
                session["date"] = dt.strftime("%Y-%m-%d")
                session["date_display"] = msg
                doctor = session.get("doctor", "")
                slots_data = await self.appointments.available_slots(doctor, session["date"])
                session["available_slots"] = slots_data["slots"]
                session["step"] = "choose_time"
            except ValueError:
                pass

        elif step == "choose_time":
            doctor = session.get("doctor", "")
            date = session.get("date", "")
            booked = await self.appointments.booked_slots(doctor, date)
            if msg in SLOTS and msg not in booked:
                session["time"] = msg
                session["step"] = "get_name"

        elif step == "get_name":
            session["patient_name"] = msg
            session["step"] = "confirm"

        elif step == "confirm":
            if msg.upper() == "SIM":
                appointment = await self.appointments.create_appointment(
                    patient_name=session["patient_name"],
                    phone=phone,
                    specialty=session["specialty"],
                    doctor=session["doctor"],
                    date=session["date"],
                    time=session["time"],
                    notes="Via WhatsApp",
                    source=AppointmentSource.WHATSAPP,
                )
                session["appointment_id"] = appointment.id
                session["step"] = "done"
            elif msg.upper() in ["NÃO", "NAO"]:
                session["step"] = "start"

        return session

    def format_response(self, session: dict) -> str:
        """Gera a mensagem de resposta com base no estado atual da sessão."""
        step = session.get("step", "start")

        if step == "start":
            return (
                "Olá! Bem-vindo à *Clínica MedCare*.\n\n"
                "Para agendar sua consulta, responda com o número da opção desejada:\n\n"
                "1 Agendar consulta\n"
                "2 Ver meus agendamentos\n"
                "3 Cancelar consulta\n"
                "4 Falar com atendente\n\n"
                "_Digite o número da opção:_"
            )
        if step == "choose_specialty":
            specs = list(SPECIALTIES.keys())
            lines = "\n".join(f"{idx + 1} {spec}" for idx, spec in enumerate(specs))
            return f"*Escolha a especialidade:*\n\n{lines}\n\n_Digite o número:_"
        if step == "choose_doctor":
            spec = session.get("specialty", "")
            docs = SPECIALTIES.get(spec, [])
            lines = "\n".join(f"{idx + 1} {doctor}" for idx, doctor in enumerate(docs))
            return f"*Médicos disponíveis em {spec}:*\n\n{lines}\n\n_Digite o número:_"
        if step == "choose_date":
            return "*Qual a data desejada?*\n\nInforme no formato: *DD/MM/AAAA*\n_(ex: 25/06/2025)_"
        if step == "choose_time":
            available = session.get("available_slots", [])
            if not available:
                return "Não há horários disponíveis nessa data. Tente outra data.\n\nInforme uma nova data (DD/MM/AAAA):"
            lines = "\n".join(f"• {slot}" for slot in available)
            return f"*Horários disponíveis:*\n\n{lines}\n\n_Digite o horário desejado (HH:MM):_"
        if step == "get_name":
            return "*Qual o seu nome completo?*"
        if step == "confirm":
            return (
                f"*Confirme seu agendamento:*\n\n"
                f"Especialidade: {session.get('specialty')}\n"
                f"Médico: {session.get('doctor')}\n"
                f"Data: {session.get('date_display')}\n"
                f"Horário: {session.get('time')}\n"
                f"Paciente: {session.get('patient_name')}\n\n"
                "Confirmar? Responda *SIM* ou *NÃO*"
            )
        if step == "done":
            code = session.get("appointment_id", "")[:8].upper()
            return (
                f"*Consulta agendada com sucesso!*\n\n"
                f"Código: *{code}*\n"
                f"{session.get('doctor')}\n"
                f"{session.get('date_display')} às {session.get('time')}\n\n"
                "Lembre-se de chegar 15 min antes.\n"
                "Em caso de dúvidas, entre em contato conosco."
            )
        if step == "list_appointments":
            appointments = session.get("user_appointments", [])
            if not appointments:
                return "Você ainda não possui agendamentos."
            lines = [
                f"• {item['date']} às {item['time']} com {item['doctor']} ({item['status']})"
                for item in appointments
            ]
            return "*Seus agendamentos:*\n\n" + "\n".join(lines)

        return "Não entendi. Digite *oi* para recomeçar."
