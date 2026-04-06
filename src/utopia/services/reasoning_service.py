"""ReasoningService — bounded-context service for the Problem Room.

The Reasoning layer captures the full arc of a decision:
raw prompt → structured problem → interrogations → decision brief
→ option paths → contradiction reports.

This service is the write interface for all reasoning artifacts.
The AI Fabric's Problem Structurer, Interrogator, Council, and
Contradiction Checker write their outputs through this service.
"""

import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.models.reasoning import (
    ContradictionReport,
    DecisionBrief,
    Interrogation,
    OptionPath,
    Problem,
    ProblemStructure,
)
from utopia.schemas.reasoning import (
    ContradictionReportCreate,
    DecisionBriefCreate,
    InterrogationCreate,
    OptionPathCreate,
    ProblemCreate,
    ProblemStructureCreate,
)


class ReasoningService:
    """Service for the Reasoning bounded context.

    All writes go through this service. The service owns ID generation
    and the structural relationships between reasoning artifacts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # Problems
    # ------------------------------------------------------------------

    async def create_problem(self, data: ProblemCreate) -> Problem:
        problem = Problem(
            id=uuid7(),
            operator_id=data.operator_id,
            title=data.title,
            raw_prompt=data.raw_prompt,
            problem_kind=data.problem_kind,
            urgency_score=data.urgency_score,
            stakes_score=data.stakes_score,
            uncertainty_score=data.uncertainty_score,
            state_at_creation=data.state_at_creation,
            thread_id=data.thread_id,
        )
        self._session.add(problem)
        await self._session.flush()
        return problem

    async def get_problem(self, problem_id: _uuid.UUID) -> Problem | None:
        return await self._session.get(Problem, problem_id)

    async def list_problems(
        self,
        operator_id: _uuid.UUID,
        limit: int = 50,
    ) -> list[Problem]:
        stmt = (
            select(Problem)
            .where(Problem.operator_id == operator_id)
            .order_by(Problem.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Problem Structures
    # ------------------------------------------------------------------

    async def create_problem_structure(
        self, data: ProblemStructureCreate
    ) -> ProblemStructure:
        structure = ProblemStructure(
            id=uuid7(),
            problem_id=data.problem_id,
            objective=data.objective,
            stakes=data.stakes,
            actors=data.actors,
            incentives=data.incentives,
            constraints=data.constraints,
            assumptions=data.assumptions,
            unknowns=data.unknowns,
            irreversibilities=data.irreversibilities,
            bottlenecks=data.bottlenecks,
            observable_facts=data.observable_facts,
            narrative_layer=data.narrative_layer,
            distortion_candidates=data.distortion_candidates,
            confidence=data.confidence,
        )
        self._session.add(structure)
        await self._session.flush()
        return structure

    async def get_problem_structure(
        self, problem_id: _uuid.UUID
    ) -> ProblemStructure | None:
        stmt = (
            select(ProblemStructure)
            .where(ProblemStructure.problem_id == problem_id)
            .order_by(ProblemStructure.generated_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Interrogations
    # ------------------------------------------------------------------

    async def create_interrogation(self, data: InterrogationCreate) -> Interrogation:
        interrogation = Interrogation(
            id=uuid7(),
            problem_id=data.problem_id,
            interrogation_kind=data.interrogation_kind,
            questions=data.questions,
            rationale=data.rationale,
        )
        self._session.add(interrogation)
        await self._session.flush()
        return interrogation

    async def list_interrogations(
        self, problem_id: _uuid.UUID
    ) -> list[Interrogation]:
        stmt = (
            select(Interrogation)
            .where(Interrogation.problem_id == problem_id)
            .order_by(Interrogation.generated_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Decision Briefs
    # ------------------------------------------------------------------

    async def create_decision_brief(self, data: DecisionBriefCreate) -> DecisionBrief:
        brief = DecisionBrief(
            id=uuid7(),
            problem_id=data.problem_id,
            classification=data.classification,
            summary=data.summary,
            key_unknowns=data.key_unknowns,
            blind_spots=data.blind_spots,
            risks=data.risks,
            relevant_lens_pack_ids=data.relevant_lens_pack_ids,
            recommendation_summary=data.recommendation_summary,
            confidence=data.confidence,
        )
        self._session.add(brief)
        await self._session.flush()
        return brief

    async def get_decision_brief(
        self, problem_id: _uuid.UUID
    ) -> DecisionBrief | None:
        stmt = (
            select(DecisionBrief)
            .where(DecisionBrief.problem_id == problem_id)
            .order_by(DecisionBrief.generated_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Option Paths
    # ------------------------------------------------------------------

    async def add_option_path(self, data: OptionPathCreate) -> OptionPath:
        option = OptionPath(
            id=uuid7(),
            decision_brief_id=data.decision_brief_id,
            option_label=data.option_label,
            description=data.description,
            expected_upside=data.expected_upside,
            expected_downside=data.expected_downside,
            reversibility=data.reversibility,
            risk_score=data.risk_score,
            recommendation_rank=data.recommendation_rank,
        )
        self._session.add(option)
        await self._session.flush()
        return option

    async def list_option_paths(
        self, decision_brief_id: _uuid.UUID
    ) -> list[OptionPath]:
        stmt = (
            select(OptionPath)
            .where(OptionPath.decision_brief_id == decision_brief_id)
            .order_by(OptionPath.recommendation_rank.asc().nulls_last())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Contradiction Reports
    # ------------------------------------------------------------------

    async def record_contradiction(
        self, data: ContradictionReportCreate
    ) -> ContradictionReport:
        report = ContradictionReport(
            id=uuid7(),
            operator_id=data.operator_id,
            problem_id=data.problem_id,
            contradiction_kind=data.contradiction_kind,
            description=data.description,
            evidence=data.evidence,
            severity=data.severity,
        )
        self._session.add(report)
        await self._session.flush()
        return report

    async def list_contradictions(
        self,
        operator_id: _uuid.UUID,
        problem_id: _uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[ContradictionReport]:
        stmt = (
            select(ContradictionReport)
            .where(ContradictionReport.operator_id == operator_id)
        )
        if problem_id is not None:
            stmt = stmt.where(ContradictionReport.problem_id == problem_id)
        stmt = stmt.order_by(ContradictionReport.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
