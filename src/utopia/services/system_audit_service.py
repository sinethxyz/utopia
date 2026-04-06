"""SystemAuditService — bounded-context service for the System Audit layer.

Records AI model invocations, retrieval runs, system events, and
outbox events. Provides the audit trail for debugging reasoning
chains, replaying decisions, and monitoring costs.
"""

import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.enums import ProcessingStatus
from utopia.models.system_audit import (
    EventLog,
    ModelProvider,
    ModelRun,
    OutboxEvent,
    RetrievalRun,
)
from utopia.schemas.system_audit import (
    EventLogCreate,
    ModelProviderCreate,
    ModelRunCreate,
    OutboxEventCreate,
    RetrievalRunCreate,
)


class SystemAuditService:
    """Service for the System Audit bounded context.

    All writes go through this service. The service owns ID generation
    and provides query methods for audit trail inspection.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # Model Providers
    # ------------------------------------------------------------------

    async def create_model_provider(
        self, data: ModelProviderCreate
    ) -> ModelProvider:
        provider = ModelProvider(
            id=uuid7(),
            name=data.name,
            provider_kind=data.provider_kind,
            api_base_url=data.api_base_url,
            default_model=data.default_model,
            is_active=data.is_active,
            config=data.config,
        )
        self._session.add(provider)
        await self._session.flush()
        return provider

    async def get_model_provider(
        self, provider_id: _uuid.UUID
    ) -> ModelProvider | None:
        return await self._session.get(ModelProvider, provider_id)

    async def list_model_providers(
        self, active_only: bool = False
    ) -> list[ModelProvider]:
        stmt = select(ModelProvider)
        if active_only:
            stmt = stmt.where(ModelProvider.is_active == True)  # noqa: E712
        stmt = stmt.order_by(ModelProvider.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Model Runs
    # ------------------------------------------------------------------

    async def record_model_run(self, data: ModelRunCreate) -> ModelRun:
        run = ModelRun(
            id=uuid7(),
            operator_id=data.operator_id,
            provider_id=data.provider_id,
            model_name=data.model_name,
            module_name=data.module_name,
            prompt_tokens=data.prompt_tokens,
            completion_tokens=data.completion_tokens,
            total_tokens=data.total_tokens,
            latency_ms=data.latency_ms,
            status=data.status,
            error_message=data.error_message,
            input_summary=data.input_summary,
            output_summary=data.output_summary,
        )
        self._session.add(run)
        await self._session.flush()
        return run

    async def get_model_run(self, run_id: _uuid.UUID) -> ModelRun | None:
        return await self._session.get(ModelRun, run_id)

    async def list_model_runs(
        self,
        operator_id: _uuid.UUID,
        module_name: str | None = None,
        limit: int = 50,
    ) -> list[ModelRun]:
        stmt = (
            select(ModelRun)
            .where(ModelRun.operator_id == operator_id)
        )
        if module_name is not None:
            stmt = stmt.where(ModelRun.module_name == module_name)
        stmt = stmt.order_by(ModelRun.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Retrieval Runs
    # ------------------------------------------------------------------

    async def record_retrieval_run(
        self, data: RetrievalRunCreate
    ) -> RetrievalRun:
        run = RetrievalRun(
            id=uuid7(),
            operator_id=data.operator_id,
            model_run_id=data.model_run_id,
            collection=data.collection,
            query_text=data.query_text,
            query_vector_dim=data.query_vector_dim,
            top_k=data.top_k,
            results_returned=data.results_returned,
            latency_ms=data.latency_ms,
            filter_criteria=data.filter_criteria,
            result_ids=data.result_ids,
        )
        self._session.add(run)
        await self._session.flush()
        return run

    async def get_retrieval_run(
        self, run_id: _uuid.UUID
    ) -> RetrievalRun | None:
        return await self._session.get(RetrievalRun, run_id)

    async def list_retrieval_runs(
        self,
        operator_id: _uuid.UUID,
        collection: str | None = None,
        limit: int = 50,
    ) -> list[RetrievalRun]:
        stmt = (
            select(RetrievalRun)
            .where(RetrievalRun.operator_id == operator_id)
        )
        if collection is not None:
            stmt = stmt.where(RetrievalRun.collection == collection)
        stmt = stmt.order_by(RetrievalRun.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Event Log
    # ------------------------------------------------------------------

    async def log_event(self, data: EventLogCreate) -> EventLog:
        event = EventLog(
            id=uuid7(),
            operator_id=data.operator_id,
            event_type=data.event_type,
            source=data.source,
            severity=data.severity,
            message=data.message,
            payload=data.payload,
            related_entity_kind=data.related_entity_kind,
            related_entity_id=data.related_entity_id,
        )
        self._session.add(event)
        await self._session.flush()
        return event

    async def get_event(self, event_id: _uuid.UUID) -> EventLog | None:
        return await self._session.get(EventLog, event_id)

    async def list_events(
        self,
        operator_id: _uuid.UUID | None = None,
        event_type: str | None = None,
        severity: str | None = None,
        limit: int = 100,
    ) -> list[EventLog]:
        stmt = select(EventLog)
        if operator_id is not None:
            stmt = stmt.where(EventLog.operator_id == operator_id)
        if event_type is not None:
            stmt = stmt.where(EventLog.event_type == event_type)
        if severity is not None:
            stmt = stmt.where(EventLog.severity == severity)
        stmt = stmt.order_by(EventLog.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Outbox Events
    # ------------------------------------------------------------------

    async def create_outbox_event(self, data: OutboxEventCreate) -> OutboxEvent:
        event = OutboxEvent(
            id=uuid7(),
            operator_id=data.operator_id,
            event_type=data.event_type,
            destination=data.destination,
            payload=data.payload,
            status=data.status,
        )
        self._session.add(event)
        await self._session.flush()
        return event

    async def get_outbox_event(
        self, event_id: _uuid.UUID
    ) -> OutboxEvent | None:
        return await self._session.get(OutboxEvent, event_id)

    async def list_outbox_events(
        self,
        status: ProcessingStatus | None = None,
        limit: int = 50,
    ) -> list[OutboxEvent]:
        stmt = select(OutboxEvent)
        if status is not None:
            stmt = stmt.where(OutboxEvent.status == status)
        stmt = stmt.order_by(OutboxEvent.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def mark_outbox_processed(
        self, event_id: _uuid.UUID
    ) -> OutboxEvent | None:
        event = await self._session.get(OutboxEvent, event_id)
        if event is None:
            return None
        event.status = ProcessingStatus.processed
        event.attempts = event.attempts + 1
        await self._session.flush()
        return event

    async def mark_outbox_failed(
        self, event_id: _uuid.UUID, error: str
    ) -> OutboxEvent | None:
        event = await self._session.get(OutboxEvent, event_id)
        if event is None:
            return None
        event.status = ProcessingStatus.failed
        event.attempts = event.attempts + 1
        event.last_error = error
        await self._session.flush()
        return event
