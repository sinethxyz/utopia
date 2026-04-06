"""ReviewService — bounded-context service for Review & Calibration.

The Review & Calibration layer is the system's immune layer:
closures capture endings, review sessions examine evidence,
rule promotions push insights to Aether, pattern updates refine
behavioral models, and calibration records measure estimate accuracy.

This service is the write interface for all review artifacts.
"""

import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.enums import ReviewScope
from utopia.models.review import (
    CalibrationRecord,
    Closure,
    PatternUpdate,
    ReviewSession,
    RulePromotion,
)
from utopia.schemas.review import (
    CalibrationRecordCreate,
    ClosureCreate,
    PatternUpdateCreate,
    ReviewSessionCreate,
    RulePromotionCreate,
)


class ReviewService:
    """Service for the Review & Calibration bounded context.

    All writes go through this service. The service owns ID generation
    and the structural relationships between review artifacts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # Closures
    # ------------------------------------------------------------------

    async def create_closure(self, data: ClosureCreate) -> Closure:
        closure = Closure(
            id=uuid7(),
            operator_id=data.operator_id,
            thread_id=data.thread_id,
            mission_id=data.mission_id,
            closure_type=data.closure_type,
            outcome_summary=data.outcome_summary,
            lessons_learned=data.lessons_learned,
            truth_revealed=data.truth_revealed,
            final_trace_id=data.final_trace_id,
            success_score=data.success_score,
        )
        self._session.add(closure)
        await self._session.flush()
        return closure

    async def get_closure(self, closure_id: _uuid.UUID) -> Closure | None:
        return await self._session.get(Closure, closure_id)

    async def list_closures(
        self,
        operator_id: _uuid.UUID,
        thread_id: _uuid.UUID | None = None,
        mission_id: _uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[Closure]:
        stmt = (
            select(Closure)
            .where(Closure.operator_id == operator_id)
        )
        if thread_id is not None:
            stmt = stmt.where(Closure.thread_id == thread_id)
        if mission_id is not None:
            stmt = stmt.where(Closure.mission_id == mission_id)
        stmt = stmt.order_by(Closure.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Review Sessions
    # ------------------------------------------------------------------

    async def create_review_session(
        self, data: ReviewSessionCreate
    ) -> ReviewSession:
        session = ReviewSession(
            id=uuid7(),
            operator_id=data.operator_id,
            review_scope=data.review_scope,
            window_start=data.window_start,
            window_end=data.window_end,
            summary=data.summary,
            insights=data.insights,
            trace_ids_reviewed=data.trace_ids_reviewed,
            patterns_identified=data.patterns_identified,
        )
        self._session.add(session)
        await self._session.flush()
        return session

    async def get_review_session(
        self, session_id: _uuid.UUID
    ) -> ReviewSession | None:
        return await self._session.get(ReviewSession, session_id)

    async def list_review_sessions(
        self,
        operator_id: _uuid.UUID,
        review_scope: ReviewScope | None = None,
        limit: int = 50,
    ) -> list[ReviewSession]:
        stmt = (
            select(ReviewSession)
            .where(ReviewSession.operator_id == operator_id)
        )
        if review_scope is not None:
            stmt = stmt.where(ReviewSession.review_scope == review_scope)
        stmt = stmt.order_by(ReviewSession.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Rule Promotions
    # ------------------------------------------------------------------

    async def record_rule_promotion(
        self, data: RulePromotionCreate
    ) -> RulePromotion:
        promotion = RulePromotion(
            id=uuid7(),
            operator_id=data.operator_id,
            review_session_id=data.review_session_id,
            rule_id=data.rule_id,
            evidence_summary=data.evidence_summary,
            supporting_trace_ids=data.supporting_trace_ids,
            confidence=data.confidence,
        )
        self._session.add(promotion)
        await self._session.flush()
        return promotion

    async def get_rule_promotion(
        self, promotion_id: _uuid.UUID
    ) -> RulePromotion | None:
        return await self._session.get(RulePromotion, promotion_id)

    async def list_rule_promotions(
        self, review_session_id: _uuid.UUID
    ) -> list[RulePromotion]:
        stmt = (
            select(RulePromotion)
            .where(RulePromotion.review_session_id == review_session_id)
            .order_by(RulePromotion.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Pattern Updates
    # ------------------------------------------------------------------

    async def record_pattern_update(
        self, data: PatternUpdateCreate
    ) -> PatternUpdate:
        update = PatternUpdate(
            id=uuid7(),
            operator_id=data.operator_id,
            review_session_id=data.review_session_id,
            pattern_id=data.pattern_id,
            update_kind=data.update_kind,
            evidence_summary=data.evidence_summary,
            supporting_trace_ids=data.supporting_trace_ids,
            confidence_before=data.confidence_before,
            confidence_after=data.confidence_after,
        )
        self._session.add(update)
        await self._session.flush()
        return update

    async def get_pattern_update(
        self, update_id: _uuid.UUID
    ) -> PatternUpdate | None:
        return await self._session.get(PatternUpdate, update_id)

    async def list_pattern_updates(
        self, review_session_id: _uuid.UUID
    ) -> list[PatternUpdate]:
        stmt = (
            select(PatternUpdate)
            .where(PatternUpdate.review_session_id == review_session_id)
            .order_by(PatternUpdate.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Calibration Records
    # ------------------------------------------------------------------

    async def record_calibration(
        self, data: CalibrationRecordCreate
    ) -> CalibrationRecord:
        record = CalibrationRecord(
            id=uuid7(),
            operator_id=data.operator_id,
            review_session_id=data.review_session_id,
            estimate_kind=data.estimate_kind,
            estimate_id=data.estimate_id,
            trace_id=data.trace_id,
            predicted_value=data.predicted_value,
            actual_value=data.actual_value,
            accuracy_score=data.accuracy_score,
            drift_direction=data.drift_direction,
            notes=data.notes,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def get_calibration_record(
        self, record_id: _uuid.UUID
    ) -> CalibrationRecord | None:
        return await self._session.get(CalibrationRecord, record_id)

    async def list_calibration_records(
        self,
        operator_id: _uuid.UUID,
        estimate_kind: str | None = None,
        limit: int = 50,
    ) -> list[CalibrationRecord]:
        stmt = (
            select(CalibrationRecord)
            .where(CalibrationRecord.operator_id == operator_id)
        )
        if estimate_kind is not None:
            stmt = stmt.where(CalibrationRecord.estimate_kind == estimate_kind)
        stmt = stmt.order_by(CalibrationRecord.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
