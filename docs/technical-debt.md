# Technical debt and reconstruction boundary

This document records what remains **without turning the historical prototype into a new product**.

The repository is preserved architecture, not deployment guidance.

## P0 — required before any real deployment

### Authentication and authorization

The historical FastAPI surface does not provide a complete authentication or authorization boundary.

A deployed system would need an authenticated operator identity and authorization checks on every operator-owned resource.

### Operator ownership invariants

Several historical services expose lookups by bare object ID. The cleanup fixes operator scoping in semantic retrieval and rejects known nested path/body identity mismatches, but it does not retrofit a complete multi-tenant ownership model across the old API.

A production design should make operator ownership an invariant at the service/query boundary rather than relying on route conventions.

### Secret and token lifecycle

The repository contains OAuth/token-shaped models, but not a complete encrypted credential lifecycle.

A real deployment would need encryption at rest, rotation, revocation, refresh-token handling, audit, least-privilege scopes, and provider-specific incident procedures.

### Sensitive-data policy

Subjective state, behavior traces, physiology, biomarkers, reasoning artifacts, and any future neurophysiology require explicit retention, deletion, export, access, and external-processing policies.

Raw physiological or neurophysiological data should never be forwarded to external model providers by default.

## P1 — architectural completion

### EvidenceBundle

The reconstructed architecture identifies an explicit evidence-bundle boundary: the exact observations/features used to evaluate a claim.

The historical code passes structured evidence, but does not implement a first-class `EvidenceBundle` runtime object with immutable provenance.

### InferenceStatus

Provider failure and parse failure should be represented explicitly rather than converted into a low-confidence domain belief.

A future implementation should distinguish states such as `VALID`, `INSUFFICIENT_EVIDENCE`, `MODEL_ERROR`, and `PARSE_ERROR`.

### Provenance

Inferences should reference the observation/feature versions, model or rule version, retrieval set, and timestamp that produced them.

### Automatic model and retrieval audit

Model-run and retrieval-run storage exists, but provider calls and retrieval are not automatically wired into a complete audit trail.

### True calibration feedback

Review sessions and calibration records exist. The historical runtime does not automatically use observed error to update future signal reliability, model weighting, or policy selection.

### Materialized-view refresh

Historical materialized read models exist without an automatic refresh mechanism.

## P2 — future research

### Generic sensor adapters

The common `SensorAdapter` contract is a modern reconstruction proposal. WHOOP is historically implemented directly; a general adapter runtime is not.

### EEG / neurophysiology

EEG and Neurosity-class devices are future/intended sources only.

Any future integration should emit observations/features with provenance and quality metadata. It should not directly emit diagnoses or authoritative cognitive-state labels.

### Individualized signal reliability

A mature calibration layer could learn that the same signal has different predictive value for different operators, contexts, and time horizons.

### Raw-signal storage strategy

High-frequency raw data should use an explicit artifact/stream storage design with checksums, retention controls, processing versions, and derived feature windows rather than one relational row per sample.
