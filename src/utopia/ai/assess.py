"""Assessment orchestrator — runs the full AI Fabric pipeline.

Gathers evidence from services, runs the three AI modules in sequence
(state estimator -> blocker classifier -> policy selector), persists
all outputs, and returns the complete assessment.

This is the main entry point for the AI Fabric.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from utopia.ai import blocker_classifier, policy_selector, state_estimator
from utopia.schemas.execution import (
    BlockerEstimateCreate,
    PolicyDecisionCreate,
    StateEstimateCreate,
)
from utopia.services.evidence_service import EvidenceService
from utopia.services.execution_service import ExecutionService

logger = logging.getLogger(__name__)


@dataclass
class AssessmentResult:
    """Complete output of the AI Fabric assessment pipeline."""

    state_estimate: dict = field(default_factory=dict)
    state_estimate_id: uuid.UUID | None = None
    blocker_estimate: dict = field(default_factory=dict)
    blocker_estimate_id: uuid.UUID | None = None
    policy_decision: dict = field(default_factory=dict)
    policy_decision_id: uuid.UUID | None = None
    evidence_summary: dict = field(default_factory=dict)
    model_usage: list[dict] = field(default_factory=list)


async def gather_evidence(
    evidence_svc: EvidenceService,
    operator_id: uuid.UUID,
    thread_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    """Gather current evidence from all available sources.

    Returns a dict suitable for passing to the AI modules.
    """
    evidence: dict[str, Any] = {}

    # Latest subjective checkin
    checkins = await evidence_svc.list_checkins(operator_id, thread_id=thread_id, limit=1)
    if checkins:
        c = checkins[0]
        evidence["checkin"] = {
            "energy": c.energy,
            "clarity": c.clarity,
            "resistance": c.resistance,
            "overwhelm": c.overwhelm,
            "emotional_load": c.emotional_load,
            "perceived_urgency": c.perceived_urgency,
            "free_text": c.free_text,
            "recorded_at": str(c.recorded_at),
        }

    # Recent behavior events
    events = await evidence_svc.list_behavior_events(
        operator_id, thread_id=thread_id, limit=10
    )
    if events:
        evidence["behavior_events"] = [
            {
                "event_type": e.event_type,
                "event_at": str(e.event_at),
                "duration_ms": e.duration_ms,
            }
            for e in events
        ]

    # Latest context snapshot
    context = await evidence_svc.get_latest_context(operator_id)
    if context:
        evidence["context"] = {
            "local_time": str(context.local_time),
            "environment_label": context.environment_label,
            "interruption_count": context.interruption_count,
            "obligation_load": context.obligation_load,
            "available_minutes": context.available_minutes,
            "active_window": context.active_window,
        }

    # Latest derived features
    features = await evidence_svc.get_latest_features(operator_id, limit=10)
    if features:
        evidence["derived_features"] = [
            {
                "feature_name": f.feature_name,
                "feature_value": str(f.feature_value) if f.feature_value else None,
                "feature_window": f.feature_window,
                "confidence": str(f.confidence) if f.confidence else None,
            }
            for f in features
        ]

    return evidence


async def run_assessment(
    evidence_svc: EvidenceService,
    execution_svc: ExecutionService,
    operator_id: uuid.UUID,
    *,
    thread_id: uuid.UUID | None = None,
) -> AssessmentResult:
    """Run the full AI Fabric assessment pipeline.

    1. Gather evidence
    2. State Estimator -> produces StateEstimate
    3. Blocker Classifier -> produces BlockerEstimate
    4. Policy Selector -> produces PolicyDecision
    5. Persist all outputs
    6. Return complete result

    Args:
        evidence_svc: EvidenceService for querying current evidence.
        execution_svc: ExecutionService for persisting outputs.
        operator_id: The operator to assess.
        thread_id: Optional thread context.

    Returns:
        AssessmentResult with all outputs and usage metadata.
    """
    result = AssessmentResult()

    # 1. Gather evidence
    evidence = await gather_evidence(evidence_svc, operator_id, thread_id)
    result.evidence_summary = evidence

    # 2. State Estimator
    state_create, state_usage = await state_estimator.estimate_state(
        operator_id, evidence, thread_id=thread_id
    )
    result.model_usage.append({"module": "state_estimator", **state_usage})

    state_obj = await execution_svc.record_state_estimate(state_create)

    result.state_estimate = {
        "state_kind": state_create.state_kind.value,
        "confidence": str(state_create.confidence),
        "contributing_factors": state_create.contributing_factors,
    }
    result.state_estimate_id = state_obj.id

    # 3. Blocker Classifier
    blocker_create, blocker_usage = await blocker_classifier.classify_blocker(
        operator_id,
        evidence,
        result.state_estimate,
        thread_id=thread_id,
    )
    result.model_usage.append({"module": "blocker_classifier", **blocker_usage})

    blocker_obj = await execution_svc.record_blocker_estimate(blocker_create)

    result.blocker_estimate = {
        "blocker_kind": blocker_create.blocker_kind.value,
        "confidence": str(blocker_create.confidence),
        "supporting_evidence": blocker_create.supporting_evidence,
    }
    result.blocker_estimate_id = blocker_obj.id

    # 4. Policy Selector
    policy_create, policy_usage = await policy_selector.select_policy(
        operator_id,
        evidence,
        result.state_estimate,
        result.blocker_estimate,
        thread_id=thread_id,
        state_estimate_id=state_obj.id,
        blocker_estimate_id=blocker_obj.id,
    )
    result.model_usage.append({"module": "policy_selector", **policy_usage})

    policy_obj = await execution_svc.record_policy_decision(policy_create)

    result.policy_decision = {
        "intervention_kind": policy_create.intervention_kind.value,
        "action_depth": policy_create.action_depth.value,
        "next_move": policy_create.next_move,
        "rationale": policy_create.rationale,
        "confidence": str(policy_create.confidence) if policy_create.confidence else None,
        "caution_flags": policy_create.caution_flags,
    }
    result.policy_decision_id = policy_obj.id

    # 5. Commit all
    await execution_svc.commit()

    logger.info(
        "Assessment complete: state=%s blocker=%s intervention=%s next_move=%s",
        result.state_estimate["state_kind"],
        result.blocker_estimate["blocker_kind"],
        result.policy_decision["intervention_kind"],
        result.policy_decision["next_move"][:60],
    )

    return result
