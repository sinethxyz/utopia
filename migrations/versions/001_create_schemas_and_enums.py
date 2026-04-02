"""M001: create schemas and enum types.

All 10 logical schemas from the architecture plus pgvector extension.
Enum types map to utopia/enums.py.

Revision ID: 001
Revises: None
"""
from typing import Sequence, Union

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- Schemas ---
SCHEMAS = [
    "core",
    "integration",
    "vector_ctrl",
    "evidence",
    "physiology",
    "aether",
    "reasoning",
    "execution",
    "system",
    "vector",
]

# --- Enum definitions: (schema-qualified name, values) ---
ENUMS = [
    ("core.status", [
        "active", "paused", "completed", "abandoned", "archived", "dormant",
    ]),
    ("core.season_status", [
        "planned", "active", "closed",
    ]),
    ("core.thread_status", [
        "active", "blocked", "paused", "closed",
    ]),
    ("core.state_kind", [
        "recover", "preserve", "orient", "clarify", "reenter",
        "execute", "deep_work", "close_loop", "review", "drift",
    ]),
    ("core.blocker_kind", [
        "ambiguity", "scope_overload", "physiological_depletion",
        "emotional_threat", "context_fracture", "vector_conflict",
        "environmental_friction", "stimulation_hijack", "narrative_distortion",
        "completion_aversion", "problem_misclassification", "decision_fog",
    ]),
    ("core.source_kind", [
        "book", "paper", "essay", "transcript", "note_bundle", "case_file",
    ]),
    ("core.memory_class", [
        "constitutional", "directional", "conceptual", "procedural",
        "episodic", "calibration", "physiological_calibration",
    ]),
    ("core.evidence_kind", [
        "subjective", "behavioral", "contextual", "physiological",
        "external_knowledge",
    ]),
    ("core.intervention_kind", [
        "recover", "preserve", "orient", "reenter", "clarify",
        "ask", "execute", "close_loop", "review",
    ]),
    ("core.action_depth", [
        "tiny", "narrow", "moderate", "deep",
    ]),
    ("core.decision_kind", [
        "strategic", "technical", "social", "legal", "execution", "personal",
    ]),
    ("core.mission_kind", [
        "strategic", "technical", "personal", "recovery", "exploratory",
    ]),
    ("core.thread_kind", [
        "build", "research", "decision", "admin", "recovery",
    ]),
    ("core.constraint_hardness", [
        "hard", "soft", "assumed",
    ]),
    ("core.oauth_status", [
        "active", "revoked", "expired",
    ]),
    ("core.score_state", [
        "SCORED", "PENDING_SCORE", "UNSCORABLE",
    ]),
    ("core.trace_kind", [
        "action", "question", "preserve", "recovery", "closure",
    ]),
    ("core.review_scope", [
        "micro", "daily", "weekly", "monthly",
    ]),
    ("core.closure_type", [
        "complete", "archive", "pause", "merge",
    ]),
    ("core.processing_status", [
        "pending", "processed", "failed",
    ]),
    ("core.edge_type", [
        "supports", "contradicts", "applies_to", "predicts",
        "resembles", "causes", "prevents", "corrected_by",
    ]),
    ("core.rule_kind", [
        "execution", "reasoning", "physiology", "strategic", "personal",
    ]),
    ("core.pattern_kind", [
        "blocker", "timing", "physiology", "narrative", "execution",
    ]),
]


def upgrade() -> None:
    # Create pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create schemas
    for schema in SCHEMAS:
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # Create enum types
    for enum_name, values in ENUMS:
        values_sql = ", ".join(f"'{v}'" for v in values)
        op.execute(f"CREATE TYPE {enum_name} AS ENUM ({values_sql})")


def downgrade() -> None:
    # Drop enum types in reverse
    for enum_name, _ in reversed(ENUMS):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

    # Drop schemas in reverse
    for schema in reversed(SCHEMAS):
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")

    op.execute("DROP EXTENSION IF EXISTS vector")
