# Security

## Status

This repository contains a **historical private-system prototype**.

It is not production-hardened and should not be exposed directly to an untrusted network.

## Current trust model

The historical FastAPI implementation does not contain a complete authentication or authorization boundary.

Until that is redesigned:

- bind services to a trusted local/private interface only
- do not expose the API publicly
- do not use production credentials
- do not store irreplaceable private data in an unreviewed deployment
- keep provider credentials in environment variables, never in the repository

## Sensitive data

The architecture can contain highly sensitive information, including:

- subjective check-ins
- behavior traces
- physiological data
- biomarker information
- reasoning artifacts
- imported personal knowledge
- future neurophysiological observations

A future deployment should treat these data classes as private by default.

## Future sensor integrations

Planned sensor-agnostic architecture may support sources such as EEG devices.

Raw neurophysiological data should not automatically be forwarded to external model providers. Sensor data should be normalized locally into explicit observations/features with provenance and retention controls.

## Medical boundary

This project is not a medical diagnostic system.

Physiological and neurophysiological signals should be treated as imperfect evidence about operational state, not as diagnostic truth.
