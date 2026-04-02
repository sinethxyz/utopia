"""VectorService — bounded-context service for the directional control plane.

This is not generic CRUD. Each method carries domain semantics:
- Life arcs are long-horizon directional commitments
- Seasons are bounded focus phases with a thesis
- Missions have success/failure/drift definitions
- Threads are live lines of work with operational metadata

The service handles ID generation (UUIDv7 for time-ordered keys)
and enforces the directional hierarchy.
"""

import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.models.vector_ctrl import (
    AntiGoal,
    LifeArc,
    Mission,
    Season,
    Thread,
    ThreadConstraint,
)
from utopia.schemas.vector_ctrl import (
    AntiGoalCreate,
    LifeArcCreate,
    MissionCreate,
    SeasonCreate,
    ThreadConstraintCreate,
    ThreadCreate,
)


class VectorService:
    """Service for the Vector control plane.

    All writes go through this service. It owns ID generation
    and domain invariants for the directional hierarchy.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # Life Arcs
    # ------------------------------------------------------------------

    async def create_life_arc(self, data: LifeArcCreate) -> LifeArc:
        arc = LifeArc(
            id=uuid7(),
            operator_id=data.operator_id,
            title=data.title,
            description=data.description,
            status=data.status,
            horizon_start=data.horizon_start,
            horizon_end=data.horizon_end,
            success_definition=data.success_definition,
            anti_goals=data.anti_goals,
        )
        self._session.add(arc)
        await self._session.flush()
        return arc

    async def get_life_arc(self, life_arc_id: _uuid.UUID) -> LifeArc | None:
        return await self._session.get(LifeArc, life_arc_id)

    # ------------------------------------------------------------------
    # Seasons
    # ------------------------------------------------------------------

    async def create_season(self, data: SeasonCreate) -> Season:
        season = Season(
            id=uuid7(),
            operator_id=data.operator_id,
            life_arc_id=data.life_arc_id,
            title=data.title,
            thesis=data.thesis,
            start_date=data.start_date,
            end_date=data.end_date,
            priority_stack=data.priority_stack,
            status=data.status,
        )
        self._session.add(season)
        await self._session.flush()
        return season

    async def get_season(self, season_id: _uuid.UUID) -> Season | None:
        return await self._session.get(Season, season_id)

    # ------------------------------------------------------------------
    # Missions
    # ------------------------------------------------------------------

    async def create_mission(self, data: MissionCreate) -> Mission:
        """Create a strategically meaningful objective.

        Missions are directional commitments, not tasks.
        success_definition, failure_definition, and drift_definition
        are the fields that give Vector its governance power.
        """
        mission = Mission(
            id=uuid7(),
            operator_id=data.operator_id,
            season_id=data.season_id,
            title=data.title,
            description=data.description,
            mission_kind=data.mission_kind,
            priority_score=data.priority_score,
            status=data.status,
            success_definition=data.success_definition,
            failure_definition=data.failure_definition,
            drift_definition=data.drift_definition,
        )
        self._session.add(mission)
        await self._session.flush()
        return mission

    async def get_mission(self, mission_id: _uuid.UUID) -> Mission | None:
        return await self._session.get(Mission, mission_id)

    async def list_missions(
        self, operator_id: _uuid.UUID, season_id: _uuid.UUID | None = None
    ) -> list[Mission]:
        stmt = select(Mission).where(Mission.operator_id == operator_id)
        if season_id is not None:
            stmt = stmt.where(Mission.season_id == season_id)
        stmt = stmt.order_by(Mission.priority_score.desc().nulls_last(), Mission.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Threads
    # ------------------------------------------------------------------

    async def create_thread(self, data: ThreadCreate) -> Thread:
        """Open a live line of work within a mission.

        Threads carry operational metadata (complexity, ambiguity,
        re-entry risk) that downstream subsystems — State Estimator,
        Blocker Classifier, Schrodinger — use for policy selection.
        """
        thread = Thread(
            id=uuid7(),
            operator_id=data.operator_id,
            mission_id=data.mission_id,
            parent_thread_id=data.parent_thread_id,
            title=data.title,
            description=data.description,
            thread_kind=data.thread_kind,
            status=data.status,
            complexity_score=data.complexity_score,
            ambiguity_score=data.ambiguity_score,
            reentry_risk_score=data.reentry_risk_score,
            next_edge_summary=data.next_edge_summary,
        )
        self._session.add(thread)
        await self._session.flush()
        return thread

    async def get_thread(self, thread_id: _uuid.UUID) -> Thread | None:
        return await self._session.get(Thread, thread_id)

    async def list_threads(
        self,
        operator_id: _uuid.UUID,
        mission_id: _uuid.UUID | None = None,
    ) -> list[Thread]:
        stmt = select(Thread).where(Thread.operator_id == operator_id)
        if mission_id is not None:
            stmt = stmt.where(Thread.mission_id == mission_id)
        stmt = stmt.order_by(Thread.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Thread Constraints
    # ------------------------------------------------------------------

    async def add_thread_constraint(self, data: ThreadConstraintCreate) -> ThreadConstraint:
        constraint = ThreadConstraint(
            id=uuid7(),
            thread_id=data.thread_id,
            constraint_type=data.constraint_type,
            description=data.description,
            hardness=data.hardness,
        )
        self._session.add(constraint)
        await self._session.flush()
        return constraint

    # ------------------------------------------------------------------
    # Anti-Goals
    # ------------------------------------------------------------------

    async def create_anti_goal(self, data: AntiGoalCreate) -> AntiGoal:
        """Define what must not happen at a given directional scope.

        Anti-goals are hard boundaries that the Vector Arbiter uses
        to detect drift and block misaligned action proposals.
        """
        anti_goal = AntiGoal(
            id=uuid7(),
            operator_id=data.operator_id,
            scope_type=data.scope_type,
            scope_id=data.scope_id,
            description=data.description,
        )
        self._session.add(anti_goal)
        await self._session.flush()
        return anti_goal
