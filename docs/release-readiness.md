# Public release readiness

**Status:** Ready except owner decisions.

This status refers to **public preservation / portfolio release**, not production deployment.

The final public state is represented by:

- **PR #4** — `Neurocognitive System v0.2 foundation cleanup`
- **PR #5** — `Neurocognitive System v0.3 public release polish`, stacked on PR #4

Neither PR is merged by this cleanup.

## Verification gates

The cleanup CI requires:

- editable development install
- Python compile pass across source, tests, and migrations
- focused Ruff correctness lint (`E4/E7/E9/F`) across active Python and cleanup migration 014
- migration from zero on PostgreSQL 16 + pgvector
- downgrade of migration 014 to 013
- re-upgrade from 013 to 014/head
- pytest
- full reachable-history Gitleaks scan using `fetch-depth: 0`
- relative-link validation across active public documentation

The 13 historical migrations remain compile- and execution-tested but are not reformatted to modern style rules during preservation.

## Regression coverage added during cleanup

The public-release pass specifically verifies:

- UUIDv7 values are normalized to the standard-library UUID type at service boundaries
- zero-valued evidence is preserved rather than treated as missing
- semantic retrieval is scoped by operator
- similar-entity retrieval is scoped by operator
- known nested path/body identity mismatches are rejected
- re-entry artifact lifecycle still works
- the health response matches its public historical framing

## Security/public-safety evidence

### Current tree

The tracked tree was reviewed for common sensitive artifact types and unsafe public defaults.

No tracked committed `.env`, database, dump, log, key/archive, or raw-data-style artifact was identified by the release inventory patterns.

Provider variables in `.env.example` are placeholders/empty.

Docker PostgreSQL binds to `127.0.0.1` by default.

### Reachable Git history

The CI history scan checks out full reachable history and runs Gitleaks.

The scan passed during the cleanup.

The limitations of this result are documented in [Public-release audit — 2026-09-23](audit/public-release-2026-09-23.md). A green scanner is evidence, not proof that no secret has ever existed.

## Trust boundary

The repository remains a historical trusted/private prototype.

It is **not** production multi-tenant software and should not be exposed directly to an untrusted network.

The cleanup addresses the identified vector-retrieval isolation defect and known nested-resource path/body mismatches. It deliberately does not retrofit a complete authentication/authorization and ownership architecture.

See [Technical debt and reconstruction boundary](technical-debt.md).

## Historical claims

The cleanup separates:

1. historically implemented behavior
2. historically intended but incomplete behavior
3. modern architectural reconstruction

EEG / Neurosity-class integration is explicitly **intended/future, not implemented**.

The generic `SensorAdapter` is explicitly a **proposed reconstruction**, not a historical subsystem.

Automatic calibration learning, complete OAuth lifecycle, complete automatic audit wiring, and production authentication are explicitly incomplete.

## Provenance

The verified pre-cleanup reference point is:

`1b2b5dba817610711a38aea382fe563413ee6dab`

The proposed tag is:

`historical-utopia-v0.1`

No tag has been created.

See [Historical provenance](history/provenance.md).

## Repository metadata

Recommended GitHub description:

> Historical multimodal neurocognitive control architecture for state estimation, continuity, policy selection, and outcome calibration.

Recommended topics:

- `cognitive-systems`
- `state-estimation`
- `control-systems`
- `human-computer-interaction`
- `wearables`
- `fastapi`
- `postgresql`
- `pgvector`
- `llm`

The connected GitHub capability used for this cleanup can modify repository files, branches, and pull requests, but does not expose repository-settings writes. Description/topics therefore remain recommended metadata rather than silently claiming they were changed.

## Owner decisions remaining

1. **License** — choose MIT, Apache-2.0, or intentionally keep the repository public/source-visible without an open-source license.
2. **Merge** — decide whether/when to merge PR #4, then PR #5 (or retarget #5 after #4 merges).
3. **Historical tag/release** — decide whether to create `historical-utopia-v0.1` at the exact pre-cleanup commit.

No other architectural/product decision is required for public preservation.

## Public-release conclusion

A reader should be able to arrive from a CV, X, LinkedIn, a GitHub profile, an engineering conversation, or an investor/research context and understand:

- what Utopia historically was
- what was actually implemented
- what remained incomplete
- what the modern reconstruction is doing
- why EEG and other future sensing are not historical implementation
- why the repository is interesting without mistaking it for production software
- what the security and medical boundaries are

That is the release target.
