# RFC-0003: Sensor Adapter Contract

**Status:** Draft

## Motivation

The historical Utopia implementation contains WHOOP-specific integration logic, while the intended system was multimodal.

A general sensor contract prevents the core architecture from becoming coupled to one wearable or one modality.

## Contract boundary

Adapters convert external sources into normalized observations.

They MUST NOT:

- declare operator state
- choose policy
- infer diagnosis
- silently discard provenance

They SHOULD expose:

- source kind
- source/device identifier
- collection/session identifier
- observed-at timestamps or ranges
- raw value/payload or artifact reference
- units
- quality metadata
- adapter/version metadata

## High-frequency data

High-frequency streams such as EEG should use a session + artifact + feature-window model instead of row-per-sample storage in the relational core.

## Historical implementation

WHOOP remains the first concrete integration.

Future examples may include:

- EEG systems such as Neurosity-class devices
- additional wearables
- environment sensors
- software/behavior telemetry

These are extension points, not claims of current implementation.
