"""Service layer unit tests.

Tests the service classes that form the persistence layer for each
bounded context. Each test operates within a rolled-back transaction
for isolation.

These tests require a running PostgreSQL database with the Utopia
schema (run alembic upgrade head first).
"""

from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

import pytest
from uuid_utils import uuid7

from utopia.enums import (
    ActionDepth,
    BlockerKind,
    InterventionKind,
    StateKind,
    TraceKind,
)
from utopia.models.core import Operator
from utopia.schemas.evidence import (
    BehaviorEventCreate,
    ContextSnapshotCreate,
    DerivedFeatureCreate,
    SubjectiveCheckinCreate,
)
from utopia.schemas.execution import (
    BlockerEstimateCreate,
    PolicyDecisionCreate,
    ReentryArtifactCreate,
    StateEstimateCreate,
    TraceCreate,
)
from utopia.schemas.reasoning import (
    ContradictionReportCreate,
    ProblemCreate,
    ProblemStructureCreate,
)


# ---------------------------------------------------------------------------
# Helper: insert a test operator
# ---------------------------------------------------------------------------

async def _insert_operator(db_session, operator_id: uuid.UUID) -> Operator:
    """Insert a minimal operator row for FK satisfaction."""
    op = Operator(
        id=operator_id,
        display_name="Test Operator",
        timezone="UTC",
    )
    db_session.add(op)
    await db_session.flush()
    return op


# ---------------------------------------------------------------------------
# Evidence Service
# ---------------------------------------------------------------------------

class TestEvidenceService:
    """Tests for the Evidence sensing layer service."""

    @pytest.mark.asyncio
    async def test_record_and_list_checkins(self, db_session, evidence_service, operator_id):
        await _insert_operator(db_session, operator_id)

        checkin = await evidence_service.record_checkin(
            SubjectiveCheckinCreate(
                operator_id=operator_id,
                energy=40,
                clarity=60,
                resistance=70,
                free_text="Feeling stuck but alert",
            )
        )

        assert checkin.id is not None
        assert checkin.energy == 40
        assert checkin.clarity == 60

        checkins = await evidence_service.list_checkins(operator_id)
        assert len(checkins) >= 1
        assert checkins[0].id == checkin.id

    @pytest.mark.asyncio
    async def test_record_behavior_event(self, db_session, evidence_service, operator_id):
        await _insert_operator(db_session, operator_id)

        event = await evidence_service.record_behavior_event(
            BehaviorEventCreate(
                operator_id=operator_id,
                event_type="failed_start",
                event_at=datetime.datetime.now(tz=datetime.timezone.utc),
                duration_ms=5000,
            )
        )

        assert event.id is not None
        assert event.event_type == "failed_start"

        events = await evidence_service.list_behavior_events(operator_id)
        assert len(events) >= 1

    @pytest.mark.asyncio
    async def test_record_context_snapshot(self, db_session, evidence_service, operator_id):
        await _insert_operator(db_session, operator_id)

        snapshot = await evidence_service.record_context_snapshot(
            ContextSnapshotCreate(
                operator_id=operator_id,
                local_time=datetime.datetime.now(tz=datetime.timezone.utc),
                environment_label="home_office",
                interruption_count=3,
                available_minutes=45,
            )
        )

        assert snapshot.id is not None
        assert snapshot.environment_label == "home_office"

        latest = await evidence_service.get_latest_context(operator_id)
        assert latest is not None
        assert latest.id == snapshot.id

    @pytest.mark.asyncio
    async def test_store_derived_feature(self, db_session, evidence_service, operator_id):
        await _insert_operator(db_session, operator_id)

        feature = await evidence_service.store_derived_feature(
            DerivedFeatureCreate(
                operator_id=operator_id,
                feature_name="failed_start_rate_24h",
                feature_value=Decimal("0.35"),
                feature_window="24h",
                confidence=Decimal("0.85"),
            )
        )

        assert feature.id is not None
        assert feature.feature_name == "failed_start_rate_24h"


# ---------------------------------------------------------------------------
# Execution Service
# ---------------------------------------------------------------------------

class TestExecutionService:
    """Tests for the Execution layer service."""

    @pytest.mark.asyncio
    async def test_record_state_estimate(self, db_session, execution_service, operator_id):
        await _insert_operator(db_session, operator_id)

        estimate = await execution_service.record_state_estimate(
            StateEstimateCreate(
                operator_id=operator_id,
                state_kind=StateKind.execute,
                confidence=Decimal("0.82"),
                contributing_factors=[
                    {"source": "checkin", "signal": "energy", "value": "70"}
                ],
            )
        )

        assert estimate.id is not None
        assert estimate.state_kind == StateKind.execute

        latest = await execution_service.get_latest_state_estimate(operator_id)
        assert latest is not None
        assert latest.id == estimate.id

    @pytest.mark.asyncio
    async def test_record_blocker_estimate(self, db_session, execution_service, operator_id):
        await _insert_operator(db_session, operator_id)

        estimate = await execution_service.record_blocker_estimate(
            BlockerEstimateCreate(
                operator_id=operator_id,
                blocker_kind=BlockerKind.ambiguity,
                confidence=Decimal("0.75"),
                supporting_evidence=[
                    {"source": "behavior", "signal": "failed_starts", "value": "3"}
                ],
            )
        )

        assert estimate.id is not None
        assert estimate.blocker_kind == BlockerKind.ambiguity

    @pytest.mark.asyncio
    async def test_record_policy_decision(self, db_session, execution_service, operator_id):
        await _insert_operator(db_session, operator_id)

        decision = await execution_service.record_policy_decision(
            PolicyDecisionCreate(
                operator_id=operator_id,
                mode=InterventionKind.clarify,
                intervention_kind=InterventionKind.clarify,
                action_depth=ActionDepth.narrow,
                next_move="Write the first test case name for the auth module",
                rationale="Ambiguity is the blocker — shrink the problem.",
            )
        )

        assert decision.id is not None
        assert decision.intervention_kind == InterventionKind.clarify
        assert decision.action_depth == ActionDepth.narrow

    @pytest.mark.asyncio
    async def test_record_trace(self, db_session, execution_service, operator_id):
        await _insert_operator(db_session, operator_id)

        trace = await execution_service.record_trace(
            TraceCreate(
                operator_id=operator_id,
                trace_kind=TraceKind.action,
                action_taken="Wrote the first test case name",
                outcome="Unblocked — realized the scope was smaller than feared",
                truth_revealed="The auth module only needs 3 test cases, not 15",
                completion_score=Decimal("0.60"),
            )
        )

        assert trace.id is not None
        assert trace.trace_kind == TraceKind.action

        traces = await execution_service.list_traces(operator_id)
        assert len(traces) >= 1

    @pytest.mark.asyncio
    async def test_reentry_artifact_lifecycle(self, db_session, execution_service, operator_id):
        await _insert_operator(db_session, operator_id)

        # Need a thread for reentry artifacts — create via vector_ctrl
        from utopia.enums import MissionKind, Status, ThreadKind, ThreadStatus
        from utopia.models.vector_ctrl import Mission, Thread

        mission = Mission(
            id=uuid7(), operator_id=operator_id, title="Test Mission",
            mission_kind=MissionKind.technical, status=Status.active,
        )
        db_session.add(mission)
        await db_session.flush()

        thread = Thread(
            id=uuid7(), operator_id=operator_id, mission_id=mission.id,
            title="Test Thread", thread_kind=ThreadKind.build, status=ThreadStatus.active,
        )
        db_session.add(thread)
        await db_session.flush()

        artifact = await execution_service.create_reentry_artifact(
            ReentryArtifactCreate(
                operator_id=operator_id,
                thread_id=thread.id,
                last_completed_step="Defined the API schema",
                unresolved_edge="Need to decide on auth strategy",
                next_smallest_move="List the 3 auth options in a comment",
                trap_to_avoid="Don't start implementing before choosing",
            )
        )

        assert artifact.id is not None

        current = await execution_service.get_current_reentry_artifact(thread.id)
        assert current is not None
        assert current.id == artifact.id

        # Supersede it
        new_artifact = await execution_service.supersede_reentry_artifact(
            artifact.id,
            ReentryArtifactCreate(
                operator_id=operator_id,
                thread_id=thread.id,
                last_completed_step="Chose JWT auth",
                next_smallest_move="Write the token validation middleware",
            ),
        )

        assert new_artifact.id != artifact.id
        current = await execution_service.get_current_reentry_artifact(thread.id)
        assert current.id == new_artifact.id


# ---------------------------------------------------------------------------
# Reasoning Service
# ---------------------------------------------------------------------------

class TestReasoningService:
    """Tests for the Reasoning layer service."""

    @pytest.mark.asyncio
    async def test_problem_lifecycle(self, db_session, reasoning_service, operator_id):
        await _insert_operator(db_session, operator_id)

        problem = await reasoning_service.create_problem(
            ProblemCreate(
                operator_id=operator_id,
                title="Should I switch to Rust for the backend?",
                raw_prompt="I keep hearing Rust is better for performance...",
                problem_kind="technical",
            )
        )

        assert problem.id is not None
        assert problem.title == "Should I switch to Rust for the backend?"

        # Create structure
        structure = await reasoning_service.create_problem_structure(
            ProblemStructureCreate(
                problem_id=problem.id,
                objective="Determine if Rust migration improves system reliability",
                stakes="6 months of rebuild time if wrong",
                assumptions=["Current Python performance is the bottleneck"],
                unknowns=["Actual latency requirements at scale"],
                confidence=Decimal("0.70"),
            )
        )

        assert structure.id is not None
        assert structure.objective is not None

        fetched = await reasoning_service.get_problem_structure(problem.id)
        assert fetched is not None

    @pytest.mark.asyncio
    async def test_contradiction_report(self, db_session, reasoning_service, operator_id):
        await _insert_operator(db_session, operator_id)

        report = await reasoning_service.record_contradiction(
            ContradictionReportCreate(
                operator_id=operator_id,
                contradiction_kind="narrative_vs_behavior",
                description="Claims to be productive but 5 failed starts today",
                evidence=[
                    {"source": "behavior", "claim": "productive", "reality": "5 failed starts"}
                ],
                severity=Decimal("0.7"),
            )
        )

        assert report.id is not None

        reports = await reasoning_service.list_contradictions(operator_id)
        assert len(reports) >= 1
