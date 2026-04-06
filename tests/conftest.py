"""Shared test fixtures for the Utopia test suite.

Provides async database session, service instances, FastAPI test client,
and factory helpers for creating test entities.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from utopia.api.app import app
from utopia.api.deps import get_db
from utopia.config import settings
from utopia.db import Base

# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

# Use the same database URL but with a test-aware approach:
# In CI, point DATABASE_URL to a test database.
# Locally, this uses the configured database.
TEST_DATABASE_URL = settings.database_url


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db_engine():
    """Create a test engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession]:
    """Provide a transactional database session that rolls back after each test.

    This ensures test isolation without requiring a separate test database
    or schema recreation between tests.
    """
    async with db_engine.connect() as conn:
        transaction = await conn.begin()
        session_factory = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with session_factory() as session:
            yield session
        await transaction.rollback()


@pytest.fixture
def override_db(db_session: AsyncSession):
    """Override the FastAPI database dependency with the test session."""

    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def client(override_db) -> AsyncGenerator[AsyncClient]:
    """Provide an async HTTP client for API integration tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Service fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def evidence_service(db_session: AsyncSession):
    from utopia.services.evidence_service import EvidenceService
    return EvidenceService(db_session)


@pytest.fixture
def execution_service(db_session: AsyncSession):
    from utopia.services.execution_service import ExecutionService
    return ExecutionService(db_session)


@pytest.fixture
def vector_service(db_session: AsyncSession):
    from utopia.services.vector_service import VectorService
    return VectorService(db_session)


@pytest.fixture
def physiology_service(db_session: AsyncSession):
    from utopia.services.physiology_service import PhysiologyService
    return PhysiologyService(db_session)


@pytest.fixture
def aether_service(db_session: AsyncSession):
    from utopia.services.aether_service import AetherService
    return AetherService(db_session)


@pytest.fixture
def reasoning_service(db_session: AsyncSession):
    from utopia.services.reasoning_service import ReasoningService
    return ReasoningService(db_session)


@pytest.fixture
def review_service(db_session: AsyncSession):
    from utopia.services.review_service import ReviewService
    return ReviewService(db_session)


@pytest.fixture
def system_audit_service(db_session: AsyncSession):
    from utopia.services.system_audit_service import SystemAuditService
    return SystemAuditService(db_session)


@pytest.fixture
def vector_search_service(db_session: AsyncSession):
    from utopia.services.vector_search_service import VectorSearchService
    return VectorSearchService(db_session)


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def operator_id() -> uuid.UUID:
    """A stable test operator UUID."""
    return uuid.UUID("01234567-0123-0123-0123-012345678901")


@pytest.fixture
def thread_id() -> uuid.UUID:
    """A stable test thread UUID."""
    return uuid.UUID("01234567-0123-0123-0123-012345678902")


# ---------------------------------------------------------------------------
# AI module mocking
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_claude():
    """Mock the Claude API provider to avoid real API calls in tests."""
    with patch("utopia.ai.providers.claude.complete", new_callable=AsyncMock) as mock:
        mock.return_value = (
            '{"state_kind": "execute", "confidence": 0.8, "contributing_factors": []}',
            {
                "model": "claude-sonnet-4-20250514",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "latency_ms": 200,
            },
        )
        yield mock


@pytest.fixture
def mock_embeddings():
    """Mock the OpenAI embeddings provider to avoid real API calls in tests."""
    with patch(
        "utopia.ai.providers.openai_embeddings.generate_embedding",
        new_callable=AsyncMock,
    ) as mock_single, patch(
        "utopia.ai.providers.openai_embeddings.generate_embeddings_batch",
        new_callable=AsyncMock,
    ) as mock_batch:
        # Return a fake 1536-dim vector
        fake_vector = [0.01] * 1536
        mock_single.return_value = fake_vector
        mock_batch.return_value = [fake_vector]
        yield mock_single, mock_batch
