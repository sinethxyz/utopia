"""System Audit ORM models — AI orchestration and audit trail.

Records every AI model invocation, retrieval run, and significant
system event. Provides the audit trail needed to debug reasoning
chains, replay decisions, and monitor costs.

- ModelProvider: registered AI provider (Anthropic, OpenAI, etc.)
- ModelRun: a single LLM invocation with token counts and latency
- RetrievalRun: a single vector/semantic search with results
- EventLog: timestamped system events with severity
- OutboxEvent: transactional outbox for async delivery

Matches: Utopia Formal Architecture DB etc.md System Audit section.
"""

import datetime
import uuid

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utopia.db import Base
from utopia.enums import ProcessingStatus


class ModelProvider(Base):
    """A registered AI model provider.

    Tracks provider metadata and configuration. Each model run
    references a provider so costs and usage can be aggregated.
    """

    __tablename__ = "model_providers"
    __table_args__ = {"schema": "system"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    provider_kind: Mapped[str] = mapped_column(Text, nullable=False)
    api_base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class ModelRun(Base):
    """A single LLM invocation.

    Records the module that triggered the call, the model used,
    token counts, latency, and a summary of input/output. This is
    the core audit record for AI Fabric reasoning.
    """

    __tablename__ = "model_runs"
    __table_args__ = {"schema": "system"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("system.model_providers.id"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    module_name: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_summary: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    output_summary: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    provider: Mapped[ModelProvider] = relationship(foreign_keys=[provider_id])


class RetrievalRun(Base):
    """A single vector/semantic search execution.

    Tracks what was queried, how many results returned, latency,
    and the IDs of retrieved documents. Optionally links to the
    model run that triggered the retrieval.
    """

    __tablename__ = "retrieval_runs"
    __table_args__ = {"schema": "system"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    model_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("system.model_runs.id"), nullable=True
    )
    collection: Mapped[str] = mapped_column(Text, nullable=False)
    query_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    query_vector_dim: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    results_returned: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    filter_criteria: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    result_ids: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    model_run: Mapped[ModelRun | None] = relationship(foreign_keys=[model_run_id])


class EventLog(Base):
    """A timestamped system event.

    Captures significant events: module activations, errors, state
    transitions, configuration changes. The polymorphic
    related_entity_kind + related_entity_id pattern links events to
    any entity in the system.
    """

    __tablename__ = "event_log"
    __table_args__ = {"schema": "system"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("core.operators.id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="info"
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    related_entity_kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class OutboxEvent(Base):
    """Transactional outbox for reliable async event delivery.

    Events that need to be delivered to external systems (webhooks,
    queues, notifications) are written here atomically with the
    business transaction. A background worker picks them up and
    delivers, tracking attempts and errors.
    """

    __tablename__ = "outbox_events"
    __table_args__ = {"schema": "system"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("core.operators.id"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    destination: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status", schema="core", create_type=False),
        nullable=False,
    )
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    processed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
