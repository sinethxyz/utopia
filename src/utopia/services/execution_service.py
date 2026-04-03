"""ExecutionService — bounded-context service for the action layer.

Closes Loop A: evidence -> inference -> policy -> outcome.

This service is persistence-first. It does not contain Schrödinger's
reasoning logic — that belongs in the AI Fabric. This service records
the typed outputs of that reasoning: state estimates, blocker estimates,
policy decisions, re-entry artifacts, and traces.

Before the AI Fabric exists, these objects can be created manually
or by deterministic rules. The chain is what matters.
"""

import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.models.execution import (
    BlockerEstimate,
    PolicyDecision,
    ReentryArtifact,
    StateEstimate,
    Trace,
)
from utopia.schemas.execution import (
    BlockerEstimateCreate,
    PolicyDecisionCreate,
    ReentryArtifactCreate,
    StateEstimateCreate,
    TraceCreate,
)


class ExecutionService:
    """Service for the Execution layer.

    Records the evidence -> inference -> policy -> outcome chain.
    Every policy decision should be traceable back through the chain.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # State Estimates
    # ------------------------------------------------------------------

    async def record_state_estimate(self, data: StateEstimateCreate) -> StateEstimate:
        """Record what operating condition the operator is in.

        Combines subjective, behavioral, contextual, and physiological
        evidence into a single typed state. This constrains all
        downstream policy selection.
        """
        estimate = StateEstimate(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            state_kind=data.state_kind,
            confidence=data.confidence,
            contributing_factors=data.contributing_factors,
        )
        self._session.add(estimate)
        await self._session.flush()
        return estimate

    async def get_state_estimate(self, estimate_id: _uuid.UUID) -> StateEstimate | None:
        return await self._session.get(StateEstimate, estimate_id)

    async def get_latest_state_estimate(
        self, operator_id: _uuid.UUID
    ) -> StateEstimate | None:
        """Return the most recent state estimate for the operator."""
        stmt = (
            select(StateEstimate)
            .where(StateEstimate.operator_id == operator_id)
            .order_by(StateEstimate.generated_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Blocker Estimates
    # ------------------------------------------------------------------

    async def record_blocker_estimate(self, data: BlockerEstimateCreate) -> BlockerEstimate:
        """Record why motion is failing.

        Each blocker kind implies a different intervention. Without
        blocker typing, the system recommends the wrong thing.
        """
        estimate = BlockerEstimate(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            blocker_kind=data.blocker_kind,
            confidence=data.confidence,
            supporting_evidence=data.supporting_evidence,
        )
        self._session.add(estimate)
        await self._session.flush()
        return estimate

    async def get_blocker_estimate(self, estimate_id: _uuid.UUID) -> BlockerEstimate | None:
        return await self._session.get(BlockerEstimate, estimate_id)

    async def get_latest_blocker_estimate(
        self, operator_id: _uuid.UUID
    ) -> BlockerEstimate | None:
        stmt = (
            select(BlockerEstimate)
            .where(BlockerEstimate.operator_id == operator_id)
            .order_by(BlockerEstimate.generated_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Re-entry Artifacts
    # ------------------------------------------------------------------

    async def create_reentry_artifact(self, data: ReentryArtifactCreate) -> ReentryArtifact:
        """Create a re-entry artifact for a thread.

        One of the most valuable objects in the system. Reduces the
        tax of interruption by preserving: last completed step,
        unresolved edge, smallest next move, trap to avoid.
        """
        artifact = ReentryArtifact(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            last_completed_step=data.last_completed_step,
            unresolved_edge=data.unresolved_edge,
            next_smallest_move=data.next_smallest_move,
            trap_to_avoid=data.trap_to_avoid,
            relevant_context=data.relevant_context,
            freshness_score=data.freshness_score,
        )
        self._session.add(artifact)
        await self._session.flush()
        return artifact

    async def get_reentry_artifact(self, artifact_id: _uuid.UUID) -> ReentryArtifact | None:
        return await self._session.get(ReentryArtifact, artifact_id)

    async def get_current_reentry_artifact(
        self, thread_id: _uuid.UUID
    ) -> ReentryArtifact | None:
        """Return the most recent non-superseded re-entry artifact for a thread."""
        stmt = (
            select(ReentryArtifact)
            .where(ReentryArtifact.thread_id == thread_id)
            .where(ReentryArtifact.superseded_by.is_(None))
            .order_by(ReentryArtifact.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def supersede_reentry_artifact(
        self,
        old_artifact_id: _uuid.UUID,
        new_data: ReentryArtifactCreate,
    ) -> ReentryArtifact:
        """Create a new re-entry artifact and mark the old one as superseded.

        This preserves the history of re-entry artifacts for a thread
        while keeping only the latest one active.
        """
        new_artifact = await self.create_reentry_artifact(new_data)
        old = await self._session.get(ReentryArtifact, old_artifact_id)
        if old is not None:
            old.superseded_by = new_artifact.id
        return new_artifact

    # ------------------------------------------------------------------
    # Policy Decisions
    # ------------------------------------------------------------------

    async def record_policy_decision(self, data: PolicyDecisionCreate) -> PolicyDecision:
        """Record a Schrödinger output — the smallest correct move.

        Links to the state estimate and blocker estimate that produced it,
        preserving the evidence -> inference -> policy chain. Before the
        AI Fabric exists, this can be created manually or by deterministic rules.
        """
        decision = PolicyDecision(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            problem_id=data.problem_id,
            state_estimate_id=data.state_estimate_id,
            blocker_estimate_id=data.blocker_estimate_id,
            mode=data.mode,
            intervention_kind=data.intervention_kind,
            action_depth=data.action_depth,
            next_move=data.next_move,
            rationale=data.rationale,
            confidence=data.confidence,
            caution_flags=data.caution_flags,
        )
        self._session.add(decision)
        await self._session.flush()
        return decision

    async def get_policy_decision(self, decision_id: _uuid.UUID) -> PolicyDecision | None:
        return await self._session.get(PolicyDecision, decision_id)

    async def get_latest_policy_decision(
        self, operator_id: _uuid.UUID
    ) -> PolicyDecision | None:
        stmt = (
            select(PolicyDecision)
            .where(PolicyDecision.operator_id == operator_id)
            .order_by(PolicyDecision.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Traces
    # ------------------------------------------------------------------

    async def record_trace(self, data: TraceCreate) -> Trace:
        """Record a compressed post-action trace.

        Not a diary. Training data for Aether and the Personal Execution
        Model. Completes the chain: evidence -> inference -> policy -> outcome.
        """
        trace = Trace(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            policy_decision_id=data.policy_decision_id,
            trace_kind=data.trace_kind,
            action_taken=data.action_taken,
            outcome=data.outcome,
            truth_revealed=data.truth_revealed,
            next_edge=data.next_edge,
            completion_score=data.completion_score,
            subjective_after=data.subjective_after,
        )
        self._session.add(trace)
        await self._session.flush()
        return trace

    async def get_trace(self, trace_id: _uuid.UUID) -> Trace | None:
        return await self._session.get(Trace, trace_id)

    async def list_traces(
        self,
        operator_id: _uuid.UUID,
        thread_id: _uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[Trace]:
        """Return recent traces, newest first."""
        stmt = select(Trace).where(Trace.operator_id == operator_id)
        if thread_id is not None:
            stmt = stmt.where(Trace.thread_id == thread_id)
        stmt = stmt.order_by(Trace.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
