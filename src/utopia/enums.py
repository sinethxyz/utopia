"""Shared enum types for the Utopia cognitive architecture.

These map 1:1 to PostgreSQL enum types created in migration M001.
Derived from Utopia Formal Architecture DB etc.md sections 4 and 18.
"""

import enum


class Status(str, enum.Enum):
    """General lifecycle status for canonical entities."""

    active = "active"
    paused = "paused"
    completed = "completed"
    abandoned = "abandoned"
    archived = "archived"
    dormant = "dormant"


class SeasonStatus(str, enum.Enum):
    planned = "planned"
    active = "active"
    closed = "closed"


class ThreadStatus(str, enum.Enum):
    active = "active"
    blocked = "blocked"
    paused = "paused"
    closed = "closed"


class StateKind(str, enum.Enum):
    """Operator state — output of the State Estimator."""

    recover = "recover"
    preserve = "preserve"
    orient = "orient"
    clarify = "clarify"
    reenter = "reenter"
    execute = "execute"
    deep_work = "deep_work"
    close_loop = "close_loop"
    review = "review"
    drift = "drift"


class BlockerKind(str, enum.Enum):
    """Why motion is failing — output of the Blocker Classifier."""

    ambiguity = "ambiguity"
    scope_overload = "scope_overload"
    physiological_depletion = "physiological_depletion"
    emotional_threat = "emotional_threat"
    context_fracture = "context_fracture"
    vector_conflict = "vector_conflict"
    environmental_friction = "environmental_friction"
    stimulation_hijack = "stimulation_hijack"
    narrative_distortion = "narrative_distortion"
    completion_aversion = "completion_aversion"
    problem_misclassification = "problem_misclassification"
    decision_fog = "decision_fog"


class SourceKind(str, enum.Enum):
    """Type of knowledge source ingested into Aether."""

    book = "book"
    paper = "paper"
    essay = "essay"
    transcript = "transcript"
    note_bundle = "note_bundle"
    case_file = "case_file"


class MemoryClass(str, enum.Enum):
    """Aether memory classification."""

    constitutional = "constitutional"
    directional = "directional"
    conceptual = "conceptual"
    procedural = "procedural"
    episodic = "episodic"
    calibration = "calibration"
    physiological_calibration = "physiological_calibration"


class EvidenceKind(str, enum.Enum):
    """Evidence plane signal types."""

    subjective = "subjective"
    behavioral = "behavioral"
    contextual = "contextual"
    physiological = "physiological"
    external_knowledge = "external_knowledge"


class InterventionKind(str, enum.Enum):
    """Action types that Schrodinger can select."""

    recover = "recover"
    preserve = "preserve"
    orient = "orient"
    reenter = "reenter"
    clarify = "clarify"
    ask = "ask"
    execute = "execute"
    close_loop = "close_loop"
    review = "review"


class ActionDepth(str, enum.Enum):
    """How deep the recommended action should go."""

    tiny = "tiny"
    narrow = "narrow"
    moderate = "moderate"
    deep = "deep"


class DecisionKind(str, enum.Enum):
    """Classification of decision artifacts."""

    strategic = "strategic"
    technical = "technical"
    social = "social"
    legal = "legal"
    execution = "execution"
    personal = "personal"


class MissionKind(str, enum.Enum):
    strategic = "strategic"
    technical = "technical"
    personal = "personal"
    recovery = "recovery"
    exploratory = "exploratory"


class ThreadKind(str, enum.Enum):
    build = "build"
    research = "research"
    decision = "decision"
    admin = "admin"
    recovery = "recovery"


class ConstraintHardness(str, enum.Enum):
    hard = "hard"
    soft = "soft"
    assumed = "assumed"


class OAuthStatus(str, enum.Enum):
    active = "active"
    revoked = "revoked"
    expired = "expired"


class ScoreState(str, enum.Enum):
    """WHOOP score state."""

    scored = "SCORED"
    pending_score = "PENDING_SCORE"
    unscorable = "UNSCORABLE"


class TraceKind(str, enum.Enum):
    action = "action"
    question = "question"
    preserve = "preserve"
    recovery = "recovery"
    closure = "closure"


class ReviewScope(str, enum.Enum):
    micro = "micro"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class ClosureType(str, enum.Enum):
    complete = "complete"
    archive = "archive"
    pause = "pause"
    merge = "merge"


class ProcessingStatus(str, enum.Enum):
    pending = "pending"
    processed = "processed"
    failed = "failed"


class EdgeType(str, enum.Enum):
    """Explicit conceptual relation types for the graph layer."""

    supports = "supports"
    contradicts = "contradicts"
    applies_to = "applies_to"
    predicts = "predicts"
    resembles = "resembles"
    causes = "causes"
    prevents = "prevents"
    corrected_by = "corrected_by"


class RuleKind(str, enum.Enum):
    execution = "execution"
    reasoning = "reasoning"
    physiology = "physiology"
    strategic = "strategic"
    personal = "personal"


class PatternKind(str, enum.Enum):
    blocker = "blocker"
    timing = "timing"
    physiology = "physiology"
    narrative = "narrative"
    execution = "execution"
