"""Physiology routes — WHOOP integration and derived physiological features."""

import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from utopia.api.deps import get_physiology_service
from utopia.schemas.physiology import (
    BiomarkerPanelCreate,
    BiomarkerPanelRead,
    PhysiologyFeatureCreate,
    PhysiologyFeatureRead,
    WhoopBodyMeasurementCreate,
    WhoopBodyMeasurementRead,
    WhoopConnectionCreate,
    WhoopConnectionRead,
    WhoopCycleCreate,
    WhoopCycleRead,
    WhoopRecoveryCreate,
    WhoopRecoveryRead,
    WhoopSleepCreate,
    WhoopSleepRead,
    WhoopWorkoutCreate,
    WhoopWorkoutRead,
)
from utopia.services.physiology_service import PhysiologyService

router = APIRouter(prefix="/physiology", tags=["physiology"])


# ---------------------------------------------------------------------------
# WHOOP Connections
# ---------------------------------------------------------------------------

@router.post("/whoop/connections", response_model=WhoopConnectionRead, status_code=201)
async def create_whoop_connection(
    data: WhoopConnectionCreate,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> WhoopConnectionRead:
    conn = await svc.connect_whoop(data)
    await svc.commit()
    return WhoopConnectionRead.model_validate(conn)


@router.get("/whoop/connections/{connection_id}", response_model=WhoopConnectionRead)
async def get_whoop_connection(
    connection_id: uuid.UUID,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> WhoopConnectionRead:
    conn = await svc.get_whoop_connection(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="WHOOP connection not found")
    return WhoopConnectionRead.model_validate(conn)


# ---------------------------------------------------------------------------
# WHOOP Body Measurements
# ---------------------------------------------------------------------------

@router.post("/whoop/body-measurements", response_model=WhoopBodyMeasurementRead, status_code=201)
async def record_body_measurement(
    data: WhoopBodyMeasurementCreate,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> WhoopBodyMeasurementRead:
    measurement = await svc.record_body_measurement(data)
    await svc.commit()
    return WhoopBodyMeasurementRead.model_validate(measurement)


# ---------------------------------------------------------------------------
# WHOOP Cycles
# ---------------------------------------------------------------------------

@router.post("/whoop/cycles", response_model=WhoopCycleRead, status_code=201)
async def upsert_cycle(
    data: WhoopCycleCreate,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> WhoopCycleRead:
    cycle = await svc.upsert_cycle(data)
    await svc.commit()
    return WhoopCycleRead.model_validate(cycle)


# ---------------------------------------------------------------------------
# WHOOP Sleeps
# ---------------------------------------------------------------------------

@router.post("/whoop/sleeps", response_model=WhoopSleepRead, status_code=201)
async def upsert_sleep(
    data: WhoopSleepCreate,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> WhoopSleepRead:
    sleep = await svc.upsert_sleep(data)
    await svc.commit()
    return WhoopSleepRead.model_validate(sleep)


# ---------------------------------------------------------------------------
# WHOOP Recoveries
# ---------------------------------------------------------------------------

@router.post("/whoop/recoveries", response_model=WhoopRecoveryRead, status_code=201)
async def upsert_recovery(
    data: WhoopRecoveryCreate,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> WhoopRecoveryRead:
    recovery = await svc.upsert_recovery(data)
    await svc.commit()
    return WhoopRecoveryRead.model_validate(recovery)


# ---------------------------------------------------------------------------
# WHOOP Workouts
# ---------------------------------------------------------------------------

@router.post("/whoop/workouts", response_model=WhoopWorkoutRead, status_code=201)
async def upsert_workout(
    data: WhoopWorkoutCreate,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> WhoopWorkoutRead:
    workout = await svc.upsert_workout(data)
    await svc.commit()
    return WhoopWorkoutRead.model_validate(workout)


# ---------------------------------------------------------------------------
# Physiology Features
# ---------------------------------------------------------------------------

@router.post("/features", response_model=PhysiologyFeatureRead, status_code=201)
async def store_physiology_feature(
    data: PhysiologyFeatureCreate,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> PhysiologyFeatureRead:
    feature = await svc.store_physiology_feature(data)
    await svc.commit()
    return PhysiologyFeatureRead.model_validate(feature)


@router.get("/features", response_model=list[PhysiologyFeatureRead])
async def list_physiology_features(
    operator_id: uuid.UUID = Query(...),
    feature_date: datetime.date | None = Query(default=None),
    svc: PhysiologyService = Depends(get_physiology_service),
) -> list[PhysiologyFeatureRead]:
    features = await svc.get_latest_features(operator_id, feature_date)
    return [PhysiologyFeatureRead.model_validate(f) for f in features]


# ---------------------------------------------------------------------------
# Biomarker Panels
# ---------------------------------------------------------------------------

@router.post("/biomarker-panels", response_model=BiomarkerPanelRead, status_code=201)
async def record_biomarker_panel(
    data: BiomarkerPanelCreate,
    svc: PhysiologyService = Depends(get_physiology_service),
) -> BiomarkerPanelRead:
    panel = await svc.record_biomarker_panel(data)
    await svc.commit()
    return BiomarkerPanelRead.model_validate(panel)
