# # Utopia

Utopia is a private cognitive operating system and judgment refinery.

It is designed for one hard problem:

**continuity failure under state variability**

Most productivity systems assume a stable operator.
Utopia does not.

It assumes attention is non linear, energy changes, context fractures, motivation is unstable, and self interpretation is often distorted by present state.

The system is being built as a backend first architecture that preserves continuity across time, captures evidence about the operator’s condition, estimates what is actually happening, and produces the smallest correct next move.

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

Implemented on `main`:

### Foundation
- Python 3.12+
- FastAPI
- SQLAlchemy 2.x async
- Alembic
- PostgreSQL 16 + pgvector
- Docker Compose local database setup
- environment based config via `pydantic-settings`

### Database infrastructure
- 10 logical PostgreSQL schemas
- 23 shared enum types
- `pgvector` extension enabled

### Implemented slices

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
- `life_arcs`
- `seasons`
- `missions`
- `threads`
- `thread_constraints`
- `anti_goals`

Includes:
- ORM models
- Pydantic schemas
- `VectorService`
- API routes

#### Evidence sensing layer
Captures what is true about the operator’s present moment:
- `subjective_checkins`
- `behavior_events`
- `context_snapshots`
- `derived_features`

Includes:
- ORM models
- Pydantic schemas
- `EvidenceService`
- API routes

#### Execution core
Closes the continuity loop:
- `state_estimates`
- `blocker_estimates`
- `reentry_artifacts`
- `policy_decisions`
- `traces`

Includes:
- ORM models
- Pydantic schemas
- `ExecutionService`
- API routes

## What is already working conceptually

Loop A is structurally present:

**direction -> sensing -> inference -> policy -> re entry -> trace**

That means the repo already has persistence and API structure for:

- directional hierarchy
- sensing the present moment
- estimating state
- estimating blockers
- storing a policy decision
- preserving a re entry artifact
- recording what happened after action

## What is not built yet

The repo is not yet the full Utopia architecture.

Major planned slices still remaining include:

### Physiology
WHOOP as a first class subsystem:
- body metrics
- recovery
- sleep
- cycles
- workouts
- physiology features

### Aether
Typed memory and knowledge graph:
- sources
- chunks
- extractions
- concepts
- mechanisms
- tradeoffs
- protocols
- rules
- patterns
- edges

### Reasoning
Problem structuring and decision artifacts:
- problems
- problem structures
- interrogations
- decision briefs
- option paths
- contradiction reports

### Review and calibration
The system’s immune layer:
- closures
- review sessions
- rule promotions
- pattern updates
- calibration records

### System audit layer
AI orchestration and audit trail:
- model providers
- model runs
- retrieval runs
- event log
- outbox events

### Vector search
- embeddings
- semantic retrieval
- materialized views for current state and active focus

### AI Fabric
Planned reasoning modules such as:
- router
- state estimator
- blocker classifier
- problem structurer
- context retriever
- physiology interpreter
- contradiction checker
- council
- policy selector

## Architecture philosophy

Utopia is built around a few core principles.

### 1. State before planning
The problem is not “I forgot the task.”
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

src/utopia/
  api/
    app.py
    deps.py
    routes/
      vector.py
      evidence.py
      execution.py
  models/
    core.py
    integration.py
    vector_ctrl.py
    evidence.py
    execution.py
  schemas/
    vector_ctrl.py
    evidence.py
    execution.py
  services/
    vector_service.py
    evidence_service.py
    execution_service.py
  ai/
  integrations/
    whoop/
