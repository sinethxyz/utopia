"""aether ORM models — typed memory and knowledge graph.

Aether stores extracted intelligence: concepts, mechanisms, tradeoffs,
heuristics, protocols, rules, patterns, and the polymorphic edge graph
that relates them. These knowledge atoms feed the AI Fabric's reasoning
modules (Council, Contradiction Checker, Context Retriever).

Matches: Utopia Formal Architecture DB etc.md section 13.
"""

import datetime
import decimal
import uuid

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from utopia.db import Base


class Source(Base):
    """An ingested knowledge source (book, paper, essay, transcript, etc.)."""

    __tablename__ = "sources"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    source_kind: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    ingest_status: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class SourceChunk(Base):
    """A semantically coherent chunk of a source document."""

    __tablename__ = "source_chunks"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("aether.sources.id"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    semantic_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class Extraction(Base):
    """AI-generated extraction from a source — thesis, summary, confidence."""

    __tablename__ = "extractions"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("aether.sources.id"), nullable=False
    )
    extraction_version: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_status: Mapped[str] = mapped_column(Text, nullable=False)
    thesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[decimal.Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    extracted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    model_run_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)


class Concept(Base):
    """A named concept extracted and deduplicated across sources."""

    __tablename__ = "concepts"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    canonical_name: Mapped[str] = mapped_column(Text, nullable=False)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    confidence: Mapped[decimal.Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class Mechanism(Base):
    """A causal mechanism — how something works."""

    __tablename__ = "mechanisms"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    causal_logic: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[decimal.Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class Tradeoff(Base):
    """A named tension between two opposing poles."""

    __tablename__ = "tradeoffs"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    pole_a: Mapped[str] = mapped_column(Text, nullable=False)
    pole_b: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class FailureMode(Base):
    """A named failure mode with early warning signals."""

    __tablename__ = "failure_modes"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    early_signals: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default="{}"
    )
    domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class Heuristic(Base):
    """A practical rule of thumb with applicability conditions."""

    __tablename__ = "heuristics"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    applicability: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[decimal.Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class DiagnosticQuestion(Base):
    """A high-leverage diagnostic question for problem interrogation."""

    __tablename__ = "diagnostic_questions"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_class: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str | None] = mapped_column(Text, nullable=True)
    usefulness_score: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(6, 3), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class Protocol(Base):
    """A structured step-by-step procedure for a domain."""

    __tablename__ = "protocols"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    protocol_name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[list] = mapped_column(JSONB, nullable=False)
    applicability: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class LensPack(Base):
    """A curated collection of knowledge atoms for a specific domain."""

    __tablename__ = "lens_packs"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    source_basis: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class LensPackItem(Base):
    """A single knowledge atom within a lens pack."""

    __tablename__ = "lens_pack_items"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    lens_pack_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("aether.lens_packs.id"), nullable=False
    )
    item_kind: Mapped[str] = mapped_column(Text, nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    weight: Mapped[decimal.Decimal | None] = mapped_column(Numeric(6, 3), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class Case(Base):
    """A recorded case study — internal or external — with lessons."""

    __tablename__ = "cases"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    case_kind: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    lessons: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class Rule(Base):
    """A promoted behavioral or strategic rule with evidence backing.

    Rules are derived from patterns in traces and calibration records.
    They are the output of the Review subsystem's learning loop.
    """

    __tablename__ = "rules"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    rule_text: Mapped[str] = mapped_column(Text, nullable=False)
    rule_kind: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    confidence: Mapped[decimal.Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    first_observed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_validated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class Pattern(Base):
    """A recurring behavioral or physiological pattern."""

    __tablename__ = "patterns"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    pattern_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pattern_kind: Mapped[str] = mapped_column(Text, nullable=False)
    recurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    confidence: Mapped[decimal.Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class Edge(Base):
    """A typed directed edge in the knowledge graph.

    Polymorphic: src_kind/dst_kind identify the entity type;
    src_id/dst_id are the entity UUIDs. This avoids foreign key
    constraints across heterogeneous entity types while preserving
    graph traversal capability.
    """

    __tablename__ = "edges"
    __table_args__ = {"schema": "aether"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("core.operators.id"), nullable=False
    )
    src_kind: Mapped[str] = mapped_column(Text, nullable=False)
    dst_kind: Mapped[str] = mapped_column(Text, nullable=False)
    src_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    dst_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    edge_type: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[decimal.Decimal | None] = mapped_column(Numeric(6, 3), nullable=True)
    provenance: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
