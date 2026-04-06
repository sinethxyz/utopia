"""Review & Calibration routes — the system's immune layer."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from utopia.api.deps import get_review_service
from utopia.enums import ReviewScope
from utopia.schemas.review import (
    CalibrationRecordCreate,
    CalibrationRecordRead,
    ClosureCreate,
    ClosureRead,
    PatternUpdateCreate,
    PatternUpdateRead,
    ReviewSessionCreate,
    ReviewSessionRead,
    RulePromotionCreate,
    RulePromotionRead,
)
from utopia.services.review_service import ReviewService

router = APIRouter(prefix="/review", tags=["review"])


# ---------------------------------------------------------------------------
# Closures
# ---------------------------------------------------------------------------

@router.post("/closures", response_model=ClosureRead, status_code=201)
async def create_closure(
    data: ClosureCreate,
    svc: ReviewService = Depends(get_review_service),
) -> ClosureRead:
    closure = await svc.create_closure(data)
    await svc.commit()
    return ClosureRead.model_validate(closure)


@router.get("/closures/{closure_id}", response_model=ClosureRead)
async def get_closure(
    closure_id: uuid.UUID,
    svc: ReviewService = Depends(get_review_service),
) -> ClosureRead:
    closure = await svc.get_closure(closure_id)
    if closure is None:
        raise HTTPException(status_code=404, detail="Closure not found")
    return ClosureRead.model_validate(closure)


@router.get("/closures", response_model=list[ClosureRead])
async def list_closures(
    operator_id: uuid.UUID = Query(...),
    thread_id: uuid.UUID | None = Query(default=None),
    mission_id: uuid.UUID | None = Query(default=None),
    svc: ReviewService = Depends(get_review_service),
) -> list[ClosureRead]:
    closures = await svc.list_closures(operator_id, thread_id, mission_id)
    return [ClosureRead.model_validate(c) for c in closures]


# ---------------------------------------------------------------------------
# Review Sessions
# ---------------------------------------------------------------------------

@router.post("/sessions", response_model=ReviewSessionRead, status_code=201)
async def create_review_session(
    data: ReviewSessionCreate,
    svc: ReviewService = Depends(get_review_service),
) -> ReviewSessionRead:
    session = await svc.create_review_session(data)
    await svc.commit()
    return ReviewSessionRead.model_validate(session)


@router.get("/sessions/{session_id}", response_model=ReviewSessionRead)
async def get_review_session(
    session_id: uuid.UUID,
    svc: ReviewService = Depends(get_review_service),
) -> ReviewSessionRead:
    session = await svc.get_review_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Review session not found")
    return ReviewSessionRead.model_validate(session)


@router.get("/sessions", response_model=list[ReviewSessionRead])
async def list_review_sessions(
    operator_id: uuid.UUID = Query(...),
    review_scope: ReviewScope | None = Query(default=None),
    svc: ReviewService = Depends(get_review_service),
) -> list[ReviewSessionRead]:
    sessions = await svc.list_review_sessions(operator_id, review_scope)
    return [ReviewSessionRead.model_validate(s) for s in sessions]


# ---------------------------------------------------------------------------
# Rule Promotions
# ---------------------------------------------------------------------------

@router.post(
    "/sessions/{session_id}/rule-promotions",
    response_model=RulePromotionRead,
    status_code=201,
)
async def record_rule_promotion(
    session_id: uuid.UUID,
    data: RulePromotionCreate,
    svc: ReviewService = Depends(get_review_service),
) -> RulePromotionRead:
    promotion = await svc.record_rule_promotion(data)
    await svc.commit()
    return RulePromotionRead.model_validate(promotion)


@router.get(
    "/sessions/{session_id}/rule-promotions",
    response_model=list[RulePromotionRead],
)
async def list_rule_promotions(
    session_id: uuid.UUID,
    svc: ReviewService = Depends(get_review_service),
) -> list[RulePromotionRead]:
    promotions = await svc.list_rule_promotions(session_id)
    return [RulePromotionRead.model_validate(p) for p in promotions]


# ---------------------------------------------------------------------------
# Pattern Updates
# ---------------------------------------------------------------------------

@router.post(
    "/sessions/{session_id}/pattern-updates",
    response_model=PatternUpdateRead,
    status_code=201,
)
async def record_pattern_update(
    session_id: uuid.UUID,
    data: PatternUpdateCreate,
    svc: ReviewService = Depends(get_review_service),
) -> PatternUpdateRead:
    update = await svc.record_pattern_update(data)
    await svc.commit()
    return PatternUpdateRead.model_validate(update)


@router.get(
    "/sessions/{session_id}/pattern-updates",
    response_model=list[PatternUpdateRead],
)
async def list_pattern_updates(
    session_id: uuid.UUID,
    svc: ReviewService = Depends(get_review_service),
) -> list[PatternUpdateRead]:
    updates = await svc.list_pattern_updates(session_id)
    return [PatternUpdateRead.model_validate(u) for u in updates]


# ---------------------------------------------------------------------------
# Calibration Records
# ---------------------------------------------------------------------------

@router.post("/calibrations", response_model=CalibrationRecordRead, status_code=201)
async def record_calibration(
    data: CalibrationRecordCreate,
    svc: ReviewService = Depends(get_review_service),
) -> CalibrationRecordRead:
    record = await svc.record_calibration(data)
    await svc.commit()
    return CalibrationRecordRead.model_validate(record)


@router.get("/calibrations/{record_id}", response_model=CalibrationRecordRead)
async def get_calibration_record(
    record_id: uuid.UUID,
    svc: ReviewService = Depends(get_review_service),
) -> CalibrationRecordRead:
    record = await svc.get_calibration_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Calibration record not found")
    return CalibrationRecordRead.model_validate(record)


@router.get("/calibrations", response_model=list[CalibrationRecordRead])
async def list_calibration_records(
    operator_id: uuid.UUID = Query(...),
    estimate_kind: str | None = Query(default=None),
    svc: ReviewService = Depends(get_review_service),
) -> list[CalibrationRecordRead]:
    records = await svc.list_calibration_records(operator_id, estimate_kind)
    return [CalibrationRecordRead.model_validate(r) for r in records]
