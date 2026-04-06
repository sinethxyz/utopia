"""Pydantic schemas for the System Audit layer.

Request schemas (Create) and response schemas (Read) for all 5 system
audit entity types: model providers, model runs, retrieval runs,
event log entries, and outbox events.
"""

import datetime
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from utopia.enums import ProcessingStatus


# ---------------------------------------------------------------------------
# Model Providers
# ---------------------------------------------------------------------------

class ModelProviderCreate(BaseModel):
    name: str
    provider_kind: str
    api_base_url: str | None = None
    default_model: str | None = None
    is_active: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class ModelProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    provider_kind: str
    api_base_url: str | None
    default_model: str | None
    is_active: bool
    config: dict[str, Any]
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Model Runs
# ---------------------------------------------------------------------------

class ModelRunCreate(BaseModel):
    operator_id: uuid.UUID
    provider_id: uuid.UUID
    model_name: str
    module_name: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: int | None = None
    status: str
    error_message: str | None = None
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output_summary: dict[str, Any] = Field(default_factory=dict)


class ModelRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    provider_id: uuid.UUID
    model_name: str
    module_name: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    latency_ms: int | None
    status: str
    error_message: str | None
    input_summary: dict[str, Any]
    output_summary: dict[str, Any]
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Retrieval Runs
# ---------------------------------------------------------------------------

class RetrievalRunCreate(BaseModel):
    operator_id: uuid.UUID
    model_run_id: uuid.UUID | None = None
    collection: str
    query_text: str | None = None
    query_vector_dim: int | None = None
    top_k: int
    results_returned: int | None = None
    latency_ms: int | None = None
    filter_criteria: dict[str, Any] = Field(default_factory=dict)
    result_ids: list[Any] = Field(default_factory=list)


class RetrievalRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    model_run_id: uuid.UUID | None
    collection: str
    query_text: str | None
    query_vector_dim: int | None
    top_k: int
    results_returned: int | None
    latency_ms: int | None
    filter_criteria: dict[str, Any]
    result_ids: list[Any]
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Event Log
# ---------------------------------------------------------------------------

class EventLogCreate(BaseModel):
    operator_id: uuid.UUID | None = None
    event_type: str
    source: str
    severity: str = "info"
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)
    related_entity_kind: str | None = None
    related_entity_id: uuid.UUID | None = None


class EventLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID | None
    event_type: str
    source: str
    severity: str
    message: str
    payload: dict[str, Any]
    related_entity_kind: str | None
    related_entity_id: uuid.UUID | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Outbox Events
# ---------------------------------------------------------------------------

class OutboxEventCreate(BaseModel):
    operator_id: uuid.UUID | None = None
    event_type: str
    destination: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: ProcessingStatus = ProcessingStatus.pending


class OutboxEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID | None
    event_type: str
    destination: str
    payload: dict[str, Any]
    status: ProcessingStatus
    attempts: int
    last_error: str | None
    created_at: datetime.datetime
    processed_at: datetime.datetime | None
