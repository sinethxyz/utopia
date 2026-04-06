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
- Alembic (12 migrations)
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

All 8 bounded contexts plus Vector Search are complete with 60+ ORM models, 13 Alembic migrations, 9 service classes, and 80+ API endpoints. Nine AI reasoning modules power the full AI Fabric. Three materialized views provide fast access to current state, active focus, and thread priority rankings. A comprehensive test suite covers service layer unit tests, AI module unit tests, and API route integration tests.

#### Vector search
Embedding storage and semantic retrieval via pgvector:
- `vector.embeddings`

Includes ORM model, Pydantic schemas, `VectorSearchService` (with content-hash change detection, batch embedding, cosine similarity search, entity-to-entity similarity), API routes. Powered by OpenAI `text-embedding-3-small` (1536 dimensions) with HNSW index.

### AI Fabric

Nine reasoning modules form the complete AI Fabric:

**Core pipeline (Loop A):**
- **State estimator** — classifies the operator into one of 10 operating states (recover, preserve, orient, clarify, reenter, execute, deep_work, close_loop, review, drift)
- **Blocker classifier** — identifies the dominant blocker from 12 types (ambiguity, scope_overload, physiological_depletion, etc.)
- **Policy selector** — selects an intervention kind and action depth matched to operator capacity

**Extended modules:**
- **Router** — intent classification for incoming operator requests, dispatching to the correct pipeline (assess, structure_problem, retrieve_context, interpret_physiology, check_contradictions, deliberate, etc.)
- **Problem structurer** — decomposes raw problems into structured reasoning artifacts (objective, stakes, actors, constraints, assumptions, unknowns, irreversibilities, bottlenecks, narrative layer, distortion candidates)
- **Context retriever** — RAG over the Aether knowledge graph via vector search, with Claude-powered synthesis of retrieved fragments
- **Physiology interpreter** — translates raw WHOOP data (recovery, sleep, HRV, strain) into actionable capacity signals and action-depth ceilings
- **Contradiction checker** — detects inconsistencies between operator narrative and evidence (narrative_vs_behavior, physiology_vs_claim, vector_vs_action, state_vs_depth, temporal_pattern)
- **Council** — multi-perspective deliberation with 4 lenses (risk analyst, opportunity scout, contrarian, state advisor) and synthesis into consensus/tension points

All modules use Claude as the reasoning backend. The `POST /ai/assess` endpoint orchestrates the core pipeline. Additional endpoints: `POST /ai/route`, `POST /ai/structure-problem`, `POST /ai/retrieve`, `POST /ai/interpret-physiology`, `POST /ai/check-contradictions`, `POST /ai/deliberate`.

### Materialized views

Migration M013 creates three materialized views for fast querying:
- **`execution.mv_current_state`** — latest state estimate, blocker estimate, and policy decision per operator (single row per operator via LATERAL joins)
- **`vector_ctrl.mv_active_focus`** — active season, top-priority mission, and most recent active thread per operator
- **`vector_ctrl.mv_thread_priority`** — ranks all active threads by a composite priority score (mission priority, thread decay, reentry risk, ambiguity)

### Test suite

Comprehensive test coverage across three layers:
- **`tests/conftest.py`** — async fixtures with transactional rollback isolation, service factories, AI module mocks (Claude + embeddings), and FastAPI test client
- **`tests/test_services.py`** — service layer unit tests for Evidence, Execution, and Reasoning services (checkins, state estimates, blocker estimates, policy decisions, traces, reentry artifacts, problems, contradiction reports)
- **`tests/test_ai_modules.py`** — unit tests for all 9 AI modules with mocked Claude responses, including parse failure fallbacks
- **`tests/test_routes.py`** — API route integration tests for health, evidence, execution, and all AI endpoints (assess, route, structure-problem, interpret-physiology, check-contradictions, deliberate)

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
    012_vector_embeddings.py
    013_materialized_views.py

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
      ai.py
      vector_search.py
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
    embedding.py
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
    vector_search_service.py
  integrations/
    whoop/
      client.py
      mapper.py
      sync.py
  ai/
    providers/
      claude.py
      openai_embeddings.py
    assess.py
    state_estimator.py
    blocker_classifier.py
    policy_selector.py
    router.py
    problem_structurer.py
    context_retriever.py
    physiology_interpreter.py
    contradiction_checker.py
    council.py
  config.py
  db.py
  enums.py

tests/
  conftest.py
  test_services.py
  test_ai_modules.py
  test_routes.py
```
