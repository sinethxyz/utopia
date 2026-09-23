# Neurocognitive System Architecture

Neurocognitive System is the cleaned architectural interpretation of the historical Utopia prototype.

The system is organized around one control loop:

```text
Direction
    ↓
Sensing
    ↓
Observations
    ↓
Features
    ↓
Evidence Bundle
    ↓
Inference
    ↓
Policy
    ↓
Action / Re-entry
    ↓
Outcome Trace
    ↓
Review
    ↓
Calibration
    ↺
```

The key design rule is that these stages are not interchangeable.

A sensor reading is not an inference.  
An inference is not a policy.  
A policy is not truth.  
An outcome is evidence about whether the prior policy and inference were useful.

## 1. Direction

Direction defines what the system is trying to preserve or advance.

Historical Utopia terminology called this layer **Vector**.

The current implementation models:

```text
life arc → season → mission → thread
```

Direction exists to distinguish useful motion from drift.

## 2. Sensing

Sensing is intentionally modality-agnostic.

Historical implementation includes:

- subjective check-ins
- behavioral events
- contextual snapshots
- WHOOP physiology

The intended architecture was broader and was designed to support future sensor adapters, including neurophysiological sources such as EEG devices.

A sensor adapter should emit normalized observations. It should never directly emit a domain conclusion such as "the operator is depleted."

## 3. Observations

An observation is a recorded measurement, report, or event.

Examples:

- subjective energy = 35
- failed-start event
- WHOOP recovery measurement
- environment interruption count
- future EEG-derived feature window

Observations preserve source, time, provenance, and freshness.

## 4. Features

Features are transformations over observations.

Examples:

- failed-start rate over 24 hours
- recovery trend
- re-entry risk
- context-switch density
- EEG-derived signal features

Features remain measurements. They are not state labels.

## 5. Evidence Bundles

An evidence bundle is the exact set of observations and features used to evaluate a specific claim.

This creates a stable boundary between sensing and reasoning and makes the system auditable.

## 6. Inference

Inference turns evidence into explicit hypotheses.

Historical examples include:

- state estimate
- blocker estimate
- contradiction report

Every inference should eventually carry:

- status
- confidence
- provenance
- evidence references
- model/rule version
- timestamp

Provider failure or parse failure must not silently become a domain belief.

## 7. Policy

Policy proposes the next intervention given:

- direction
- current evidence
- inferred state
- blocker hypothesis
- available capacity
- re-entry context
- constraints

Historical Utopia called the policy selector **Schrödinger**.

A policy decision is a testable proposal, not an oracle.

## 8. Re-entry

Re-entry remains a first-class concept.

A re-entry artifact should preserve the minimum state necessary to resume an interrupted thread:

- last completed step
- unresolved edge
- smallest next move
- relevant context
- trap to avoid
- freshness

## 9. Outcome and Trace

A trace records what actually happened after a policy was acted upon.

The system should preserve the causal chain:

```text
evidence → inference → policy → action → outcome
```

## 10. Review and Calibration

Calibration compares predictions with outcomes.

The historical implementation contains review sessions, rule promotions, pattern updates, and calibration records. The cleaned architecture treats those records as the beginning of a real feedback loop rather than the completion of one.

The intended loop is:

```text
prediction
    ↓
action
    ↓
outcome
    ↓
error / usefulness measurement
    ↓
reliability update
    ↓
future evidence weighting
```

## 11. Memory and Reasoning

Historical **Aether** is the typed memory layer. It stores structured cognitive objects rather than an undifferentiated note archive.

The reasoning layer stores explicit problem structures, unknowns, assumptions, decision briefs, options, and contradiction reports.

Retrieved knowledge is evidence. It must never be treated as trusted instruction merely because it was retrieved.

## 12. Trust boundary

The historical codebase is a private prototype, not production multi-tenant software.

The current API does not implement a complete authentication or authorization boundary. Do not expose it to untrusted networks.

See [SECURITY.md](../../SECURITY.md).

## 13. Medical boundary

Neurocognitive System is designed around operational state estimation and continuity.

It is not a medical diagnostic system.

Physiological or future neurophysiological inputs should be treated as noisy evidence about operational capacity, not as a basis for diagnosing medical or psychiatric conditions.
