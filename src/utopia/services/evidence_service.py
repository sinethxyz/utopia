"""EvidenceService — bounded-context service for the live sensing layer.

Evidence is append-mostly: checkins, behavior events, and context
snapshots flow in. Derived features are computed and stored. The
service does not interpret evidence — that is the AI Fabric's job
(State Estimator, Blocker Classifier). This service captures truth.
"""

import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.models.evidence import (
    BehaviorEvent,
    ContextSnapshot,
    DerivedFeature,
    SubjectiveCheckin,
)
from utopia.schemas.evidence import (
    BehaviorEventCreate,
    ContextSnapshotCreate,
    DerivedFeatureCreate,
    SubjectiveCheckinCreate,
)


class EvidenceService:
    """Service for the Evidence sensing layer.

    Captures subjective, behavioral, and contextual evidence.
    All evidence is append-only or append-mostly.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # Subjective Checkins
    # ------------------------------------------------------------------

    async def record_checkin(self, data: SubjectiveCheckinCreate) -> SubjectiveCheckin:
        """Record a subjective self-report of the operator's internal state.

        Partial checkins are valid. Even a single signal (e.g. energy=30)
        is meaningful evidence for the State Estimator.
        """
        checkin = SubjectiveCheckin(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            energy=data.energy,
            clarity=data.clarity,
            resistance=data.resistance,
            overwhelm=data.overwhelm,
            emotional_load=data.emotional_load,
            perceived_urgency=data.perceived_urgency,
            free_text=data.free_text,
            recorded_at=data.recorded_at,
        )
        self._session.add(checkin)
        await self._session.flush()
        return checkin

    async def get_checkin(self, checkin_id: _uuid.UUID) -> SubjectiveCheckin | None:
        return await self._session.get(SubjectiveCheckin, checkin_id)

    async def list_checkins(
        self,
        operator_id: _uuid.UUID,
        thread_id: _uuid.UUID | None = None,
        limit: int = 20,
    ) -> list[SubjectiveCheckin]:
        """Return recent checkins, newest first."""
        stmt = (
            select(SubjectiveCheckin)
            .where(SubjectiveCheckin.operator_id == operator_id)
        )
        if thread_id is not None:
            stmt = stmt.where(SubjectiveCheckin.thread_id == thread_id)
        stmt = stmt.order_by(SubjectiveCheckin.recorded_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Behavior Events
    # ------------------------------------------------------------------

    async def record_behavior_event(self, data: BehaviorEventCreate) -> BehaviorEvent:
        """Record an observed behavioral signal.

        Behavior events are the raw material for pattern detection:
        failed starts, switching frequency, thread neglect, completion
        aversion. The Blocker Classifier consumes these.
        """
        event = BehaviorEvent(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            event_type=data.event_type,
            event_at=data.event_at,
            duration_ms=data.duration_ms,
            metadata_=data.metadata,
        )
        self._session.add(event)
        await self._session.flush()
        return event

    async def list_behavior_events(
        self,
        operator_id: _uuid.UUID,
        thread_id: _uuid.UUID | None = None,
        event_type: str | None = None,
        limit: int = 50,
    ) -> list[BehaviorEvent]:
        """Return recent behavior events, newest first."""
        stmt = (
            select(BehaviorEvent)
            .where(BehaviorEvent.operator_id == operator_id)
        )
        if thread_id is not None:
            stmt = stmt.where(BehaviorEvent.thread_id == thread_id)
        if event_type is not None:
            stmt = stmt.where(BehaviorEvent.event_type == event_type)
        stmt = stmt.order_by(BehaviorEvent.event_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Context Snapshots
    # ------------------------------------------------------------------

    async def record_context_snapshot(self, data: ContextSnapshotCreate) -> ContextSnapshot:
        """Capture structural facts about the operator's environment.

        Environment label, interruption count, obligation load,
        available minutes, and active window give the State Estimator
        the context it needs to weight feasibility of action depth.
        """
        snapshot = ContextSnapshot(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            local_time=data.local_time,
            environment_label=data.environment_label,
            interruption_count=data.interruption_count,
            obligation_load=data.obligation_load,
            available_minutes=data.available_minutes,
            active_window=data.active_window,
            metadata_=data.metadata,
        )
        self._session.add(snapshot)
        await self._session.flush()
        return snapshot

    async def get_latest_context(
        self, operator_id: _uuid.UUID
    ) -> ContextSnapshot | None:
        """Return the most recent context snapshot for the operator."""
        stmt = (
            select(ContextSnapshot)
            .where(ContextSnapshot.operator_id == operator_id)
            .order_by(ContextSnapshot.local_time.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Derived Features
    # ------------------------------------------------------------------

    async def store_derived_feature(self, data: DerivedFeatureCreate) -> DerivedFeature:
        """Store a computed feature derived from raw evidence.

        Derived features are the bridge between raw evidence and
        policy-relevant signals. Examples: failed_start_rate_24h,
        thread_decay_hours, drift_probability, completion_aversion_score.
        """
        feature = DerivedFeature(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            feature_name=data.feature_name,
            feature_value=data.feature_value,
            feature_json=data.feature_json,
            feature_window=data.feature_window,
            confidence=data.confidence,
            observed_at=data.observed_at,
        )
        self._session.add(feature)
        await self._session.flush()
        return feature

    async def get_latest_features(
        self,
        operator_id: _uuid.UUID,
        feature_names: list[str] | None = None,
        limit: int = 50,
    ) -> list[DerivedFeature]:
        """Return latest derived features, optionally filtered by name."""
        stmt = (
            select(DerivedFeature)
            .where(DerivedFeature.operator_id == operator_id)
        )
        if feature_names:
            stmt = stmt.where(DerivedFeature.feature_name.in_(feature_names))
        stmt = stmt.order_by(DerivedFeature.observed_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
