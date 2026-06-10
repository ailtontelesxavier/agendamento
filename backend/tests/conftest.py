from contextlib import asynccontextmanager
from datetime import datetime

import pytest
import pytest_asyncio

from medcare.adapters import InMemoryAppointmentRepository, InMemorySessionRepository
from medcare.api import create_app
from medcare.application import AppointmentUseCases, WhatsAppUseCases
from medcare.domain import Appointment


@pytest.fixture
def appointment_repository():
    return InMemoryAppointmentRepository()


@pytest.fixture
def session_repository():
    return InMemorySessionRepository()


@pytest.fixture
def appointment_use_cases(appointment_repository):
    return AppointmentUseCases(appointment_repository)


@pytest.fixture
def whatsapp_use_cases(appointment_use_cases, session_repository):
    return WhatsAppUseCases(appointment_use_cases, session_repository)


@pytest.fixture
def app(appointment_use_cases, whatsapp_use_cases):
    return create_app(appointment_use_cases, whatsapp_use_cases)


@pytest_asyncio.fixture
async def client(app):
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_model_time():
    @asynccontextmanager
    async def _mock(time=datetime(2024, 1, 1)):
        original_default_factory = Appointment.__dataclass_fields__["created_at"].default_factory
        Appointment.__dataclass_fields__["created_at"].default_factory = lambda: time
        try:
            yield time
        finally:
            Appointment.__dataclass_fields__["created_at"].default_factory = original_default_factory

    return _mock
