# Sensor architecture

The cleaned Neurocognitive System treats sensing as a replaceable boundary.

The historical implementation contains WHOOP-specific ingestion. Future sensing should be implemented through a common adapter contract.

## Design rule

A sensor adapter emits **observations**.

It does not emit diagnoses, identity claims, or policy decisions.

```text
device / source
      ↓
adapter
      ↓
observation
      ↓
feature derivation
      ↓
evidence bundle
      ↓
inference
```

## Proposed SensorAdapter contract

A future adapter should expose capabilities such as:

- source identity
- device/session identity
- observation types
- time range
- sampling metadata
- freshness
- provenance
- optional raw-artifact reference

Conceptually:

```python
class SensorAdapter(Protocol):
    source_kind: str

    async def capabilities(self) -> SensorCapabilities: ...
    async def collect(self, request: CollectionRequest) -> list[Observation]: ...
```

The exact implementation is intentionally deferred.

## High-frequency sources

High-frequency sources such as EEG should not be represented as one PostgreSQL row per raw sample.

The intended split is:

```text
SensorSession
    ↓
raw artifact / stream
    ↓
feature windows
    ↓
normalized observations
    ↓
evidence
```

Raw signal artifacts can live in private object/file storage. PostgreSQL should store identity, provenance, time ranges, checksums, and derived features required by the control loop.

## WHOOP

WHOOP is the historical first sensor implementation.

In the cleaned architecture it should eventually become an adapter that produces observations such as:

- recovery
- sleep
- strain/cycle
- workout
- body measurement

WHOOP-derived values remain evidence inputs, not policy authority.

## EEG / neurophysiology

The historical direction included future neurophysiological sensing, including devices in the class of Neurosity EEG.

A future EEG adapter should preserve:

- device identity
- session identity
- sample-rate/channel metadata
- time range
- processing pipeline/version
- raw-artifact checksum/reference
- derived feature definitions
- feature-window timestamps
- quality/confidence indicators

EEG-derived features must not be translated directly into medical or psychiatric conclusions.

The useful question for this architecture is operational:

> Does this signal improve prediction of usable cognitive state or action depth for this operator?

If repeated outcomes show that a signal is not useful, the calibration layer should reduce its weight.

## Privacy

Raw neurophysiological data is a sensitive data class.

Default policy should be:

- private/local storage
- explicit retention
- no automatic external-model upload
- derived features preferred over raw streams for routine inference
- provenance retained for every transformation
