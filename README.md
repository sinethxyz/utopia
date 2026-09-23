# Neurocognitive System

> **Historical codename: Utopia**  
> **Status: historical / inactive / preserved**

Neurocognitive System was an experimental, backend-first architecture for state-aware cognitive control.

It was built around one assumption:

**the operator is not stable.**

Attention changes. Energy changes. Context disappears. Re-entry has a cost. Present-state narratives can be wrong. A system that assumes a permanently consistent operator will eventually recommend the wrong thing at the wrong depth.

The experiment asked whether software could preserve continuity by maintaining explicit models of direction, evidence, state, blockers, policy, action, outcome, and calibration.

Its central loop was:

```text
Direction
   ↓
Evidence
   ↓
State + Blocker Estimate
   ↓
Policy
   ↓
Action / Re-entry
   ↓
Trace
   ↓
Review / Calibration
   ↺
```

The project is no longer actively developed as a product.

It remains public because several architectural ideas explored here continued to recur in later systems.

**The implementation is historical. The questions were not.**

---

## The problem

Most productivity software assumes a relatively stable operator.

If the correct task is visible, the user can execute it.

If context is lost, they can reload it.

If they stop moving, the problem is assumed to be motivation, planning, or discipline.

This system explored a different model.

The failure may be one of continuity.

The operator may still know what matters in the abstract while temporarily losing access to the context, state, energy, or cognitive depth required to act on it.

That produces a different set of questions:

- What direction actually matters right now?
- What evidence describes the operator's current condition?
- What state is the operator in?
- What is actually blocking motion?
- What action depth is appropriate for that state?
- What is the smallest correct next move?
- How can interrupted work be re-entered without reconstructing everything?
- What did reality reveal after the action?
- Was the system's previous estimate actually correct?

The goal was not to maximize visible activity.

The goal was to preserve direction and choose the smallest defensible move given the available evidence.

---

## Not a task manager

Neurocognitive System was not designed as a conventional productivity application.

It was not primarily:

- a to-do list
- a note-taking system
- a mood tracker
- a habit app
- a diary
- a generic second brain
- a chatbot over personal data

The architecture treated cognition and execution as a control problem.

A recommendation was not supposed to be the end of the loop.

It was a **claim** about what the operator should do next.

That claim could later be compared with the outcome.

```text
observation → inference → intervention → outcome → calibration
```

That feedback loop is the important part.

---

## Architecture

The repository separates the system into bounded contexts rather than storing everything inside generic notes or chat history.

### Vector

Directional control.

Vector models what matters across different horizons:

```text
life arc → season → mission → thread
```

It exists to prevent motion from being mistaken for progress.

### Evidence

The sensing layer.

It captures subjective, behavioral, contextual, and derived evidence about the operator's present condition.

The governing principle was:

**evidence before narrative.**

The system should not automatically treat a present-state self-interpretation as ground truth.

### Physiology

A physiological evidence channel.

The implementation includes WHOOP ingestion for cycles, sleep, recovery, workouts, body measurements, and derived physiology features.

Physiological data was intended to constrain interpretation, not define identity.

### Execution

The action-control layer.

Execution stores:

- state estimates
- blocker estimates
- policy decisions
- re-entry artifacts
- traces

The important chain is:

```text
evidence → inference → policy → outcome
```

A policy decision can be traced back to the estimates that produced it, and a later trace can record what actually happened.

### Re-entry

Interruptions were treated as normal rather than exceptional.

A re-entry artifact preserves enough state to restart a thread without reconstructing the entire problem:

- last completed step
- unresolved edge
- smallest next move
- trap to avoid
- relevant context

Re-entry was modeled as a first-class object because continuity loss was considered part of the system, not an edge case.

### Aether

Typed memory and knowledge.

Aether was designed to preserve reusable cognitive objects rather than accumulate an undifferentiated archive.

Its model includes concepts such as:

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
- explicit edges between them

The intention was to make memory useful for future judgment rather than merely searchable.

### Reasoning

Structured problem representation.

The reasoning layer stores artifacts such as:

- problems
- problem structures
- interrogations
- decision briefs
- option paths
- contradiction reports

The underlying idea was that the system should improve the shape of the problem before rushing to solve it.

### Review and Calibration

The system's correction layer.

Review stores:

- closures
- review sessions
- rule promotions
- pattern updates
- calibration records

Calibration records were designed to compare earlier estimates with later outcomes.

That makes it possible, at least architecturally, for the system to ask:

**Was my previous interpretation actually accurate?**

### System Audit

The AI and retrieval audit layer records model runs, retrieval runs, events, and outbox state so that reasoning does not disappear into an opaque chat transcript.

---

## AI Fabric

The implementation contains nine reasoning modules.

### Core execution pipeline

- **State Estimator** — estimates the operator's current operating state.
- **Blocker Classifier** — identifies the dominant reason motion is failing.
- **Policy Selector** — chooses an intervention and action depth appropriate to the estimated state.

### Extended reasoning

- **Router** — classifies incoming intent and chooses the appropriate reasoning path.
- **Problem Structurer** — turns raw problems into explicit objectives, constraints, unknowns, assumptions, and bottlenecks.
- **Context Retriever** — retrieves relevant material from the typed knowledge graph.
- **Physiology Interpreter** — translates physiological signals into bounded capacity information.
- **Contradiction Checker** — compares narrative against behavior, physiology, direction, and temporal patterns.
- **Council** — runs multiple reasoning lenses and synthesizes agreement and tension.

Claude is used as the reasoning backend for these modules. OpenAI embeddings are used for semantic retrieval.

The model layer was intended to remain subordinate to the typed system around it.

---

## What was actually built

This repository is more than an architecture document.

The historical implementation includes:

- Python 3.12+
- FastAPI
- SQLAlchemy 2.x async
- PostgreSQL 16
- pgvector
- Alembic
- 13 database migrations
- typed ORM models and Pydantic schemas
- bounded service layers
- API routes across the major contexts
- WHOOP API client, mapping, and synchronization
- semantic vector search
- Claude-backed reasoning modules
- OpenAI embedding support
- system-level model/retrieval audit records
- three materialized views for current state, active focus, and thread priority
- service, reasoning-module, and API-route tests

The major bounded contexts represented in code are:

```text
core
integration
vector_ctrl
evidence
execution
physiology
aether
reasoning
review
system
vector
```

---

## Implementation vs. architecture

The architecture documents in this repository describe a larger intended system than the implementation reached.

That distinction is deliberate.

Some ideas were implemented deeply enough to have migrations, models, services, routes, and tests.

Others remained design directions.

The documents are preserved because they show the evolution of the system's reasoning, but they should not be read as claims that every proposed subsystem became a finished product.

There is no attempt here to rewrite the historical record into a cleaner story than it was.

---

## Architectural principles

Several ideas mattered more than any individual feature.

### State before planning

The correct next action depends on the state of the operator executing it.

### Evidence before narrative

Self-interpretation is evidence, not unquestionable truth.

### Direction before motion

Activity is not inherently progress.

### Re-entry as a first-class object

A system designed for interruption should preserve the minimum state required to resume.

### Typed memory over accumulation

If everything is a note, the system loses semantic structure.

### Explicit confidence and provenance

Inferred state should remain distinguishable from observed fact.

### Outcomes over persuasive explanations

A recommendation that sounds intelligent is still only a hypothesis until reality answers.

### Calibration over permanent assumptions

The system should be able to compare previous estimates with subsequent outcomes and update accordingly.

### Separation of observation, judgment, and execution

Sensing reality, interpreting reality, and acting on reality are different operations and should remain inspectable.

---

## Why preserve this repository?

Neurocognitive System is not the architecture I would build unchanged today.

That is part of its value.

It preserves an earlier attempt to formalize several problems that continued to matter:

- continuity across interrupted work
- explicit system state
- evidence-backed inference
- re-entry cost
- typed memory
- confidence and provenance
- contradiction detection
- action selection under variable capacity
- outcome traces
- calibration
- review as a correction mechanism

Looking backward, the vocabulary changed more than the underlying questions.

The repository is useful as architecture archaeology: a record of how those ideas were represented before later systems refined them.

**The implementation is historical. The questions were not.**

---

## Historical terminology

Some names in the code and architecture documents are preserved because they were part of the original system.

- **Utopia** — original project codename
- **Vector** — directional control plane
- **Aether** — typed knowledge and memory
- **Schrödinger** — original name for the policy-selection / "one correct move" concept

These names should be read as historical terminology, not as a recommendation for how the same primitives would necessarily be named today.

---

## Repository structure

```text
migrations/
  versions/                 # 13 historical Alembic migrations

src/utopia/
  api/                      # FastAPI application and routes
  models/                   # SQLAlchemy domain models
  schemas/                  # Pydantic request/response contracts
  services/                 # bounded-context service layer
  integrations/
    whoop/                  # WHOOP client, mapping, sync
  ai/                       # reasoning modules and providers
  config.py
  db.py
  enums.py

tests/
  conftest.py
  test_services.py
  test_ai_modules.py
  test_routes.py

docs/
  adhd-visual-prosthetic-thesis.md

Utopia Architecture.md
Utopia Formal Architecture DB etc.md
```

---

## Local setup

This is a historical repository, so setup instructions are preserved primarily for inspection and experimentation.

### Requirements

- Python 3.12+
- Docker / Docker Compose
- PostgreSQL 16 with pgvector

### Environment

Copy the example environment file and provide only the integrations you intend to use:

```bash
cp .env.example .env
```

Available configuration includes PostgreSQL, WHOOP, Anthropic, and OpenAI credentials.

### Database

```bash
docker compose up -d
alembic upgrade head
```

### Development

Install the project and run the test suite using the configuration in `pyproject.toml`.

---

## Status

**Historical / inactive / preserved.**

There is no active product roadmap for this repository.

Parts of the architecture may be extracted, rewritten, or reappear elsewhere, but this repository represents the system as it existed during this experiment.

It is preserved as evidence of the design process, including ideas that worked, ideas that did not, and primitives that survived into later thinking.

**The implementation is historical. The questions were not.**
