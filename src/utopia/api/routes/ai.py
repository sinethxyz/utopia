"""AI Fabric routes — assessment pipeline and reasoning modules."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from utopia.api.deps import (
    get_evidence_service,
    get_execution_service,
    get_reasoning_service,
    get_vector_search_service,
)
from utopia.services.evidence_service import EvidenceService
from utopia.services.execution_service import ExecutionService
from utopia.services.reasoning_service import ReasoningService
from utopia.services.vector_search_service import VectorSearchService

router = APIRouter(prefix="/ai", tags=["ai"])


# ---------------------------------------------------------------------------
# Assessment pipeline
# ---------------------------------------------------------------------------

class AssessmentRequest(BaseModel):
    operator_id: uuid.UUID
    thread_id: uuid.UUID | None = None


class AssessmentResponse(BaseModel):
    state_estimate: dict[str, Any]
    state_estimate_id: uuid.UUID | None
    blocker_estimate: dict[str, Any]
    blocker_estimate_id: uuid.UUID | None
    policy_decision: dict[str, Any]
    policy_decision_id: uuid.UUID | None
    evidence_summary: dict[str, Any]
    model_usage: list[dict[str, Any]]


@router.post("/assess", response_model=AssessmentResponse, status_code=200)
async def run_assessment(
    data: AssessmentRequest,
    evidence_svc: EvidenceService = Depends(get_evidence_service),
    execution_svc: ExecutionService = Depends(get_execution_service),
) -> AssessmentResponse:
    """Run the full AI Fabric assessment pipeline.

    Gathers current evidence, runs the State Estimator, Blocker Classifier,
    and Policy Selector in sequence, persists all outputs, and returns
    the complete assessment with the recommended next move.
    """
    from utopia.ai.assess import run_assessment as _run

    result = await _run(
        evidence_svc,
        execution_svc,
        data.operator_id,
        thread_id=data.thread_id,
    )

    return AssessmentResponse(
        state_estimate=result.state_estimate,
        state_estimate_id=result.state_estimate_id,
        blocker_estimate=result.blocker_estimate,
        blocker_estimate_id=result.blocker_estimate_id,
        policy_decision=result.policy_decision,
        policy_decision_id=result.policy_decision_id,
        evidence_summary=result.evidence_summary,
        model_usage=result.model_usage,
    )


# ---------------------------------------------------------------------------
# Router — intent classification
# ---------------------------------------------------------------------------

class RouterRequest(BaseModel):
    operator_id: uuid.UUID
    message: str
    recent_state: dict[str, Any] | None = None


class RouterResponse(BaseModel):
    intent: str
    confidence: float
    extracted_context: dict[str, Any]
    reasoning: str
    model_usage: dict[str, Any]


@router.post("/route", response_model=RouterResponse, status_code=200)
async def classify_intent(data: RouterRequest) -> RouterResponse:
    """Classify the operator's intent to dispatch to the correct pipeline."""
    from utopia.ai.router import classify_intent as _classify

    classification, usage = await _classify(
        data.operator_id,
        data.message,
        recent_state=data.recent_state,
    )

    return RouterResponse(
        intent=classification["intent"],
        confidence=classification["confidence"],
        extracted_context=classification["extracted_context"],
        reasoning=classification["reasoning"],
        model_usage=usage,
    )


# ---------------------------------------------------------------------------
# Problem Structurer
# ---------------------------------------------------------------------------

class StructureRequest(BaseModel):
    problem_id: uuid.UUID
    raw_prompt: str
    operator_state: dict[str, Any] | None = None
    thread_context: str | None = None


class StructureResponse(BaseModel):
    problem_id: uuid.UUID
    structure: dict[str, Any]
    model_usage: dict[str, Any]


@router.post("/structure-problem", response_model=StructureResponse, status_code=200)
async def structure_problem(
    data: StructureRequest,
    reasoning_svc: ReasoningService = Depends(get_reasoning_service),
) -> StructureResponse:
    """Decompose a raw problem into a structured analysis and persist it."""
    from utopia.ai.problem_structurer import structure_problem as _structure

    create, usage = await _structure(
        data.problem_id,
        data.raw_prompt,
        operator_state=data.operator_state,
        thread_context=data.thread_context,
    )

    structure = await reasoning_svc.create_problem_structure(create)
    await reasoning_svc.commit()

    return StructureResponse(
        problem_id=data.problem_id,
        structure={
            "id": str(structure.id),
            "objective": create.objective,
            "stakes": create.stakes,
            "actors": create.actors,
            "constraints": create.constraints,
            "assumptions": create.assumptions,
            "unknowns": create.unknowns,
            "irreversibilities": create.irreversibilities,
            "bottlenecks": create.bottlenecks,
            "observable_facts": create.observable_facts,
            "narrative_layer": create.narrative_layer,
            "distortion_candidates": create.distortion_candidates,
            "confidence": str(create.confidence) if create.confidence else None,
        },
        model_usage=usage,
    )


# ---------------------------------------------------------------------------
# Context Retriever
# ---------------------------------------------------------------------------

class RetrieveRequest(BaseModel):
    query: str
    operator_id: uuid.UUID | None = None
    entity_kinds: list[str] | None = None
    top_k: int = 10
    synthesize: bool = True


class RetrieveResponse(BaseModel):
    relevant_knowledge: list[dict[str, Any]]
    synthesis: str
    contradictions: list[str]
    knowledge_gaps: list[str]
    confidence: float
    raw_results_count: int
    model_usage: dict[str, Any]


@router.post("/retrieve", response_model=RetrieveResponse, status_code=200)
async def retrieve_context(
    data: RetrieveRequest,
    vector_search_svc: VectorSearchService = Depends(get_vector_search_service),
) -> RetrieveResponse:
    """Retrieve and synthesize relevant knowledge from Aether."""
    from utopia.ai.context_retriever import retrieve_context as _retrieve

    result = await _retrieve(
        vector_search_svc,
        data.query,
        operator_id=data.operator_id,
        entity_kinds=data.entity_kinds,
        top_k=data.top_k,
        synthesize=data.synthesize,
    )

    return RetrieveResponse(
        relevant_knowledge=result.relevant_knowledge,
        synthesis=result.synthesis,
        contradictions=result.contradictions,
        knowledge_gaps=result.knowledge_gaps,
        confidence=result.confidence,
        raw_results_count=result.raw_results_count,
        model_usage=result.model_usage,
    )


# ---------------------------------------------------------------------------
# Physiology Interpreter
# ---------------------------------------------------------------------------

class PhysiologyInterpretRequest(BaseModel):
    operator_id: uuid.UUID
    physiology_data: dict[str, Any]
    recent_trends: dict[str, Any] | None = None


class PhysiologyInterpretResponse(BaseModel):
    capacity_level: str
    capacity_score: int
    key_signals: list[dict[str, Any]]
    action_depth_ceiling: str
    recovery_trajectory: str
    warnings: list[str]
    recommendation: str
    confidence: float
    model_usage: dict[str, Any]


@router.post(
    "/interpret-physiology",
    response_model=PhysiologyInterpretResponse,
    status_code=200,
)
async def interpret_physiology(data: PhysiologyInterpretRequest) -> PhysiologyInterpretResponse:
    """Interpret raw physiological data into capacity signals."""
    from utopia.ai.physiology_interpreter import interpret_physiology as _interpret

    interpretation, usage = await _interpret(
        data.operator_id,
        data.physiology_data,
        recent_trends=data.recent_trends,
    )

    return PhysiologyInterpretResponse(
        capacity_level=interpretation.capacity_level,
        capacity_score=interpretation.capacity_score,
        key_signals=interpretation.key_signals,
        action_depth_ceiling=interpretation.action_depth_ceiling,
        recovery_trajectory=interpretation.recovery_trajectory,
        warnings=interpretation.warnings,
        recommendation=interpretation.recommendation,
        confidence=interpretation.confidence,
        model_usage=usage,
    )


# ---------------------------------------------------------------------------
# Contradiction Checker
# ---------------------------------------------------------------------------

class ContradictionRequest(BaseModel):
    operator_id: uuid.UUID
    operator_claims: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    state_estimate: dict[str, Any] | None = None
    physiology: dict[str, Any] | None = None
    recent_behavior: list[dict[str, Any]] | None = None
    problem_id: uuid.UUID | None = None


class ContradictionResponse(BaseModel):
    contradictions: list[dict[str, Any]]
    model_usage: dict[str, Any]


@router.post(
    "/check-contradictions",
    response_model=ContradictionResponse,
    status_code=200,
)
async def check_contradictions(
    data: ContradictionRequest,
    reasoning_svc: ReasoningService = Depends(get_reasoning_service),
) -> ContradictionResponse:
    """Check for contradictions between operator narrative and evidence."""
    from utopia.ai.contradiction_checker import check_contradictions as _check

    reports, usage = await _check(
        data.operator_id,
        operator_claims=data.operator_claims,
        evidence=data.evidence,
        state_estimate=data.state_estimate,
        physiology=data.physiology,
        recent_behavior=data.recent_behavior,
        problem_id=data.problem_id,
    )

    # Persist contradiction reports
    persisted = []
    for report_create in reports:
        report = await reasoning_svc.record_contradiction(report_create)
        persisted.append({
            "id": str(report.id),
            "contradiction_kind": report_create.contradiction_kind,
            "description": report_create.description,
            "severity": str(report_create.severity) if report_create.severity else None,
        })
    if reports:
        await reasoning_svc.commit()

    return ContradictionResponse(contradictions=persisted, model_usage=usage)


# ---------------------------------------------------------------------------
# Council — multi-perspective deliberation
# ---------------------------------------------------------------------------

class CouncilRequest(BaseModel):
    problem_description: str
    problem_structure: dict[str, Any] | None = None
    operator_state: dict[str, Any] | None = None
    physiology: dict[str, Any] | None = None
    relevant_knowledge: list[dict[str, Any]] | None = None


class CouncilResponse(BaseModel):
    perspectives: list[dict[str, Any]]
    consensus_points: list[str]
    tension_points: list[dict[str, Any]]
    dominant_perspective: str
    synthesis: str
    decision_readiness: str
    confidence: float
    model_usage: list[dict[str, Any]]


@router.post("/deliberate", response_model=CouncilResponse, status_code=200)
async def run_council(data: CouncilRequest) -> CouncilResponse:
    """Run multi-perspective deliberation on a problem."""
    from utopia.ai.council import deliberate as _deliberate

    result = await _deliberate(
        data.problem_description,
        problem_structure=data.problem_structure,
        operator_state=data.operator_state,
        physiology=data.physiology,
        relevant_knowledge=data.relevant_knowledge,
    )

    return CouncilResponse(
        perspectives=result.perspectives,
        consensus_points=result.consensus_points,
        tension_points=result.tension_points,
        dominant_perspective=result.dominant_perspective,
        synthesis=result.synthesis,
        decision_readiness=result.decision_readiness,
        confidence=result.confidence,
        model_usage=result.model_usage,
    )
