"""AI Fabric routes — assessment pipeline and reasoning modules."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from utopia.api.deps import get_evidence_service, get_execution_service
from utopia.services.evidence_service import EvidenceService
from utopia.services.execution_service import ExecutionService

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
