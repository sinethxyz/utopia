# Historical provenance

## Naming

**Utopia** is the historical project and codename.

**Neurocognitive System** is the present descriptive framing used to make the old architecture legible to a public reader.

The Python package, database language, and historical documents continue to use Utopia-era names where changing them would erase useful evidence.

## What the cleanup means

The public cleanup separates three categories:

1. **Historically implemented** — code and database structures that exist in the preserved prototype.
2. **Historically intended but incomplete** — ideas visible in the design or partial implementation that were not completed.
3. **Modern reconstruction** — terminology and boundaries added during the 2026 preservation pass to explain the durable primitives.

A modern architecture document is not evidence that its cleaned abstraction existed as a finished historical subsystem.

In particular, the proposed generic sensor-adapter boundary and future EEG / Neurosity-class integration are reconstruction or intended direction, not historical implementation.

## Pre-cleanup reference point

The first explicit Neurocognitive System reframing on `main` is commit:

`82dafca1f4dfccf8ea3e5f7defb3c6f3dff516ec` — `docs: reframe Utopia as historical Neurocognitive System`

Its direct parent is:

`1b2b5dba817610711a38aea382fe563413ee6dab` — `Add ADHD visual prosthetic thesis`

That parent is the last repository state before the public-preservation reframing began and is therefore the clearest historical reference point currently established from Git history.

## Proposed historical tag

If the owner wants an immutable public marker, the proposed tag is:

`historical-utopia-v0.1`

pointing exactly to:

`1b2b5dba817610711a38aea382fe563413ee6dab`

The tag has **not** been created by this cleanup. Creating it is an owner decision.

## Chronology

- **2026-04-02 to 2026-04-06** — core Utopia implementation assembled: database layers, services, WHOOP integration, reasoning modules, semantic retrieval, review/calibration structures, and tests.
- **2026-04-20** — the historical repository received the ADHD visual-prosthetic thesis document.
- **2026-09-23** — public-preservation work began with the Neurocognitive System reframing, static audit, architecture reconstruction, correctness fixes, and release hygiene.

The intended Git story is therefore:

```text
historical Utopia implementation
        ↓
historical pre-cleanup reference point
        ↓
audit and architectural reconstruction
        ↓
public preservation
```

No history rewrite is required to tell that story.
