"""FastAPI routes for the Execution layer.

These routes close Loop A: evidence -> inference -> policy -> outcome.
State estimates and blocker estimates record what the system infers.
Policy decisions record what move was selected. Traces record what happened.
Re-entry artifacts preserve continuity across interruptions.

Before the AI Fabric exists, all these objects can be created manually
or by deterministic rules. The typed persistence chain is what matters.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException

from utopia.api.deps import get_execution_service
from utopia.schemas.execution import (
    BlockerEstimateCreate,
    BlockerEstimateRead,
    PolicyDecisionCreate,
    PolicyDecisionRead,
    ReentryArtifactCreate,
    ReentryArtifactRead,
    StateEstimateCreate,
    StateEstimateRead,
    TraceCreate,
    TraceRead,
)
from utopia.services.execution_service import ExecutionService

router = APIRouter(prefix="/execution", tags=["execution"])


# ---------------------------------------------------------------------------
# State Estimates
# ---------------------------------------------------------------------------


@router.post("/state-estimates", response_model=StateEstimateRead, status_code=201)
async def record_state_estimate(
    body: StateEstimateCreate,
    svc: ExecutionService = Depends(get_execution_service),
) -> StateEstimateRead:
    estimate = await svc.record_state_estimate(body)
    await svc.commit()
    return StateEstimateRead.model_validate(estimate)


@router.get("/state-estimates/{estimate_id}", response_model=StateEstimateRead)
async def get_state_estimate(
    estimate_id: uuid.UUID,
    svc: ExecutionService = Depends(get_execution_service),
) -> StateEstimateRead:
    estimate = await svc.get_state_estimate(estimate_id)
    if estimate is None:
        raise HTTPException(status_code=404, detail="State estimate not found")
    return StateEstimateRead.model_validate(estimate)


# ---------------------------------------------------------------------------
# Blocker Estimates
# ---------------------------------------------------------------------------


@router.post("/blocker-estimates", response_model=BlockerEstimateRead, status_code=201)
async def record_blocker_estimate(
    body: BlockerEstimateCreate,
    svc: ExecutionService = Depends(get_execution_service),
) -> BlockerEstimateRead:
    estimate = await svc.record_blocker_estimate(body)
    await svc.commit()
    return BlockerEstimateRead.model_validate(estimate)


@router.get("/blocker-estimates/{estimate_id}", response_model=BlockerEstimateRead)
async def get_blocker_estimate(
    estimate_id: uuid.UUID,
    svc: ExecutionService = Depends(get_execution_service),
) -> BlockerEstimateRead:
    estimate = await svc.get_blocker_estimate(estimate_id)
    if estimate is None:
        raise HTTPException(status_code=404, detail="Blocker estimate not found")
    return BlockerEstimateRead.model_validate(estimate)


# ---------------------------------------------------------------------------
# Re-entry Artifacts
# ---------------------------------------------------------------------------


@router.post("/reentry-artifacts", response_model=ReentryArtifactRead, status_code=201)
async def create_reentry_artifact(
    body: ReentryArtifactCreate,
    svc: ExecutionService = Depends(get_execution_service),
) -> ReentryArtifactRead:
    artifact = await svc.create_reentry_artifact(body)
    await svc.commit()
    return ReentryArtifactRead.model_validate(artifact)


@router.get("/reentry-artifacts/{artifact_id}", response_model=ReentryArtifactRead)
async def get_reentry_artifact(
    artifact_id: uuid.UUID,
    svc: ExecutionService = Depends(get_execution_service),
) -> ReentryArtifactRead:
    artifact = await svc.get_reentry_artifact(artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Re-entry artifact not found")
    return ReentryArtifactRead.model_validate(artifact)


@router.get("/reentry-artifacts/current/{thread_id}", response_model=ReentryArtifactRead)
async def get_current_reentry_artifact(
    thread_id: uuid.UUID,
    svc: ExecutionService = Depends(get_execution_service),
) -> ReentryArtifactRead:
    artifact = await svc.get_current_reentry_artifact(thread_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="No active re-entry artifact for this thread")
    return ReentryArtifactRead.model_validate(artifact)


# ---------------------------------------------------------------------------
# Policy Decisions
# ---------------------------------------------------------------------------


@router.post("/policy-decisions", response_model=PolicyDecisionRead, status_code=201)
async def record_policy_decision(
    body: PolicyDecisionCreate,
    svc: ExecutionService = Depends(get_execution_service),
) -> PolicyDecisionRead:
    decision = await svc.record_policy_decision(body)
    await svc.commit()
    return PolicyDecisionRead.model_validate(decision)


@router.get("/policy-decisions/{decision_id}", response_model=PolicyDecisionRead)
async def get_policy_decision(
    decision_id: uuid.UUID,
    svc: ExecutionService = Depends(get_execution_service),
) -> PolicyDecisionRead:
    decision = await svc.get_policy_decision(decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="Policy decision not found")
    return PolicyDecisionRead.model_validate(decision)


# ---------------------------------------------------------------------------
# Traces
# ---------------------------------------------------------------------------


@router.post("/traces", response_model=TraceRead, status_code=201)
async def record_trace(
    body: TraceCreate,
    svc: ExecutionService = Depends(get_execution_service),
) -> TraceRead:
    trace = await svc.record_trace(body)
    await svc.commit()
    return TraceRead.model_validate(trace)


@router.get("/traces/{trace_id}", response_model=TraceRead)
async def get_trace(
    trace_id: uuid.UUID,
    svc: ExecutionService = Depends(get_execution_service),
) -> TraceRead:
    trace = await svc.get_trace(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found")
    return TraceRead.model_validate(trace)


@router.get("/traces", response_model=list[TraceRead])
async def list_traces(
    operator_id: uuid.UUID,
    thread_id: uuid.UUID | None = None,
    limit: int = 50,
    svc: ExecutionService = Depends(get_execution_service),
) -> list[TraceRead]:
    traces = await svc.list_traces(operator_id, thread_id=thread_id, limit=limit)
    return [TraceRead.model_validate(t) for t in traces]
