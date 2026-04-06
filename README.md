# Utopia

Utopia is a private cognitive operating system and judgment refinery.

It is designed for one hard problem:

**continuity failure under state variability**

Most productivity systems assume a stable operator.
Utopia does not.

It assumes attention is non linear, energy changes, context fractures, motivation is unstable, and self interpretation is often distorted by present state.

The system is being built as a backend first architecture that preserves continuity across time, captures evidence about the operator's condition, estimates what is actually happening, and produces the smallest correct next move.

## Core idea

Utopia is not a task manager.

It is a state aware system that tries to answer questions like:

- What state is the operator in right now
- What is actually blocking motion
- What thread matters
- What is the smallest correct move
- How do we preserve re entry across interruptions
- What did reality reveal after action

The architecture is split into bounded contexts that map to different layers of cognition and control.

## Current status

### Foundation
- Python 3.12+
- FastAPI
- SQLAlchemy 2.x async
- Alembic (11 migrations)
- PostgreSQL 16 + pgvector
- Docker Compose local database setup
- environment based config via `pydantic-settings`
- httpx for external API integration

### Database infrastructure
- 11 logical PostgreSQL schemas (`core`, `integration`, `vector_ctrl`, `evidence`, `execution`, `physiology`, `aether`, `reasoning`, `review`, `system`, `vector`)
- 23 shared enum types
- `pgvector` extension enabled

### Implemented slices

All 8 bounded contexts are implemented with the full stack: Alembic migration, ORM models, Pydantic schemas, service layer, and API routes.

#### Core
Root identity tables:
- `core.operators`
- `core.devices`

#### Integration
External integration infrastructure:
- `integration.oauth_connections`
- `integration.permissions`
- `integration.webhook_receipts`

#### Vector control plane
Directional governance, not task storage:
- `vector_ctrl.life_arcs`
- `vector_ctrl.seasons`
- `vector_ctrl.missions`
- `vector_ctrl.threads`
- `vector_ctrl.thread_constraints`
- `vector_ctrl.anti_goals`

Includes ORM models, Pydantic schemas, `VectorService`, API routes.

#### Evidence sensing layer
Captures what is true about the operator's present moment:
- `evidence.subjective_checkins`
- `evidence.behavior_events`
- `evidence.context_snapshots`
- `evidence.derived_features`

Includes ORM models, Pydantic schemas, `EvidenceService`, API routes.

#### Execution core
Closes the continuity loop:
- `execution.state_estimates`
- `execution.blocker_estimates`
- `execution.reentry_artifacts`
- `execution.policy_decisions`
- `execution.traces`

Includes ORM models, Pydantic schemas, `ExecutionService`, API routes.

#### Physiology
WHOOP as a first class subsystem:
- `physiology.whoop_connections`
- `physiology.whoop_body_measurements`
- `physiology.whoop_cycles`
- `physiology.whoop_sleeps`
- `physiology.whoop_recoveries`
- `physiology.whoop_workouts`
- `physiology.physiology_features`
- `physiology.biomarker_panels`

Includes ORM models, Pydantic schemas, `PhysiologyService` (with upsert semantics), API routes, and a fully implemented WHOOP API client with response mappers and sync orchestrator. The `POST /physiology/whoop/sync` endpoint triggers a full data pull from the WHOOP Developer API.

#### Aether
Typed memory and knowledge graph:
- `aether.sources`
- `aether.source_chunks`
- `aether.extractions`
- `aether.concepts`
- `aether.mechanisms`
- `aether.tradeoffs`
- `aether.failure_modes`
- `aether.heuristics`
- `aether.diagnostic_questions`
- `aether.protocols`
- `aether.lens_packs`
- `aether.lens_pack_items`
- `aether.cases`
- `aether.rules`
- `aether.patterns`
- `aether.edges`

Includes ORM models, Pydantic schemas, `AetherService`, API routes.

#### Reasoning
Problem structuring and decision artifacts:
- `reasoning.problems`
- `reasoning.problem_structures`
- `reasoning.interrogations`
- `reasoning.decision_briefs`
- `reasoning.option_paths`
- `reasoning.contradiction_reports`

Includes ORM models, Pydantic schemas, `ReasoningService`, API routes.

#### Review and calibration
The system's immune layer:
- `review.closures`
- `review.review_sessions`
- `review.rule_promotions`
- `review.pattern_updates`
- `review.calibration_records`

Includes ORM models, Pydantic schemas, `ReviewService`, API routes.

#### System audit
AI orchestration and audit trail:
- `system.model_providers`
- `system.model_runs`
- `system.retrieval_runs`
- `system.event_log`
- `system.outbox_events`

Includes ORM models, Pydantic schemas, `SystemAuditService` (with outbox state management), API routes.

## What is already working

Loop A is structurally present across the full data layer:

**direction -> sensing -> inference -> policy -> re entry -> trace**

The system has persistence and API structure for:

- directional hierarchy (life arcs, seasons, missions, threads, anti goals)
- sensing the present moment (subjective checkins, behavior events, context snapshots)
- estimating state and blockers
- storing policy decisions with full traceability
- preserving re entry artifacts
- recording what happened after action (traces)
- physiology data ingestion from WHOOP (cycles, sleep, recovery, workouts)
- typed knowledge and memory (Aether graph with 16 entity types)
- problem structuring and decision artifacts
- review sessions with rule promotions and calibration records
- full AI orchestration audit trail (model runs, retrieval runs, event log)

All 8 bounded contexts are complete with 60+ ORM models, 11 Alembic migrations, 8 service classes, and 70+ API endpoints.

## What is not built yet

### Vector search
- embeddings for Aether entities
- semantic retrieval via pgvector
- materialized views for current state and active focus

### AI Fabric
Planned reasoning modules:
- router
- state estimator
- blocker classifier
- problem structurer
- context retriever
- physiology interpreter
- contradiction checker
- council
- policy selector

These modules will consume evidence and produce inference artifacts (state estimates, blocker estimates, policy decisions) through the existing Execution and Reasoning schemas.

## Architecture philosophy

Utopia is built around a few core principles.

### 1. State before planning
The problem is not "I forgot the task."
The problem is often that the operator is in the wrong state for the depth of action being demanded.

### 2. Evidence before narrative
The system should not trust self interpretation by default.
It should compare subjective reports, behavior, context, and later physiology.

### 3. Direction before motion
Threads only make sense relative to missions, seasons, and life arcs.
Without direction, motion becomes drift.

### 4. Re entry is a first class object
Interruptions are not edge cases.
They are normal.
A serious system must preserve continuity explicitly.

### 5. Judgment compounds
Over time, the system should become better at recognizing patterns, promoting rules, calibrating interpretation, and preserving what improves future decisions.

## Repository structure

A simplified view of the current layout:

```text
migrations/
  versions/
    001_create_schemas_and_enums.py
    002_core_operators_and_devices.py
    003_integration_tables.py
    004_vector_ctrl_tables.py
    005_evidence_tables.py
    006_execution_tables.py
    007_physiology_tables.py
    008_aether_tables.py
    009_reasoning_tables.py
    010_review_tables.py
    011_system_audit_tables.py

src/utopia/
  api/
    app.py
    deps.py
    routes/
      vector.py
      evidence.py
      execution.py
      physiology.py
      aether.py
      reasoning.py
      review.py
      system_audit.py
  models/
    core.py
    integration.py
    vector_ctrl.py
    evidence.py
    execution.py
    physiology.py
    aether.py
    reasoning.py
    review.py
    system_audit.py
  schemas/
    vector_ctrl.py
    evidence.py
    execution.py
    physiology.py
    aether.py
    reasoning.py
    review.py
    system_audit.py
  services/
    vector_service.py
    evidence_service.py
    execution_service.py
    physiology_service.py
    aether_service.py
    reasoning_service.py
    review_service.py
    system_audit_service.py
  integrations/
    whoop/
      client.py
      mapper.py
      sync.py
  ai/
  config.py
  db.py
  enums.py
```
