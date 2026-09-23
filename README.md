# Neurocognitive System

> **Historical codename: Utopia**  
> **Status: historical / inactive / preserved**

An early multimodal cognitive-state, continuity, and adaptive-control architecture.

**The operator is not stable.**

Attention changes. Energy changes. Context disappears. Re-entry has a cost. Self-report is noisy. Behavior is noisy. Physiology is noisy. Any future neurophysiology is noisy too.

Utopia explored a system that could form explicit, testable hypotheses about an operator's current cognitive/operational state from multiple imperfect signals, select an appropriate intervention, observe what happened next, and retain the result for later review.

The compressed loop is:

```text
Observation → Evidence → Inference → Policy → Outcome → Calibration
```

**The implementation is historical. The questions were not.**

## In 30 seconds

**What exists:** a Python/FastAPI/PostgreSQL prototype with directional hierarchy, multimodal evidence records, WHOOP ingestion, state/blocker inference, policy selection, re-entry artifacts, typed memory, semantic retrieval, structured reasoning, traces, review/calibration storage, and audit models.

**What does not exist:** production authentication, a complete OAuth lifecycle, automatic calibration learning, complete automatic model/retrieval auditing, a generic sensor-adapter runtime, or EEG/Neurosity integration.

**Why preserve it:** the old implementation already contained durable primitives around state, evidence, continuity, policy, re-entry, auditability, and calibration. The cleanup makes those primitives legible without pretending the prototype became a modern production system.

**Where to look next:**

- [Architecture overview](docs/architecture/overview.md)
- [Implemented vs. intended](#implemented-vs-intended)
- [Historical provenance](docs/history/provenance.md)
- [Original Utopia material](docs/history/README.md)
- [Technical debt / reconstruction boundary](docs/technical-debt.md)
- [Public-release audit](docs/audit/public-release-2026-09-23.md)
- [Release readiness](docs/release-readiness.md)

---

## Architecture

```mermaid
flowchart TD
    D[Direction] --> S[Sensors]

    S --> SUB[Subjective]
    S --> BEH[Behavioral]
    S --> CTX[Contextual]
    S --> PHY["Physiological / WHOOP<br/>IMPLEMENTED"]
    S -.-> EEG["Neurophysiological / EEG<br/>FUTURE / INTENDED"]

    SUB --> O[Observations]
    BEH --> O
    CTX --> O
    PHY --> O
    EEG -.-> O

    O --> F[Features]
    F --> E[Evidence Bundle]
    E --> I["Inference<br/>state · blocker · contradiction"]
    I --> P[Policy]
    P --> A[Action / Re-entry]
    A --> T[Trace / Outcome]
    T --> C[Review / Calibration]
    C --> E

    M["Typed Memory / Reasoning"] -. context .-> I
    T -. learning .-> M
```

The cleaned architectural sequence is:

```text
Direction
→ Sensing
→ Observations
→ Features
→ Evidence
→ Inference
→ Policy
→ Action / Re-entry
→ Outcome
→ Calibration
↺
```

The important boundary is:

**observation ≠ evidence ≠ inference ≠ policy ≠ truth**

A sensor reading is not a conclusion. An inference is a hypothesis. A policy is something to try. An outcome is evidence about whether the earlier hypothesis and policy were useful.

---

## Implemented vs. intended

This table is derived from the preserved code and cleanup audit.

| Capability | Historical status | Notes |
| --- | --- | --- |
| Direction hierarchy | **Implemented** | Life arcs → seasons → missions → threads |
| Subjective evidence | **Implemented** | Check-ins with bounded state signals and free text |
| Behavioral evidence | **Implemented** | Event records such as failed starts and thread switching |
| Context evidence | **Implemented** | Environment, interruptions, available time, active window |
| WHOOP integration | **Implemented** | API client, mapping, sync, and physiology persistence |
| State estimator | **Implemented** | Provider-backed historical inference module |
| Blocker classifier | **Implemented** | Typed blocker hypotheses with confidence/evidence |
| Policy selector | **Implemented** | Intervention type, action depth, next move, rationale |
| Re-entry artifacts | **Implemented** | Continuity objects for interrupted threads |
| Typed memory / Aether | **Substantially implemented** | Sources, concepts, mechanisms, heuristics, rules, patterns, graph edges, etc. |
| Semantic retrieval | **Implemented** | pgvector retrieval; cleanup scopes embedding identity and retrieval by operator |
| Structured reasoning artifacts | **Implemented** | Problems, structures, interrogations, briefs, options, contradictions |
| Review/calibration storage | **Implemented** | Review sessions, promotions, pattern updates, calibration records |
| Model/retrieval audit storage | **Implemented as storage** | Automatic end-to-end audit wiring was not completed |
| Materialized read models | **Implemented** | Automatic refresh orchestration was not completed |
| Automatic calibration feedback | **Not completed** | Stored calibration does not automatically reweight future inference/policy |
| Complete OAuth lifecycle | **Not completed** | Token-shaped models exist; full encrypted refresh/rotation lifecycle does not |
| Production authentication/authorization | **Not completed** | Historical API is a trusted/private prototype |
| Generic `SensorAdapter` runtime | **Proposed reconstruction** | Modern architectural extension point, not a historical runtime subsystem |
| EEG / Neurosity integration | **Intended, not implemented** | Future neurophysiological evidence source only |

The repository intentionally keeps these statuses separate. A modern reconstruction document does not retroactively make an intended subsystem historical implementation.

---

## Core primitives

### Direction

Historical name: **Vector**.

```text
life arc → season → mission → thread
```

Direction distinguishes useful motion from drift.

### Sensing, observations, and evidence

The historical system records subjective, behavioral, contextual, derived, and physiological information.

WHOOP is the implemented external sensor integration.

The cleaned architecture makes the boundary more explicit:

```text
imperfect source
    ↓
observation
    ↓
feature
    ↓
evidence
    ↓
hypothesis
```

Future EEG or other neurophysiology belongs at the source/observation side of that boundary. It is **not implemented here**, and it would not be allowed to directly declare a diagnosis or authoritative state.

### Inference

Historical AI modules estimate:

- operating state
- dominant blocker
- contradictions between narrative and evidence

The historical runtime also contains fallback behavior on model/parse failure. The reconstruction identifies explicit inference-failure status as unfinished architectural work rather than presenting fallback values as ideal design.

### Policy

Historical name: **Schrödinger**.

Policy selects an intervention and action depth from the current evidence and inferred condition.

A policy decision is a testable proposal, not an oracle.

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

Instead of treating all memory as generic notes, the prototype stores typed objects such as concepts, mechanisms, trade-offs, failure modes, heuristics, diagnostic questions, protocols, cases, rules, patterns, and graph edges.

### Outcome and calibration

Traces record what happened after an action. Review/calibration structures preserve later evaluation.

The historical implementation models more of this loop than it automatically executes:

```text
prediction → action → outcome → error/usefulness → future reliability
```

Automatic reliability updating was not completed.

---

## Historical provenance

Utopia is the historical project/codename. Neurocognitive System is the current descriptive framing.

The original architecture material remains under [docs/history](docs/history/README.md) with its historical assumptions and terminology intact.

The selected historical Utopia reference point is the last Utopia-specific repository state before an unrelated thesis document was added and before the later public-preservation reframing:

`656c32b70cfac7a5ad7b94bb31451425fb6139bf`

A proposed, **not yet created**, historical tag is:

`historical-utopia-v0.1`

See [Historical provenance](docs/history/provenance.md) for the exact chronology and why that commit was selected.

---

## Trust and medical boundaries

**Do not expose the historical API directly to an untrusted network.**

The current code does not contain a complete production authentication/authorization boundary. The cleanup fixes operator scoping in semantic retrieval and known nested-resource identity mismatches, but it does not retrofit a new security architecture across the old prototype.

See [SECURITY.md](SECURITY.md) and [Technical debt](docs/technical-debt.md).

Neurocognitive System is **not a medical diagnostic system**.

Subjective, behavioral, physiological, and any future neurophysiological signals are treated as imperfect evidence about operational state and usable capacity. They are not a basis for diagnosing medical or psychiatric conditions.

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
  versions/            # 13 historical migrations + cleanup migration 014

docs/
  architecture/        # cleaned architecture
  rfcs/                # reconstruction contracts
  audit/               # static + public-release audits
  history/             # preserved Utopia material + provenance
  technical-debt.md

tests/
  test_services.py
  test_ai_modules.py
  test_routes.py
```

---

## Local inspection

Python 3.12+ and Docker are expected.

```bash
cp .env.example .env
docker compose up -d
python -m pip install -e ".[dev]"
alembic upgrade head
```

The Docker PostgreSQL port is bound to loopback by default.

### Tests

Tests intentionally refuse to run against a database whose name does not end in `_test`.

Create an isolated test database once:

```bash
docker compose exec postgres createdb -U utopia utopia_test
```

Then point both database URLs at it:

```bash
export DATABASE_URL=postgresql+asyncpg://utopia:utopia@localhost:5432/utopia_test
export DATABASE_URL_SYNC=postgresql+psycopg://utopia:utopia@localhost:5432/utopia_test

alembic upgrade head
pytest -q
ruff check --select E4,E7,E9,F src tests migrations/env.py migrations/versions/014_operator_scoped_embeddings.py
```

CI additionally verifies that cleanup migration 014 can downgrade to 013 and upgrade to head again.

The 13 historical migrations are compiled and executed, but are intentionally not reformatted to modern lint style during preservation.

Provider keys are optional unless exercising the corresponding external integrations.

---

## Security audit

The cleanup CI performs a full-history Gitleaks scan using a checkout with `fetch-depth: 0`.

The release audit also reviews the tracked tree, environment examples, ignored artifact classes, Docker binding defaults, and trust boundary.

See [Public-release audit — 2026-09-23](docs/audit/public-release-2026-09-23.md) for results and explicit limitations.

A green scanner is evidence, not proof that a secret has never existed.

---

## Further architecture documents

- [Architecture overview](docs/architecture/overview.md)
- [Sensor architecture](docs/architecture/sensors.md)
- [RFC-0001: Neurocognitive System](docs/rfcs/RFC-0001-neurocognitive-system.md)
- [RFC-0002: Observation, Evidence, and Inference](docs/rfcs/RFC-0002-observation-evidence-inference.md)
- [RFC-0003: Sensor Adapter Contract](docs/rfcs/RFC-0003-sensor-adapter-contract.md)
- [Historical terminology](docs/history/terminology.md)
- [Static audit — 2026-09-23](docs/audit/2026-09-23.md)
- [Technical debt / reconstruction boundary](docs/technical-debt.md)

---

## License

No software license has been selected yet.

Until the owner chooses one, this should be described as a **public source repository** or **source-visible repository**, not as formally open source.

Practical owner choices include MIT, Apache-2.0, or keeping the source visible without an open-source license.

---

## Status

There is no active product roadmap for the historical Utopia application.

This cleanup preserves the implementation, fixes high-confidence correctness and release-safety issues, and documents the durable architectural primitives without rewriting the prototype into something it never was.

**The implementation is historical. The questions were not.**
