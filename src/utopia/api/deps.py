"""FastAPI dependency injection providers.

Pattern: each bounded-context service is a dependency that owns
its own session. Routes depend on the service, never on the raw
session. The service exposes commit() so the route controls the
transaction boundary without touching the session directly.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from utopia.db import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


# ---------------------------------------------------------------------------
# Service dependencies — one per bounded context
# ---------------------------------------------------------------------------

def get_vector_service(
    session: AsyncSession = Depends(get_db),
):
    from utopia.services.vector_service import VectorService
    return VectorService(session)


def get_evidence_service(
    session: AsyncSession = Depends(get_db),
):
    from utopia.services.evidence_service import EvidenceService
    return EvidenceService(session)


def get_execution_service(
    session: AsyncSession = Depends(get_db),
):
    from utopia.services.execution_service import ExecutionService
    return ExecutionService(session)
