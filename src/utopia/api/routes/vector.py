"""FastAPI routes for the Vector control plane.

These routes expose the directional hierarchy:
life arcs > seasons > missions > threads.

Vector is directional governance, not task management.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException

from utopia.api.deps import get_vector_service
from utopia.schemas.vector_ctrl import (
    LifeArcCreate,
    LifeArcRead,
    MissionCreate,
    MissionRead,
    SeasonCreate,
    SeasonRead,
    ThreadCreate,
    ThreadRead,
)
from utopia.services.vector_service import VectorService

router = APIRouter(prefix="/vector", tags=["vector"])


# ---------------------------------------------------------------------------
# Life Arcs
# ---------------------------------------------------------------------------


@router.post("/life-arcs", response_model=LifeArcRead, status_code=201)
async def create_life_arc(
    body: LifeArcCreate,
    svc: VectorService = Depends(get_vector_service),
) -> LifeArcRead:
    arc = await svc.create_life_arc(body)
    await svc.commit()
    return LifeArcRead.model_validate(arc)


@router.get("/life-arcs/{life_arc_id}", response_model=LifeArcRead)
async def get_life_arc(
    life_arc_id: uuid.UUID,
    svc: VectorService = Depends(get_vector_service),
) -> LifeArcRead:
    arc = await svc.get_life_arc(life_arc_id)
    if arc is None:
        raise HTTPException(status_code=404, detail="Life arc not found")
    return LifeArcRead.model_validate(arc)


# ---------------------------------------------------------------------------
# Seasons
# ---------------------------------------------------------------------------


@router.post("/seasons", response_model=SeasonRead, status_code=201)
async def create_season(
    body: SeasonCreate,
    svc: VectorService = Depends(get_vector_service),
) -> SeasonRead:
    season = await svc.create_season(body)
    await svc.commit()
    return SeasonRead.model_validate(season)


@router.get("/seasons/{season_id}", response_model=SeasonRead)
async def get_season(
    season_id: uuid.UUID,
    svc: VectorService = Depends(get_vector_service),
) -> SeasonRead:
    season = await svc.get_season(season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return SeasonRead.model_validate(season)


# ---------------------------------------------------------------------------
# Missions
# ---------------------------------------------------------------------------


@router.post("/missions", response_model=MissionRead, status_code=201)
async def create_mission(
    body: MissionCreate,
    svc: VectorService = Depends(get_vector_service),
) -> MissionRead:
    mission = await svc.create_mission(body)
    await svc.commit()
    return MissionRead.model_validate(mission)


@router.get("/missions/{mission_id}", response_model=MissionRead)
async def get_mission(
    mission_id: uuid.UUID,
    svc: VectorService = Depends(get_vector_service),
) -> MissionRead:
    mission = await svc.get_mission(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionRead.model_validate(mission)


@router.get("/missions", response_model=list[MissionRead])
async def list_missions(
    operator_id: uuid.UUID,
    season_id: uuid.UUID | None = None,
    svc: VectorService = Depends(get_vector_service),
) -> list[MissionRead]:
    missions = await svc.list_missions(operator_id, season_id=season_id)
    return [MissionRead.model_validate(m) for m in missions]


# ---------------------------------------------------------------------------
# Threads
# ---------------------------------------------------------------------------


@router.post("/threads", response_model=ThreadRead, status_code=201)
async def create_thread(
    body: ThreadCreate,
    svc: VectorService = Depends(get_vector_service),
) -> ThreadRead:
    thread = await svc.create_thread(body)
    await svc.commit()
    return ThreadRead.model_validate(thread)


@router.get("/threads/{thread_id}", response_model=ThreadRead)
async def get_thread(
    thread_id: uuid.UUID,
    svc: VectorService = Depends(get_vector_service),
) -> ThreadRead:
    thread = await svc.get_thread(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return ThreadRead.model_validate(thread)


@router.get("/threads", response_model=list[ThreadRead])
async def list_threads(
    operator_id: uuid.UUID,
    mission_id: uuid.UUID | None = None,
    svc: VectorService = Depends(get_vector_service),
) -> list[ThreadRead]:
    threads = await svc.list_threads(operator_id, mission_id=mission_id)
    return [ThreadRead.model_validate(t) for t in threads]
