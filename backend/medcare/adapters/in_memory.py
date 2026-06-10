from medcare.domain import Appointment


class InMemoryAppointmentRepository:
    def __init__(self) -> None:
        self._items: dict[str, Appointment] = {}

    def add(self, appointment: Appointment) -> Appointment:
        self._items[appointment.id] = appointment
        return appointment

    def get(self, appointment_id: str) -> Appointment | None:
        return self._items.get(appointment_id)

    def list(
        self,
        date: str | None = None,
        doctor: str | None = None,
        status: str | None = None,
        phone: str | None = None,
    ) -> list[Appointment]:
        appointments = list(self._items.values())
        if date:
            appointments = [item for item in appointments if item.date == date]
        if doctor:
            appointments = [item for item in appointments if item.doctor == doctor]
        if status:
            appointments = [item for item in appointments if item.status.value == status]
        if phone:
            appointments = [item for item in appointments if item.phone == phone]
        return sorted(appointments, key=lambda item: (item.date, item.time))

    def update(self, appointment: Appointment) -> Appointment:
        self._items[appointment.id] = appointment
        return appointment


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    def get(self, phone: str) -> dict | None:
        session = self._items.get(phone)
        return dict(session) if session else None

    def set(self, phone: str, session: dict) -> None:
        self._items[phone] = dict(session)

    def delete(self, phone: str) -> None:
        self._items.pop(phone, None)

    def list(self) -> dict[str, dict]:
        return {phone: dict(session) for phone, session in self._items.items()}

