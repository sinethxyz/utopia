# RFC-0002: Observation, Evidence, and Inference

**Status:** Draft

## Problem

The historical architecture sometimes collapses measurement, evidence, and model judgment into one object graph.

That makes provenance harder to inspect and allows model failure to masquerade as domain truth.

## Definitions

### Observation

A measurement, report, or event produced by a known source.

An observation answers:

> What was recorded?

### Feature

A deterministic or model-derived transformation over one or more observations.

A feature answers:

> What signal was derived?

### Evidence

An observation or feature used in support of or against a specific claim.

Evidence answers:

> Why is this claim being considered?

### Inference

A hypothesis produced from an evidence bundle.

An inference answers:

> What does the system currently believe, with what confidence and provenance?

### Policy

A proposed intervention based on direction, evidence, inference, constraints, and capacity.

A policy answers:

> What should be tried next?

### Outcome

A trace of what happened after action.

An outcome answers:

> What did reality do?

## Required invariant

No provider error, parse error, missing sensor value, or retrieval failure may silently become a valid inference.

Future inference records should distinguish statuses such as:

- valid
- low_confidence
- insufficient_evidence
- provider_error
- parse_error
- rejected

## Sensor rule

Sensor adapters emit observations.

They do not emit operator identity claims, diagnoses, or policy decisions.

## Calibration rule

Confidence should become increasingly grounded in observed predictive usefulness rather than model self-reported certainty alone.
