# RFC-0001: Neurocognitive System

**Status:** Draft  
**Historical predecessor:** Utopia v0.1

## Summary

This RFC defines the cleaned architecture extracted from Utopia.

The historical implementation explored continuity, state-aware action, typed memory, physiology, reasoning, traces, and calibration. The redesign keeps the durable primitives while separating sensing, evidence, inference, policy, and feedback more rigorously.

## Core claim

The operator is not stable.

Attention, context, energy, environment, and usable cognitive capacity change over time. A control system should therefore estimate state from imperfect evidence rather than assume a permanently stable executor.

## System loop

```text
Direction → Sensing → Observations → Features → Evidence
          → Inference → Policy → Action → Outcome → Calibration
```

## Non-goals

This system does not:

- diagnose medical or psychiatric conditions
- treat any wearable or EEG signal as ground truth
- make model output equivalent to truth
- replace operator authority
- optimize activity without regard to direction

## Historical compatibility

The existing Python package remains `utopia` during the cleanup phase so the historical implementation remains inspectable.

Historical names such as Vector, Aether, and Schrödinger are documented but are not required vocabulary for future architecture.

## Migration principle

Do not rewrite history to make the prototype appear more complete than it was.

The cleaned architecture must clearly distinguish:

1. implemented historical behavior
2. intended historical architecture
3. proposed future abstractions
