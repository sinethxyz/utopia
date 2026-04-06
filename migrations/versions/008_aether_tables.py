"""M008: aether tables — typed memory and knowledge graph.

Aether is the extracted intelligence layer. It stores knowledge atoms
(concepts, mechanisms, tradeoffs, heuristics, protocols, rules, patterns)
extracted from sources, plus a polymorphic edge graph for relating them.

Aether enables Loop B: judgment and strategic reasoning by giving the
AI Fabric structured access to what the operator has learned.

Matches: Utopia Formal Architecture DB etc.md section 13.

Revision ID: 008
Revises: 007
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- sources ---
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("source_kind", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("author", sa.Text(), nullable=True),
        sa.Column("published_at", sa.Date(), nullable=True),
        sa.Column("ingest_status", sa.Text(), nullable=False),
        sa.Column("canonical_uri", sa.Text(), nullable=True),
        sa.Column("storage_uri", sa.Text(), nullable=True),
        sa.Column("checksum", sa.Text(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_sources_operator_created",
        "sources", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- source_chunks ---
    op.create_table(
        "source_chunks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("aether.sources.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("semantic_label", sa.Text(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=True),
        schema="aether",
    )
    op.create_index(
        "ix_aether_source_chunks_source_id",
        "source_chunks", ["source_id"],
        schema="aether",
    )

    # --- extractions ---
    op.create_table(
        "extractions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("aether.sources.id"), nullable=False),
        sa.Column("extraction_version", sa.Text(), nullable=False),
        sa.Column("extraction_status", sa.Text(), nullable=False),
        sa.Column("thesis", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("model_run_id", sa.Uuid(), nullable=True),
        sa.UniqueConstraint("source_id", "extraction_version", name="uq_extractions_source_version"),
        schema="aether",
    )
    op.create_index(
        "ix_aether_extractions_source_id",
        "extractions", ["source_id"],
        schema="aether",
    )

    # --- concepts ---
    op.create_table(
        "concepts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("canonical_name", sa.Text(), nullable=False),
        sa.Column("definition", sa.Text(), nullable=True),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("operator_id", "canonical_name", name="uq_concepts_operator_name"),
        schema="aether",
    )
    op.create_index(
        "ix_aether_concepts_operator_created",
        "concepts", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- mechanisms ---
    op.create_table(
        "mechanisms",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("causal_logic", sa.Text(), nullable=True),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_mechanisms_operator_created",
        "mechanisms", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- tradeoffs ---
    op.create_table(
        "tradeoffs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("pole_a", sa.Text(), nullable=False),
        sa.Column("pole_b", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_tradeoffs_operator_created",
        "tradeoffs", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- failure_modes ---
    op.create_table(
        "failure_modes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("early_signals", ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column("severity", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_failure_modes_operator_created",
        "failure_modes", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- heuristics ---
    op.create_table(
        "heuristics",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column("applicability", sa.Text(), nullable=True),
        sa.Column("failure_conditions", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_heuristics_operator_created",
        "heuristics", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- diagnostic_questions ---
    op.create_table(
        "diagnostic_questions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_class", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=True),
        sa.Column("usefulness_score", sa.Numeric(6, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_diagnostic_questions_operator_created",
        "diagnostic_questions", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- protocols ---
    op.create_table(
        "protocols",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("protocol_name", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("steps", JSONB(), nullable=False),
        sa.Column("applicability", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_protocols_operator_created",
        "protocols", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- lens_packs ---
    op.create_table(
        "lens_packs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.Text(), nullable=False),
        sa.Column("source_basis", JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_lens_packs_operator_created",
        "lens_packs", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- lens_pack_items ---
    op.create_table(
        "lens_pack_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("lens_pack_id", sa.Uuid(), sa.ForeignKey("aether.lens_packs.id"), nullable=False),
        sa.Column("item_kind", sa.Text(), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("weight", sa.Numeric(6, 3), nullable=True),
        sa.Column("metadata", JSONB(), nullable=True),
        schema="aether",
    )
    op.create_index(
        "ix_aether_lens_pack_items_lens_pack_id",
        "lens_pack_items", ["lens_pack_id"],
        schema="aether",
    )

    # --- cases ---
    op.create_table(
        "cases",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("case_kind", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("lessons", JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_cases_operator_created",
        "cases", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- rules ---
    op.create_table(
        "rules",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("rule_text", sa.Text(), nullable=False),
        sa.Column("rule_kind", sa.Text(), nullable=False),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("first_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_rules_operator_active",
        "rules", ["operator_id", "active"],
        schema="aether",
    )
    op.create_index(
        "ix_aether_rules_operator_created",
        "rules", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- patterns ---
    op.create_table(
        "patterns",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("pattern_name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("pattern_kind", sa.Text(), nullable=False),
        sa.Column("recurrence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_patterns_operator_created",
        "patterns", ["operator_id", sa.text("created_at DESC")],
        schema="aether",
    )

    # --- edges ---
    op.create_table(
        "edges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("operator_id", sa.Uuid(), sa.ForeignKey("core.operators.id"), nullable=False),
        sa.Column("src_kind", sa.Text(), nullable=False),
        sa.Column("dst_kind", sa.Text(), nullable=False),
        sa.Column("src_id", sa.Uuid(), nullable=False),
        sa.Column("dst_id", sa.Uuid(), nullable=False),
        sa.Column("edge_type", sa.Text(), nullable=False),
        sa.Column("weight", sa.Numeric(6, 3), nullable=True),
        sa.Column("provenance", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="aether",
    )
    op.create_index(
        "ix_aether_edges_operator_src",
        "edges", ["operator_id", "src_kind", "src_id"],
        schema="aether",
    )
    op.create_index(
        "ix_aether_edges_operator_dst",
        "edges", ["operator_id", "dst_kind", "dst_id"],
        schema="aether",
    )


def downgrade() -> None:
    op.drop_index("ix_aether_edges_operator_dst", table_name="edges", schema="aether")
    op.drop_index("ix_aether_edges_operator_src", table_name="edges", schema="aether")
    op.drop_table("edges", schema="aether")

    op.drop_index("ix_aether_patterns_operator_created", table_name="patterns", schema="aether")
    op.drop_table("patterns", schema="aether")

    op.drop_index("ix_aether_rules_operator_created", table_name="rules", schema="aether")
    op.drop_index("ix_aether_rules_operator_active", table_name="rules", schema="aether")
    op.drop_table("rules", schema="aether")

    op.drop_index("ix_aether_cases_operator_created", table_name="cases", schema="aether")
    op.drop_table("cases", schema="aether")

    op.drop_index("ix_aether_lens_pack_items_lens_pack_id", table_name="lens_pack_items", schema="aether")
    op.drop_table("lens_pack_items", schema="aether")

    op.drop_index("ix_aether_lens_packs_operator_created", table_name="lens_packs", schema="aether")
    op.drop_table("lens_packs", schema="aether")

    op.drop_index("ix_aether_protocols_operator_created", table_name="protocols", schema="aether")
    op.drop_table("protocols", schema="aether")

    op.drop_index("ix_aether_diagnostic_questions_operator_created", table_name="diagnostic_questions", schema="aether")
    op.drop_table("diagnostic_questions", schema="aether")

    op.drop_index("ix_aether_heuristics_operator_created", table_name="heuristics", schema="aether")
    op.drop_table("heuristics", schema="aether")

    op.drop_index("ix_aether_failure_modes_operator_created", table_name="failure_modes", schema="aether")
    op.drop_table("failure_modes", schema="aether")

    op.drop_index("ix_aether_tradeoffs_operator_created", table_name="tradeoffs", schema="aether")
    op.drop_table("tradeoffs", schema="aether")

    op.drop_index("ix_aether_mechanisms_operator_created", table_name="mechanisms", schema="aether")
    op.drop_table("mechanisms", schema="aether")

    op.drop_index("ix_aether_concepts_operator_created", table_name="concepts", schema="aether")
    op.drop_table("concepts", schema="aether")

    op.drop_index("ix_aether_extractions_source_id", table_name="extractions", schema="aether")
    op.drop_table("extractions", schema="aether")

    op.drop_index("ix_aether_source_chunks_source_id", table_name="source_chunks", schema="aether")
    op.drop_table("source_chunks", schema="aether")

    op.drop_index("ix_aether_sources_operator_created", table_name="sources", schema="aether")
    op.drop_table("sources", schema="aether")
