# Neurocognitive System

> **Historical codename: Utopia**  
> **Status: historical / inactive / preserved**

Neurocognitive System is a historical experiment in **multimodal cognitive-state estimation, continuity, reasoning, and adaptive control**.

It began from one assumption:

**the operator is not stable.**

Attention changes. Energy changes. Context disappears. Re-entry has a cost. Self-report is useful but imperfect. Physiological and behavioral signals are useful but imperfect. The intended architecture was therefore not a task manager or an AI that simply "knows" the user.

It was a system for maintaining explicit, testable hypotheses about the operator's current state and deciding what depth of action was appropriate.

```text
Direction
    ↓
Sensing
    ↓
Observations
    ↓
Features
    ↓
Evidence
    ↓
Inference
    ↓
Policy
    ↓
Action / Re-entry
    ↓
Outcome
    ↓
Calibration
    ↺
```

**The implementation is historical. The questions were not.**

---

## What this repository contains

The historical implementation includes:

- Python 3.12+
- FastAPI
- PostgreSQL 16 + pgvector
- SQLAlchemy + Alembic
- 13 database migrations
- typed ORM and Pydantic models
- directional hierarchy: life arcs → seasons → missions → threads
- subjective, behavioral, contextual, and derived evidence
- WHOOP ingestion for sleep, recovery, cycles, workouts, and body measurements
- state estimation, blocker classification, and policy selection
- typed memory and semantic retrieval
- structured problem reasoning
- re-entry artifacts and execution traces
- review and calibration records
- model/retrieval audit data models
- materialized read models
- service, AI-module, and API tests

The Python package remains named `utopia` so the historical implementation stays intact.

---

## Multimodal intent

WHOOP was the first implemented external sensor, not the intended endpoint.

The longer-term design was sensor-agnostic. It was meant to accept additional evidence sources such as:

- behavioral telemetry
- environment/context sensors
- additional wearables
- biomarkers
- neurophysiological interfaces such as EEG devices, including systems in the class of Neurosity

The goal was **not** to make any sensor authoritative.

The intended model was:

```text
imperfect sensor
    ↓
observation
    ↓
derived feature
    ↓
evidence
    ↓
state hypothesis
    ↓
policy
    ↓
outcome
    ↓
calibration
```

A future EEG integration would therefore contribute observations or derived features. It would not directly declare a cognitive state or diagnosis.

---

## Architecture

The cleaned architecture is documented in:

- [Architecture overview](docs/architecture/overview.md)
- [RFC-0001: Neurocognitive System](docs/rfcs/RFC-0001-neurocognitive-system.md)
- [RFC-0002: Observation, Evidence, and Inference](docs/rfcs/RFC-0002-observation-evidence-inference.md)
- [Historical terminology](docs/history/terminology.md)
- [Static codebase audit](docs/audit/2026-09-23.md)

The original Utopia documents are preserved unchanged under [docs/history](docs/history/README.md).

---

## Core primitives

### Direction

Historical name: **Vector**.

Direction represents what matters:

```text
life arc → season → mission → thread
```

It exists to distinguish useful motion from drift.

### Sensing and Evidence

The system records subjective, behavioral, contextual, and physiological signals.

The cleaned architecture separates:

**observation ≠ evidence ≠ inference**

A measurement is not automatically a conclusion.

### Inference

The historical AI Fabric estimates things such as:

- current operating state
- dominant blocker
- contradictions between narrative and evidence

Inference should remain explicit about confidence, provenance, and failure.

### Policy

Historical name: **Schrödinger**.

Policy selects an intervention and action depth based on available evidence and inferred state.

A policy decision is a hypothesis about what to try next, not ground truth.

### Re-entry

Interrupted work is treated as normal.

A re-entry artifact preserves:

- last completed step
- unresolved edge
- smallest next move
- trap to avoid
- relevant context
- freshness

### Memory

Historical name: **Aether**.

The system stores typed cognitive objects rather than treating all memory as notes:

- concepts
- mechanisms
- trade-offs
- failure modes
- heuristics
- diagnostic questions
- protocols
- cases
- rules
- patterns
- explicit graph edges

### Feedback and Calibration

The historical implementation records traces, reviews, rule promotions, pattern updates, and calibration records.

The intended end-state was a real feedback loop:

```text
prediction → action → outcome → error → reliability update
```

The historical code models this loop more completely than it executes it.

---

## What is implemented vs. what was intended

This repository intentionally distinguishes implementation from architecture.

### Implemented

Substantial backend/domain infrastructure exists for:

- Direction / Vector
- Evidence
- Execution
- Physiology
- Aether
- Reasoning
- Review
- System Audit
- vector search
- WHOOP ingestion
- AI reasoning modules

### Incomplete or architectural

Examples include:

- a complete authentication/authorization boundary
- automatic model/retrieval audit wiring
- a full encrypted OAuth/token lifecycle
- automatic materialized-view refresh
- calibration automatically changing future model/rule weighting
- the complete cross-domain control loop
- general sensor-adapter abstractions
- EEG / Neurosity integration

These are documented as unfinished rather than presented as completed features.

---

## Trust boundary

**Do not expose the historical API directly to an untrusted network.**

The current implementation was built as private prototype software and does not contain a complete authentication and authorization boundary.

See [SECURITY.md](SECURITY.md).

---

## Medical boundary

Neurocognitive System is **not a medical diagnostic system**.

Physiological or future neurophysiological inputs are treated as imperfect evidence about operational state and usable capacity. They are not a basis for diagnosing medical or psychiatric conditions.

---

## Repository layout

```text
src/utopia/
  api/                 # historical FastAPI surface
  models/              # SQLAlchemy domain model
  schemas/             # Pydantic contracts
  services/            # bounded-context services
  integrations/whoop/  # implemented sensor integration
  ai/                  # historical reasoning runtime

migrations/
  versions/            # 13 historical migrations

docs/
  architecture/        # cleaned architecture
  rfcs/                # redesign contracts
  audit/               # static audit record
  history/             # original Utopia design material
  adhd-visual-prosthetic-thesis.md

tests/
  test_services.py
  test_ai_modules.py
  test_routes.py
```

---

## Local inspection

This repository is preserved primarily for architecture inspection and experimentation.

```bash
cp .env.example .env
docker compose up -d
pip install -e ".[dev]"
alembic upgrade head
pytest
```

Provider keys are optional unless exercising the corresponding external integrations.

---

## Status

There is no active product roadmap for the historical Utopia application.

The cleanup exists to expose the durable architectural primitives without rewriting the prototype into something it never was.

**The implementation is historical. The questions were not.**
