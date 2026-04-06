"""Reasoning routes — problem structurer and decision artifacts."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from utopia.api.deps import get_reasoning_service
from utopia.schemas.reasoning import (
    ContradictionReportCreate,
    ContradictionReportRead,
    DecisionBriefCreate,
    DecisionBriefRead,
    InterrogationCreate,
    InterrogationRead,
    OptionPathCreate,
    OptionPathRead,
    ProblemCreate,
    ProblemRead,
    ProblemStructureCreate,
    ProblemStructureRead,
)
from utopia.services.reasoning_service import ReasoningService

router = APIRouter(prefix="/reasoning", tags=["reasoning"])


# ---------------------------------------------------------------------------
# Problems
# ---------------------------------------------------------------------------

@router.post("/problems", response_model=ProblemRead, status_code=201)
async def create_problem(
    data: ProblemCreate,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> ProblemRead:
    problem = await svc.create_problem(data)
    await svc.commit()
    return ProblemRead.model_validate(problem)


@router.get("/problems/{problem_id}", response_model=ProblemRead)
async def get_problem(
    problem_id: uuid.UUID,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> ProblemRead:
    problem = await svc.get_problem(problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return ProblemRead.model_validate(problem)


@router.get("/problems", response_model=list[ProblemRead])
async def list_problems(
    operator_id: uuid.UUID = Query(...),
    svc: ReasoningService = Depends(get_reasoning_service),
) -> list[ProblemRead]:
    problems = await svc.list_problems(operator_id)
    return [ProblemRead.model_validate(p) for p in problems]


# ---------------------------------------------------------------------------
# Problem Structures
# ---------------------------------------------------------------------------

@router.post("/problems/{problem_id}/structure", response_model=ProblemStructureRead, status_code=201)
async def create_problem_structure(
    problem_id: uuid.UUID,
    data: ProblemStructureCreate,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> ProblemStructureRead:
    structure = await svc.create_problem_structure(data)
    await svc.commit()
    return ProblemStructureRead.model_validate(structure)


@router.get("/problems/{problem_id}/structure", response_model=ProblemStructureRead)
async def get_problem_structure(
    problem_id: uuid.UUID,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> ProblemStructureRead:
    structure = await svc.get_problem_structure(problem_id)
    if structure is None:
        raise HTTPException(status_code=404, detail="Problem structure not found")
    return ProblemStructureRead.model_validate(structure)


# ---------------------------------------------------------------------------
# Interrogations
# ---------------------------------------------------------------------------

@router.post("/problems/{problem_id}/interrogations", response_model=InterrogationRead, status_code=201)
async def create_interrogation(
    problem_id: uuid.UUID,
    data: InterrogationCreate,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> InterrogationRead:
    interrogation = await svc.create_interrogation(data)
    await svc.commit()
    return InterrogationRead.model_validate(interrogation)


@router.get("/problems/{problem_id}/interrogations", response_model=list[InterrogationRead])
async def list_interrogations(
    problem_id: uuid.UUID,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> list[InterrogationRead]:
    interrogations = await svc.list_interrogations(problem_id)
    return [InterrogationRead.model_validate(i) for i in interrogations]


# ---------------------------------------------------------------------------
# Decision Briefs
# ---------------------------------------------------------------------------

@router.post("/problems/{problem_id}/brief", response_model=DecisionBriefRead, status_code=201)
async def create_decision_brief(
    problem_id: uuid.UUID,
    data: DecisionBriefCreate,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> DecisionBriefRead:
    brief = await svc.create_decision_brief(data)
    await svc.commit()
    return DecisionBriefRead.model_validate(brief)


@router.get("/problems/{problem_id}/brief", response_model=DecisionBriefRead)
async def get_decision_brief(
    problem_id: uuid.UUID,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> DecisionBriefRead:
    brief = await svc.get_decision_brief(problem_id)
    if brief is None:
        raise HTTPException(status_code=404, detail="Decision brief not found")
    return DecisionBriefRead.model_validate(brief)


# ---------------------------------------------------------------------------
# Option Paths
# ---------------------------------------------------------------------------

@router.post("/briefs/{brief_id}/options", response_model=OptionPathRead, status_code=201)
async def add_option_path(
    brief_id: uuid.UUID,
    data: OptionPathCreate,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> OptionPathRead:
    option = await svc.add_option_path(data)
    await svc.commit()
    return OptionPathRead.model_validate(option)


@router.get("/briefs/{brief_id}/options", response_model=list[OptionPathRead])
async def list_option_paths(
    brief_id: uuid.UUID,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> list[OptionPathRead]:
    options = await svc.list_option_paths(brief_id)
    return [OptionPathRead.model_validate(o) for o in options]


# ---------------------------------------------------------------------------
# Contradiction Reports
# ---------------------------------------------------------------------------

@router.post("/contradictions", response_model=ContradictionReportRead, status_code=201)
async def record_contradiction(
    data: ContradictionReportCreate,
    svc: ReasoningService = Depends(get_reasoning_service),
) -> ContradictionReportRead:
    report = await svc.record_contradiction(data)
    await svc.commit()
    return ContradictionReportRead.model_validate(report)


@router.get("/contradictions", response_model=list[ContradictionReportRead])
async def list_contradictions(
    operator_id: uuid.UUID = Query(...),
    problem_id: uuid.UUID | None = Query(default=None),
    svc: ReasoningService = Depends(get_reasoning_service),
) -> list[ContradictionReportRead]:
    reports = await svc.list_contradictions(operator_id, problem_id)
    return [ContradictionReportRead.model_validate(r) for r in reports]
