"""Pydantic schemas for the Reasoning layer.

Request schemas (Create) and response schemas (Read) for all 6 reasoning
entity types: problems, problem structures, interrogations, decision briefs,
option paths, and contradiction reports.
"""

import datetime
import uuid
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Problems
# ---------------------------------------------------------------------------

class ProblemCreate(BaseModel):
    operator_id: uuid.UUID
    title: str
    raw_prompt: str
    problem_kind: str | None = None
    urgency_score: Decimal | None = None
    stakes_score: Decimal | None = None
    uncertainty_score: Decimal | None = None
    state_at_creation: str | None = None
    thread_id: uuid.UUID | None = None


class ProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    title: str
    raw_prompt: str
    problem_kind: str | None
    urgency_score: Decimal | None
    stakes_score: Decimal | None
    uncertainty_score: Decimal | None
    state_at_creation: str | None
    thread_id: uuid.UUID | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Problem Structures
# ---------------------------------------------------------------------------

class ProblemStructureCreate(BaseModel):
    problem_id: uuid.UUID
    objective: str | None = None
    stakes: str | None = None
    actors: list[Any] = Field(default_factory=list)
    incentives: list[Any] = Field(default_factory=list)
    constraints: list[Any] = Field(default_factory=list)
    assumptions: list[Any] = Field(default_factory=list)
    unknowns: list[Any] = Field(default_factory=list)
    irreversibilities: list[Any] = Field(default_factory=list)
    bottlenecks: list[Any] = Field(default_factory=list)
    observable_facts: list[Any] = Field(default_factory=list)
    narrative_layer: list[Any] = Field(default_factory=list)
    distortion_candidates: list[Any] = Field(default_factory=list)
    confidence: Decimal | None = None


class ProblemStructureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    problem_id: uuid.UUID
    objective: str | None
    stakes: str | None
    actors: list[Any]
    incentives: list[Any]
    constraints: list[Any]
    assumptions: list[Any]
    unknowns: list[Any]
    irreversibilities: list[Any]
    bottlenecks: list[Any]
    observable_facts: list[Any]
    narrative_layer: list[Any]
    distortion_candidates: list[Any]
    confidence: Decimal | None
    generated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Interrogations
# ---------------------------------------------------------------------------

class InterrogationCreate(BaseModel):
    problem_id: uuid.UUID
    interrogation_kind: str
    questions: list[Any] = Field(default_factory=list)
    rationale: dict[str, Any] | None = None


class InterrogationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    problem_id: uuid.UUID
    interrogation_kind: str
    questions: list[Any]
    rationale: dict[str, Any] | None
    generated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Decision Briefs
# ---------------------------------------------------------------------------

class DecisionBriefCreate(BaseModel):
    problem_id: uuid.UUID
    classification: str | None = None
    summary: str | None = None
    key_unknowns: list[Any] = Field(default_factory=list)
    blind_spots: list[Any] = Field(default_factory=list)
    risks: list[Any] = Field(default_factory=list)
    relevant_lens_pack_ids: list[uuid.UUID] = Field(default_factory=list)
    recommendation_summary: str | None = None
    confidence: Decimal | None = None


class DecisionBriefRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    problem_id: uuid.UUID
    classification: str | None
    summary: str | None
    key_unknowns: list[Any]
    blind_spots: list[Any]
    risks: list[Any]
    relevant_lens_pack_ids: list[Any]
    recommendation_summary: str | None
    confidence: Decimal | None
    generated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Option Paths
# ---------------------------------------------------------------------------

class OptionPathCreate(BaseModel):
    decision_brief_id: uuid.UUID
    option_label: str
    description: str
    expected_upside: str | None = None
    expected_downside: str | None = None
    reversibility: str | None = None
    risk_score: Decimal | None = None
    recommendation_rank: int | None = None


class OptionPathRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    decision_brief_id: uuid.UUID
    option_label: str
    description: str
    expected_upside: str | None
    expected_downside: str | None
    reversibility: str | None
    risk_score: Decimal | None
    recommendation_rank: int | None
    created_at: datetime.datetime


# ---------------------------------------------------------------------------
# Contradiction Reports
# ---------------------------------------------------------------------------

class ContradictionReportCreate(BaseModel):
    operator_id: uuid.UUID
    problem_id: uuid.UUID | None = None
    contradiction_kind: str
    description: str
    evidence: list[Any] = Field(default_factory=list)
    severity: Decimal | None = None


class ContradictionReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    problem_id: uuid.UUID | None
    contradiction_kind: str
    description: str
    evidence: list[Any]
    severity: Decimal | None
    created_at: datetime.datetime
