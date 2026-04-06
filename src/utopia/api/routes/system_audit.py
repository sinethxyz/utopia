"""System Audit routes — AI orchestration and audit trail."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from utopia.api.deps import get_system_audit_service
from utopia.enums import ProcessingStatus
from utopia.schemas.system_audit import (
    EventLogCreate,
    EventLogRead,
    ModelProviderCreate,
    ModelProviderRead,
    ModelRunCreate,
    ModelRunRead,
    OutboxEventCreate,
    OutboxEventRead,
    RetrievalRunCreate,
    RetrievalRunRead,
)
from utopia.services.system_audit_service import SystemAuditService

router = APIRouter(prefix="/system", tags=["system"])


# ---------------------------------------------------------------------------
# Model Providers
# ---------------------------------------------------------------------------

@router.post("/providers", response_model=ModelProviderRead, status_code=201)
async def create_model_provider(
    data: ModelProviderCreate,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> ModelProviderRead:
    provider = await svc.create_model_provider(data)
    await svc.commit()
    return ModelProviderRead.model_validate(provider)


@router.get("/providers/{provider_id}", response_model=ModelProviderRead)
async def get_model_provider(
    provider_id: uuid.UUID,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> ModelProviderRead:
    provider = await svc.get_model_provider(provider_id)
    if provider is None:
        raise HTTPException(status_code=404, detail="Model provider not found")
    return ModelProviderRead.model_validate(provider)


@router.get("/providers", response_model=list[ModelProviderRead])
async def list_model_providers(
    active_only: bool = Query(default=False),
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> list[ModelProviderRead]:
    providers = await svc.list_model_providers(active_only)
    return [ModelProviderRead.model_validate(p) for p in providers]


# ---------------------------------------------------------------------------
# Model Runs
# ---------------------------------------------------------------------------

@router.post("/model-runs", response_model=ModelRunRead, status_code=201)
async def record_model_run(
    data: ModelRunCreate,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> ModelRunRead:
    run = await svc.record_model_run(data)
    await svc.commit()
    return ModelRunRead.model_validate(run)


@router.get("/model-runs/{run_id}", response_model=ModelRunRead)
async def get_model_run(
    run_id: uuid.UUID,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> ModelRunRead:
    run = await svc.get_model_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Model run not found")
    return ModelRunRead.model_validate(run)


@router.get("/model-runs", response_model=list[ModelRunRead])
async def list_model_runs(
    operator_id: uuid.UUID = Query(...),
    module_name: str | None = Query(default=None),
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> list[ModelRunRead]:
    runs = await svc.list_model_runs(operator_id, module_name)
    return [ModelRunRead.model_validate(r) for r in runs]


# ---------------------------------------------------------------------------
# Retrieval Runs
# ---------------------------------------------------------------------------

@router.post("/retrieval-runs", response_model=RetrievalRunRead, status_code=201)
async def record_retrieval_run(
    data: RetrievalRunCreate,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> RetrievalRunRead:
    run = await svc.record_retrieval_run(data)
    await svc.commit()
    return RetrievalRunRead.model_validate(run)


@router.get("/retrieval-runs/{run_id}", response_model=RetrievalRunRead)
async def get_retrieval_run(
    run_id: uuid.UUID,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> RetrievalRunRead:
    run = await svc.get_retrieval_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Retrieval run not found")
    return RetrievalRunRead.model_validate(run)


@router.get("/retrieval-runs", response_model=list[RetrievalRunRead])
async def list_retrieval_runs(
    operator_id: uuid.UUID = Query(...),
    collection: str | None = Query(default=None),
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> list[RetrievalRunRead]:
    runs = await svc.list_retrieval_runs(operator_id, collection)
    return [RetrievalRunRead.model_validate(r) for r in runs]


# ---------------------------------------------------------------------------
# Event Log
# ---------------------------------------------------------------------------

@router.post("/events", response_model=EventLogRead, status_code=201)
async def log_event(
    data: EventLogCreate,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> EventLogRead:
    event = await svc.log_event(data)
    await svc.commit()
    return EventLogRead.model_validate(event)


@router.get("/events/{event_id}", response_model=EventLogRead)
async def get_event(
    event_id: uuid.UUID,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> EventLogRead:
    event = await svc.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventLogRead.model_validate(event)


@router.get("/events", response_model=list[EventLogRead])
async def list_events(
    operator_id: uuid.UUID | None = Query(default=None),
    event_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> list[EventLogRead]:
    events = await svc.list_events(operator_id, event_type, severity)
    return [EventLogRead.model_validate(e) for e in events]


# ---------------------------------------------------------------------------
# Outbox Events
# ---------------------------------------------------------------------------

@router.post("/outbox", response_model=OutboxEventRead, status_code=201)
async def create_outbox_event(
    data: OutboxEventCreate,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> OutboxEventRead:
    event = await svc.create_outbox_event(data)
    await svc.commit()
    return OutboxEventRead.model_validate(event)


@router.get("/outbox/{event_id}", response_model=OutboxEventRead)
async def get_outbox_event(
    event_id: uuid.UUID,
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> OutboxEventRead:
    event = await svc.get_outbox_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Outbox event not found")
    return OutboxEventRead.model_validate(event)


@router.get("/outbox", response_model=list[OutboxEventRead])
async def list_outbox_events(
    status: ProcessingStatus | None = Query(default=None),
    svc: SystemAuditService = Depends(get_system_audit_service),
) -> list[OutboxEventRead]:
    events = await svc.list_outbox_events(status)
    return [OutboxEventRead.model_validate(e) for e in events]
