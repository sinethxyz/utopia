"""FastAPI routes for the Evidence sensing layer.

Evidence captures what is true about the operator's present moment.
These routes are append-heavy: checkins flow in, behavior events
accumulate, context snapshots are captured.

Evidence does not interpret — that is the AI Fabric's job.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException

from utopia.api.deps import get_evidence_service
from utopia.schemas.evidence import (
    BehaviorEventCreate,
    BehaviorEventRead,
    ContextSnapshotCreate,
    ContextSnapshotRead,
    DerivedFeatureCreate,
    DerivedFeatureRead,
    SubjectiveCheckinCreate,
    SubjectiveCheckinRead,
)
from utopia.services.evidence_service import EvidenceService

router = APIRouter(prefix="/evidence", tags=["evidence"])


# ---------------------------------------------------------------------------
# Subjective Checkins
# ---------------------------------------------------------------------------


@router.post("/checkins", response_model=SubjectiveCheckinRead, status_code=201)
async def record_checkin(
    body: SubjectiveCheckinCreate,
    svc: EvidenceService = Depends(get_evidence_service),
) -> SubjectiveCheckinRead:
    checkin = await svc.record_checkin(body)
    await svc.commit()
    return SubjectiveCheckinRead.model_validate(checkin)


@router.get("/checkins/{checkin_id}", response_model=SubjectiveCheckinRead)
async def get_checkin(
    checkin_id: uuid.UUID,
    svc: EvidenceService = Depends(get_evidence_service),
) -> SubjectiveCheckinRead:
    checkin = await svc.get_checkin(checkin_id)
    if checkin is None:
        raise HTTPException(status_code=404, detail="Checkin not found")
    return SubjectiveCheckinRead.model_validate(checkin)


@router.get("/checkins", response_model=list[SubjectiveCheckinRead])
async def list_checkins(
    operator_id: uuid.UUID,
    thread_id: uuid.UUID | None = None,
    limit: int = 20,
    svc: EvidenceService = Depends(get_evidence_service),
) -> list[SubjectiveCheckinRead]:
    checkins = await svc.list_checkins(operator_id, thread_id=thread_id, limit=limit)
    return [SubjectiveCheckinRead.model_validate(c) for c in checkins]


# ---------------------------------------------------------------------------
# Behavior Events
# ---------------------------------------------------------------------------


@router.post("/behavior-events", response_model=BehaviorEventRead, status_code=201)
async def record_behavior_event(
    body: BehaviorEventCreate,
    svc: EvidenceService = Depends(get_evidence_service),
) -> BehaviorEventRead:
    event = await svc.record_behavior_event(body)
    await svc.commit()
    return BehaviorEventRead.model_validate(event)


@router.get("/behavior-events", response_model=list[BehaviorEventRead])
async def list_behavior_events(
    operator_id: uuid.UUID,
    thread_id: uuid.UUID | None = None,
    event_type: str | None = None,
    limit: int = 50,
    svc: EvidenceService = Depends(get_evidence_service),
) -> list[BehaviorEventRead]:
    events = await svc.list_behavior_events(
        operator_id, thread_id=thread_id, event_type=event_type, limit=limit
    )
    return [BehaviorEventRead.model_validate(e) for e in events]


# ---------------------------------------------------------------------------
# Context Snapshots
# ---------------------------------------------------------------------------


@router.post("/context-snapshots", response_model=ContextSnapshotRead, status_code=201)
async def record_context_snapshot(
    body: ContextSnapshotCreate,
    svc: EvidenceService = Depends(get_evidence_service),
) -> ContextSnapshotRead:
    snapshot = await svc.record_context_snapshot(body)
    await svc.commit()
    return ContextSnapshotRead.model_validate(snapshot)


@router.get("/context-snapshots/latest", response_model=ContextSnapshotRead)
async def get_latest_context(
    operator_id: uuid.UUID,
    svc: EvidenceService = Depends(get_evidence_service),
) -> ContextSnapshotRead:
    snapshot = await svc.get_latest_context(operator_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No context snapshot found")
    return ContextSnapshotRead.model_validate(snapshot)


# ---------------------------------------------------------------------------
# Derived Features
# ---------------------------------------------------------------------------


@router.post("/derived-features", response_model=DerivedFeatureRead, status_code=201)
async def store_derived_feature(
    body: DerivedFeatureCreate,
    svc: EvidenceService = Depends(get_evidence_service),
) -> DerivedFeatureRead:
    feature = await svc.store_derived_feature(body)
    await svc.commit()
    return DerivedFeatureRead.model_validate(feature)


@router.get("/derived-features", response_model=list[DerivedFeatureRead])
async def get_latest_features(
    operator_id: uuid.UUID,
    limit: int = 50,
    svc: EvidenceService = Depends(get_evidence_service),
) -> list[DerivedFeatureRead]:
    features = await svc.get_latest_features(operator_id, limit=limit)
    return [DerivedFeatureRead.model_validate(f) for f in features]
