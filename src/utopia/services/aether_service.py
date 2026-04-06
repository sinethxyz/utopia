"""AetherService — bounded-context service for the knowledge graph.

Aether stores typed memory: extracted intelligence from sources,
knowledge atoms (concepts, mechanisms, heuristics, rules, patterns),
and the polymorphic edge graph that relates them.

This service enables the AI Fabric's Context Retriever, Council, and
Contradiction Checker to access structured knowledge during reasoning.
"""

import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.models.aether import (
    Case,
    Concept,
    DiagnosticQuestion,
    Edge,
    Extraction,
    FailureMode,
    Heuristic,
    LensPack,
    LensPackItem,
    Mechanism,
    Pattern,
    Protocol,
    Rule,
    Source,
    SourceChunk,
    Tradeoff,
)
from utopia.schemas.aether import (
    CaseCreate,
    ConceptCreate,
    DiagnosticQuestionCreate,
    EdgeCreate,
    ExtractionCreate,
    FailureModeCreate,
    HeuristicCreate,
    LensPackCreate,
    LensPackItemCreate,
    MechanismCreate,
    PatternCreate,
    ProtocolCreate,
    RuleCreate,
    SourceChunkCreate,
    SourceCreate,
    TradeoffCreate,
)


class AetherService:
    """Service for the Aether knowledge layer.

    All writes go through this service. It owns ID generation and
    maintains the integrity of the knowledge graph.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------------

    async def ingest_source(self, data: SourceCreate) -> Source:
        source = Source(
            id=uuid7(),
            operator_id=data.operator_id,
            source_kind=data.source_kind,
            title=data.title,
            author=data.author,
            published_at=data.published_at,
            ingest_status=data.ingest_status,
            canonical_uri=data.canonical_uri,
            storage_uri=data.storage_uri,
            checksum=data.checksum,
            metadata_=data.metadata_,
        )
        self._session.add(source)
        await self._session.flush()
        return source

    async def get_source(self, source_id: _uuid.UUID) -> Source | None:
        return await self._session.get(Source, source_id)

    async def add_source_chunk(self, data: SourceChunkCreate) -> SourceChunk:
        chunk = SourceChunk(
            id=uuid7(),
            source_id=data.source_id,
            chunk_index=data.chunk_index,
            raw_text=data.raw_text,
            token_count=data.token_count,
            semantic_label=data.semantic_label,
            metadata_=data.metadata_,
        )
        self._session.add(chunk)
        await self._session.flush()
        return chunk

    async def record_extraction(self, data: ExtractionCreate) -> Extraction:
        """Upsert an extraction on (source_id, extraction_version) conflict."""
        stmt = (
            pg_insert(Extraction)
            .values(
                id=uuid7(),
                source_id=data.source_id,
                extraction_version=data.extraction_version,
                extraction_status=data.extraction_status,
                thesis=data.thesis,
                summary=data.summary,
                confidence=data.confidence,
                extracted_at=data.extracted_at,
                model_run_id=data.model_run_id,
            )
            .on_conflict_do_update(
                constraint="uq_extractions_source_version",
                set_={
                    "extraction_status": data.extraction_status,
                    "thesis": data.thesis,
                    "summary": data.summary,
                    "confidence": data.confidence,
                    "extracted_at": data.extracted_at,
                    "model_run_id": data.model_run_id,
                },
            )
            .returning(Extraction)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    # ------------------------------------------------------------------
    # Knowledge Atoms
    # ------------------------------------------------------------------

    async def create_concept(self, data: ConceptCreate) -> Concept:
        """Upsert a concept on (operator_id, canonical_name) conflict."""
        stmt = (
            pg_insert(Concept)
            .values(
                id=uuid7(),
                operator_id=data.operator_id,
                canonical_name=data.canonical_name,
                definition=data.definition,
                domain=data.domain,
                confidence=data.confidence,
            )
            .on_conflict_do_update(
                constraint="uq_concepts_operator_name",
                set_={
                    "definition": data.definition,
                    "domain": data.domain,
                    "confidence": data.confidence,
                    "source_count": Concept.source_count + 1,
                },
            )
            .returning(Concept)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    async def list_concepts(
        self, operator_id: _uuid.UUID, limit: int = 100
    ) -> list[Concept]:
        stmt = (
            select(Concept)
            .where(Concept.operator_id == operator_id)
            .order_by(Concept.canonical_name)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_mechanism(self, data: MechanismCreate) -> Mechanism:
        mechanism = Mechanism(
            id=uuid7(),
            operator_id=data.operator_id,
            name=data.name,
            description=data.description,
            causal_logic=data.causal_logic,
            domain=data.domain,
            confidence=data.confidence,
        )
        self._session.add(mechanism)
        await self._session.flush()
        return mechanism

    async def create_tradeoff(self, data: TradeoffCreate) -> Tradeoff:
        tradeoff = Tradeoff(
            id=uuid7(),
            operator_id=data.operator_id,
            name=data.name,
            pole_a=data.pole_a,
            pole_b=data.pole_b,
            description=data.description,
            domain=data.domain,
        )
        self._session.add(tradeoff)
        await self._session.flush()
        return tradeoff

    async def create_failure_mode(self, data: FailureModeCreate) -> FailureMode:
        failure_mode = FailureMode(
            id=uuid7(),
            operator_id=data.operator_id,
            name=data.name,
            description=data.description,
            early_signals=data.early_signals,
            domain=data.domain,
            severity=data.severity,
        )
        self._session.add(failure_mode)
        await self._session.flush()
        return failure_mode

    async def create_heuristic(self, data: HeuristicCreate) -> Heuristic:
        heuristic = Heuristic(
            id=uuid7(),
            operator_id=data.operator_id,
            statement=data.statement,
            domain=data.domain,
            applicability=data.applicability,
            failure_conditions=data.failure_conditions,
            confidence=data.confidence,
        )
        self._session.add(heuristic)
        await self._session.flush()
        return heuristic

    async def create_diagnostic_question(
        self, data: DiagnosticQuestionCreate
    ) -> DiagnosticQuestion:
        question = DiagnosticQuestion(
            id=uuid7(),
            operator_id=data.operator_id,
            question_text=data.question_text,
            question_class=data.question_class,
            domain=data.domain,
            usefulness_score=data.usefulness_score,
        )
        self._session.add(question)
        await self._session.flush()
        return question

    async def create_protocol(self, data: ProtocolCreate) -> Protocol:
        protocol = Protocol(
            id=uuid7(),
            operator_id=data.operator_id,
            protocol_name=data.protocol_name,
            domain=data.domain,
            purpose=data.purpose,
            steps=data.steps,
            applicability=data.applicability,
        )
        self._session.add(protocol)
        await self._session.flush()
        return protocol

    # ------------------------------------------------------------------
    # Lens Packs
    # ------------------------------------------------------------------

    async def create_lens_pack(self, data: LensPackCreate) -> LensPack:
        pack = LensPack(
            id=uuid7(),
            operator_id=data.operator_id,
            name=data.name,
            domain=data.domain,
            description=data.description,
            version=data.version,
            source_basis=data.source_basis,
        )
        self._session.add(pack)
        await self._session.flush()
        return pack

    async def get_lens_pack(self, lens_pack_id: _uuid.UUID) -> LensPack | None:
        return await self._session.get(LensPack, lens_pack_id)

    async def add_lens_pack_item(self, data: LensPackItemCreate) -> LensPackItem:
        item = LensPackItem(
            id=uuid7(),
            lens_pack_id=data.lens_pack_id,
            item_kind=data.item_kind,
            item_id=data.item_id,
            weight=data.weight,
            metadata_=data.metadata_,
        )
        self._session.add(item)
        await self._session.flush()
        return item

    async def list_lens_pack_items(
        self, lens_pack_id: _uuid.UUID
    ) -> list[LensPackItem]:
        stmt = (
            select(LensPackItem)
            .where(LensPackItem.lens_pack_id == lens_pack_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Cases
    # ------------------------------------------------------------------

    async def create_case(self, data: CaseCreate) -> Case:
        case = Case(
            id=uuid7(),
            operator_id=data.operator_id,
            title=data.title,
            case_kind=data.case_kind,
            summary=data.summary,
            outcome=data.outcome,
            lessons=data.lessons,
        )
        self._session.add(case)
        await self._session.flush()
        return case

    # ------------------------------------------------------------------
    # Rules
    # ------------------------------------------------------------------

    async def create_rule(self, data: RuleCreate) -> Rule:
        rule = Rule(
            id=uuid7(),
            operator_id=data.operator_id,
            rule_text=data.rule_text,
            rule_kind=data.rule_kind,
            confidence=data.confidence,
            first_observed_at=data.first_observed_at,
        )
        self._session.add(rule)
        await self._session.flush()
        return rule

    async def update_rule_confidence(
        self,
        rule_id: _uuid.UUID,
        confidence: float,
        increment_evidence: bool = True,
    ) -> Rule | None:
        rule = await self._session.get(Rule, rule_id)
        if rule is None:
            return None
        rule.confidence = confidence  # type: ignore[assignment]
        if increment_evidence:
            rule.evidence_count = rule.evidence_count + 1  # type: ignore[assignment]
        await self._session.flush()
        return rule

    async def list_rules(
        self,
        operator_id: _uuid.UUID,
        active: bool = True,
        limit: int = 100,
    ) -> list[Rule]:
        stmt = (
            select(Rule)
            .where(Rule.operator_id == operator_id)
            .where(Rule.active == active)
            .order_by(Rule.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Patterns
    # ------------------------------------------------------------------

    async def create_pattern(self, data: PatternCreate) -> Pattern:
        pattern = Pattern(
            id=uuid7(),
            operator_id=data.operator_id,
            pattern_name=data.pattern_name,
            description=data.description,
            pattern_kind=data.pattern_kind,
            confidence=data.confidence,
        )
        self._session.add(pattern)
        await self._session.flush()
        return pattern

    async def increment_pattern_recurrence(
        self, pattern_id: _uuid.UUID
    ) -> Pattern | None:
        pattern = await self._session.get(Pattern, pattern_id)
        if pattern is None:
            return None
        pattern.recurrence_count = pattern.recurrence_count + 1  # type: ignore[assignment]
        await self._session.flush()
        return pattern

    async def list_patterns(
        self, operator_id: _uuid.UUID, limit: int = 100
    ) -> list[Pattern]:
        stmt = (
            select(Pattern)
            .where(Pattern.operator_id == operator_id)
            .order_by(Pattern.recurrence_count.desc(), Pattern.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Edges
    # ------------------------------------------------------------------

    async def create_edge(self, data: EdgeCreate) -> Edge:
        edge = Edge(
            id=uuid7(),
            operator_id=data.operator_id,
            src_kind=data.src_kind,
            dst_kind=data.dst_kind,
            src_id=data.src_id,
            dst_id=data.dst_id,
            edge_type=data.edge_type,
            weight=data.weight,
            provenance=data.provenance,
        )
        self._session.add(edge)
        await self._session.flush()
        return edge

    async def get_edges_for_object(
        self,
        operator_id: _uuid.UUID,
        src_kind: str,
        src_id: _uuid.UUID,
        limit: int = 50,
    ) -> list[Edge]:
        stmt = (
            select(Edge)
            .where(Edge.operator_id == operator_id)
            .where(Edge.src_kind == src_kind)
            .where(Edge.src_id == src_id)
            .order_by(Edge.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_edges(
        self, operator_id: _uuid.UUID, limit: int = 100
    ) -> list[Edge]:
        stmt = (
            select(Edge)
            .where(Edge.operator_id == operator_id)
            .order_by(Edge.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
