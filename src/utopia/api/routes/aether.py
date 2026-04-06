"""Aether routes — knowledge graph and typed memory."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from utopia.api.deps import get_aether_service
from utopia.schemas.aether import (
    CaseCreate,
    CaseRead,
    ConceptCreate,
    ConceptRead,
    DiagnosticQuestionCreate,
    DiagnosticQuestionRead,
    EdgeCreate,
    EdgeRead,
    ExtractionCreate,
    ExtractionRead,
    FailureModeCreate,
    FailureModeRead,
    HeuristicCreate,
    HeuristicRead,
    LensPackCreate,
    LensPackItemCreate,
    LensPackItemRead,
    LensPackRead,
    MechanismCreate,
    MechanismRead,
    PatternCreate,
    PatternRead,
    ProtocolCreate,
    ProtocolRead,
    RuleCreate,
    RuleRead,
    SourceChunkCreate,
    SourceChunkRead,
    SourceCreate,
    SourceRead,
    TradeoffCreate,
    TradeoffRead,
)
from utopia.services.aether_service import AetherService

router = APIRouter(prefix="/aether", tags=["aether"])


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

@router.post("/sources", response_model=SourceRead, status_code=201)
async def ingest_source(
    data: SourceCreate,
    svc: AetherService = Depends(get_aether_service),
) -> SourceRead:
    source = await svc.ingest_source(data)
    await svc.commit()
    return SourceRead.model_validate(source)


@router.get("/sources/{source_id}", response_model=SourceRead)
async def get_source(
    source_id: uuid.UUID,
    svc: AetherService = Depends(get_aether_service),
) -> SourceRead:
    source = await svc.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceRead.model_validate(source)


@router.post("/sources/{source_id}/chunks", response_model=SourceChunkRead, status_code=201)
async def add_source_chunk(
    source_id: uuid.UUID,
    data: SourceChunkCreate,
    svc: AetherService = Depends(get_aether_service),
) -> SourceChunkRead:
    chunk = await svc.add_source_chunk(data)
    await svc.commit()
    return SourceChunkRead.model_validate(chunk)


@router.post("/sources/{source_id}/extractions", response_model=ExtractionRead, status_code=201)
async def record_extraction(
    source_id: uuid.UUID,
    data: ExtractionCreate,
    svc: AetherService = Depends(get_aether_service),
) -> ExtractionRead:
    extraction = await svc.record_extraction(data)
    await svc.commit()
    return ExtractionRead.model_validate(extraction)


# ---------------------------------------------------------------------------
# Concepts
# ---------------------------------------------------------------------------

@router.post("/concepts", response_model=ConceptRead, status_code=201)
async def create_concept(
    data: ConceptCreate,
    svc: AetherService = Depends(get_aether_service),
) -> ConceptRead:
    concept = await svc.create_concept(data)
    await svc.commit()
    return ConceptRead.model_validate(concept)


@router.get("/concepts", response_model=list[ConceptRead])
async def list_concepts(
    operator_id: uuid.UUID = Query(...),
    svc: AetherService = Depends(get_aether_service),
) -> list[ConceptRead]:
    concepts = await svc.list_concepts(operator_id)
    return [ConceptRead.model_validate(c) for c in concepts]


# ---------------------------------------------------------------------------
# Mechanisms
# ---------------------------------------------------------------------------

@router.post("/mechanisms", response_model=MechanismRead, status_code=201)
async def create_mechanism(
    data: MechanismCreate,
    svc: AetherService = Depends(get_aether_service),
) -> MechanismRead:
    mechanism = await svc.create_mechanism(data)
    await svc.commit()
    return MechanismRead.model_validate(mechanism)


# ---------------------------------------------------------------------------
# Tradeoffs
# ---------------------------------------------------------------------------

@router.post("/tradeoffs", response_model=TradeoffRead, status_code=201)
async def create_tradeoff(
    data: TradeoffCreate,
    svc: AetherService = Depends(get_aether_service),
) -> TradeoffRead:
    tradeoff = await svc.create_tradeoff(data)
    await svc.commit()
    return TradeoffRead.model_validate(tradeoff)


# ---------------------------------------------------------------------------
# Failure Modes
# ---------------------------------------------------------------------------

@router.post("/failure-modes", response_model=FailureModeRead, status_code=201)
async def create_failure_mode(
    data: FailureModeCreate,
    svc: AetherService = Depends(get_aether_service),
) -> FailureModeRead:
    failure_mode = await svc.create_failure_mode(data)
    await svc.commit()
    return FailureModeRead.model_validate(failure_mode)


# ---------------------------------------------------------------------------
# Heuristics
# ---------------------------------------------------------------------------

@router.post("/heuristics", response_model=HeuristicRead, status_code=201)
async def create_heuristic(
    data: HeuristicCreate,
    svc: AetherService = Depends(get_aether_service),
) -> HeuristicRead:
    heuristic = await svc.create_heuristic(data)
    await svc.commit()
    return HeuristicRead.model_validate(heuristic)


# ---------------------------------------------------------------------------
# Diagnostic Questions
# ---------------------------------------------------------------------------

@router.post("/diagnostic-questions", response_model=DiagnosticQuestionRead, status_code=201)
async def create_diagnostic_question(
    data: DiagnosticQuestionCreate,
    svc: AetherService = Depends(get_aether_service),
) -> DiagnosticQuestionRead:
    question = await svc.create_diagnostic_question(data)
    await svc.commit()
    return DiagnosticQuestionRead.model_validate(question)


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------

@router.post("/protocols", response_model=ProtocolRead, status_code=201)
async def create_protocol(
    data: ProtocolCreate,
    svc: AetherService = Depends(get_aether_service),
) -> ProtocolRead:
    protocol = await svc.create_protocol(data)
    await svc.commit()
    return ProtocolRead.model_validate(protocol)


# ---------------------------------------------------------------------------
# Lens Packs
# ---------------------------------------------------------------------------

@router.post("/lens-packs", response_model=LensPackRead, status_code=201)
async def create_lens_pack(
    data: LensPackCreate,
    svc: AetherService = Depends(get_aether_service),
) -> LensPackRead:
    pack = await svc.create_lens_pack(data)
    await svc.commit()
    return LensPackRead.model_validate(pack)


@router.get("/lens-packs/{lens_pack_id}", response_model=LensPackRead)
async def get_lens_pack(
    lens_pack_id: uuid.UUID,
    svc: AetherService = Depends(get_aether_service),
) -> LensPackRead:
    pack = await svc.get_lens_pack(lens_pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Lens pack not found")
    return LensPackRead.model_validate(pack)


@router.post("/lens-packs/{lens_pack_id}/items", response_model=LensPackItemRead, status_code=201)
async def add_lens_pack_item(
    lens_pack_id: uuid.UUID,
    data: LensPackItemCreate,
    svc: AetherService = Depends(get_aether_service),
) -> LensPackItemRead:
    item = await svc.add_lens_pack_item(data)
    await svc.commit()
    return LensPackItemRead.model_validate(item)


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

@router.post("/cases", response_model=CaseRead, status_code=201)
async def create_case(
    data: CaseCreate,
    svc: AetherService = Depends(get_aether_service),
) -> CaseRead:
    case = await svc.create_case(data)
    await svc.commit()
    return CaseRead.model_validate(case)


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

@router.post("/rules", response_model=RuleRead, status_code=201)
async def create_rule(
    data: RuleCreate,
    svc: AetherService = Depends(get_aether_service),
) -> RuleRead:
    rule = await svc.create_rule(data)
    await svc.commit()
    return RuleRead.model_validate(rule)


@router.get("/rules", response_model=list[RuleRead])
async def list_rules(
    operator_id: uuid.UUID = Query(...),
    active: bool = Query(default=True),
    svc: AetherService = Depends(get_aether_service),
) -> list[RuleRead]:
    rules = await svc.list_rules(operator_id, active=active)
    return [RuleRead.model_validate(r) for r in rules]


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

@router.post("/patterns", response_model=PatternRead, status_code=201)
async def create_pattern(
    data: PatternCreate,
    svc: AetherService = Depends(get_aether_service),
) -> PatternRead:
    pattern = await svc.create_pattern(data)
    await svc.commit()
    return PatternRead.model_validate(pattern)


@router.get("/patterns", response_model=list[PatternRead])
async def list_patterns(
    operator_id: uuid.UUID = Query(...),
    svc: AetherService = Depends(get_aether_service),
) -> list[PatternRead]:
    patterns = await svc.list_patterns(operator_id)
    return [PatternRead.model_validate(p) for p in patterns]


# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------

@router.post("/edges", response_model=EdgeRead, status_code=201)
async def create_edge(
    data: EdgeCreate,
    svc: AetherService = Depends(get_aether_service),
) -> EdgeRead:
    edge = await svc.create_edge(data)
    await svc.commit()
    return EdgeRead.model_validate(edge)


@router.get("/edges", response_model=list[EdgeRead])
async def list_edges(
    operator_id: uuid.UUID = Query(...),
    src_kind: str | None = Query(default=None),
    src_id: uuid.UUID | None = Query(default=None),
    svc: AetherService = Depends(get_aether_service),
) -> list[EdgeRead]:
    if src_kind is not None and src_id is not None:
        edges = await svc.get_edges_for_object(operator_id, src_kind, src_id)
    else:
        edges = await svc.list_edges(operator_id)
    return [EdgeRead.model_validate(e) for e in edges]
