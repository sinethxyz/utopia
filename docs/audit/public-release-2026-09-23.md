# Public-release audit — 2026-09-23

This audit covers the public-preservation branches for the historical Utopia / Neurocognitive System repository.

It is intentionally narrower than a production security assessment.

## Current-tree audit

The tracked-file inventory was reviewed for common public-release hazards, including:

- committed environment files
- provider credentials
- API keys and tokens
- database dumps
- local database files
- logs
- private payload/data artifacts
- raw physiological datasets
- private hostnames and URLs
- unsafe development defaults

Observed public configuration uses placeholder/empty provider variables in `.env.example`.

The Docker PostgreSQL port was changed to bind to `127.0.0.1` rather than all host interfaces.

`.gitignore` covers local environment variants, logs, dumps, SQL dumps, local databases, and common local data artifacts.

Gitleaks also scans the checked-out current commit as part of CI.

**Result:** no secret finding was reported by the automated scan, and no tracked raw user/physiological dataset or committed `.env` file was identified in the reviewed tree.

## Reachable-history audit

CI checks out the repository with full history:

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 0
```

and runs:

```yaml
- uses: gitleaks/gitleaks-action@v3
```

The history scan passed during the cleanup.

This is materially stronger than scanning only HEAD because it can detect many credentials that were committed and later removed.

## What this audit does not prove

A successful automated scan does **not** prove that no secret has ever existed.

The audit cannot establish:

- whether an unrecognised credential format is present
- whether a value that looks harmless is valid in an external system
- whether a credential was exposed in a fork, cache, issue, release artifact, or other system
- whether deleted/unreachable Git objects exist outside the fetched reachable history
- whether GitHub Actions secrets or provider dashboards contain safe values
- whether credentials previously used elsewhere have been rotated

If a real credential is ever known to have been committed, rotation remains necessary even if the scanner is green.

## Trust boundary

The historical API still lacks a complete production authentication and authorization boundary.

The repository must therefore be treated as local/private prototype software and should not be exposed directly to an untrusted network.

Operator-scoped semantic retrieval has been fixed in the cleanup, and known nested path/body identity mismatches are rejected. Bare-ID ownership enforcement across the historical API remains documented P0 deployment debt.

## Medical boundary

This repository is not a medical diagnostic system.

Subjective, behavioral, physiological, and any future neurophysiological signals are noisy evidence for operational hypotheses; they are not diagnostic truth.
