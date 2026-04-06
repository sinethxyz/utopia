"""Pydantic schemas for the Aether knowledge layer.

Request schemas (Create) and response schemas (Read) for all 16 Aether
entity types: sources, chunks, extractions, concepts, mechanisms, tradeoffs,
failure modes, heuristics, diagnostic questions, protocols, lens packs,
lens pack items, cases, rules, patterns, and edges.
"""

import datetime
import uuid
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

class SourceCreate(BaseModel):
    operator_id: uuid.UUID
    source_kind: str
    title: str | None = None
    author: str | None = None
    published_at: datetime.date | None = None
    ingest_status: str = "pending"
    canonical_uri: str | None = None
    storage_uri: str | None = None
    checksum: str | None = None
    metadata_: dict[str, Any] | None = None


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    source_kind: str
    title: str | None
    author: str | None
    published_at: datetime.date | None
    ingest_status: str
    canonical_uri: str | None
    storage_uri: str | None
    checksum: str | None
    metadata_: dict[str, Any] | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Source Chunks
# ---------------------------------------------------------------------------

class SourceChunkCreate(BaseModel):
    source_id: uuid.UUID
    chunk_index: int
    raw_text: str
    token_count: int | None = None
    semantic_label: str | None = None
    metadata_: dict[str, Any] | None = None


class SourceChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: uuid.UUID
    chunk_index: int
    raw_text: str
    token_count: int | None
    semantic_label: str | None
    metadata_: dict[str, Any] | None


# ---------------------------------------------------------------------------
# Extractions
# ---------------------------------------------------------------------------

class ExtractionCreate(BaseModel):
    source_id: uuid.UUID
    extraction_version: str
    extraction_status: str = "pending"
    thesis: str | None = None
    summary: str | None = None
    confidence: Decimal | None = None
    extracted_at: datetime.datetime | None = None
    model_run_id: uuid.UUID | None = None


class ExtractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: uuid.UUID
    extraction_version: str
    extraction_status: str
    thesis: str | None
    summary: str | None
    confidence: Decimal | None
    extracted_at: datetime.datetime | None
    model_run_id: uuid.UUID | None


# ---------------------------------------------------------------------------
# Concepts
# ---------------------------------------------------------------------------

class ConceptCreate(BaseModel):
    operator_id: uuid.UUID
    canonical_name: str
    definition: str | None = None
    domain: str | None = None
    confidence: Decimal | None = None


class ConceptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    canonical_name: str
    definition: str | None
    domain: str | None
    source_count: int
    confidence: Decimal | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Mechanisms
# ---------------------------------------------------------------------------

class MechanismCreate(BaseModel):
    operator_id: uuid.UUID
    name: str
    description: str
    causal_logic: str | None = None
    domain: str | None = None
    confidence: Decimal | None = None


class MechanismRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    name: str
    description: str
    causal_logic: str | None
    domain: str | None
    confidence: Decimal | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Tradeoffs
# ---------------------------------------------------------------------------

class TradeoffCreate(BaseModel):
    operator_id: uuid.UUID
    name: str
    pole_a: str
    pole_b: str
    description: str | None = None
    domain: str | None = None


class TradeoffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    name: str
    pole_a: str
    pole_b: str
    description: str | None
    domain: str | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Failure Modes
# ---------------------------------------------------------------------------

class FailureModeCreate(BaseModel):
    operator_id: uuid.UUID
    name: str
    description: str
    early_signals: list[str] = Field(default_factory=list)
    domain: str | None = None
    severity: str | None = None


class FailureModeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    name: str
    description: str
    early_signals: list[str]
    domain: str | None
    severity: str | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Heuristics
# ---------------------------------------------------------------------------

class HeuristicCreate(BaseModel):
    operator_id: uuid.UUID
    statement: str
    domain: str | None = None
    applicability: str | None = None
    failure_conditions: str | None = None
    confidence: Decimal | None = None


class HeuristicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    statement: str
    domain: str | None
    applicability: str | None
    failure_conditions: str | None
    confidence: Decimal | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Diagnostic Questions
# ---------------------------------------------------------------------------

class DiagnosticQuestionCreate(BaseModel):
    operator_id: uuid.UUID
    question_text: str
    question_class: str
    domain: str | None = None
    usefulness_score: Decimal | None = None


class DiagnosticQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    question_text: str
    question_class: str
    domain: str | None
    usefulness_score: Decimal | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------

class ProtocolCreate(BaseModel):
    operator_id: uuid.UUID
    protocol_name: str
    domain: str
    purpose: str | None = None
    steps: list[Any] = Field(default_factory=list)
    applicability: str | None = None


class ProtocolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    protocol_name: str
    domain: str
    purpose: str | None
    steps: list[Any]
    applicability: str | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Lens Packs
# ---------------------------------------------------------------------------

class LensPackCreate(BaseModel):
    operator_id: uuid.UUID
    name: str
    domain: str
    description: str | None = None
    version: str = "1.0"
    source_basis: list[Any] = Field(default_factory=list)


class LensPackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    name: str
    domain: str
    description: str | None
    version: str
    source_basis: list[Any]
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Lens Pack Items
# ---------------------------------------------------------------------------

class LensPackItemCreate(BaseModel):
    lens_pack_id: uuid.UUID
    item_kind: str
    item_id: uuid.UUID
    weight: Decimal | None = None
    metadata_: dict[str, Any] | None = None


class LensPackItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lens_pack_id: uuid.UUID
    item_kind: str
    item_id: uuid.UUID
    weight: Decimal | None
    metadata_: dict[str, Any] | None


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

class CaseCreate(BaseModel):
    operator_id: uuid.UUID
    title: str
    case_kind: str
    summary: str | None = None
    outcome: str | None = None
    lessons: list[Any] = Field(default_factory=list)


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    title: str
    case_kind: str
    summary: str | None
    outcome: str | None
    lessons: list[Any]
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

class RuleCreate(BaseModel):
    operator_id: uuid.UUID
    rule_text: str
    rule_kind: str
    confidence: Decimal | None = None
    first_observed_at: datetime.datetime | None = None


class RuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    rule_text: str
    rule_kind: str
    evidence_count: int
    confidence: Decimal | None
    first_observed_at: datetime.datetime | None
    last_validated_at: datetime.datetime | None
    active: bool
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

class PatternCreate(BaseModel):
    operator_id: uuid.UUID
    pattern_name: str
    description: str | None = None
    pattern_kind: str
    confidence: Decimal | None = None


class PatternRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    pattern_name: str
    description: str | None
    pattern_kind: str
    recurrence_count: int
    confidence: Decimal | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------

class EdgeCreate(BaseModel):
    operator_id: uuid.UUID
    src_kind: str
    dst_kind: str
    src_id: uuid.UUID
    dst_id: uuid.UUID
    edge_type: str
    weight: Decimal | None = None
    provenance: dict[str, Any] | None = None


class EdgeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    src_kind: str
    dst_kind: str
    src_id: uuid.UUID
    dst_id: uuid.UUID
    edge_type: str
    weight: Decimal | None
    provenance: dict[str, Any] | None
    created_at: datetime.datetime
