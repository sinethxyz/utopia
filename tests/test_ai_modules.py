"""Unit tests for AI Fabric modules.

Tests the parsing and response handling of each AI module
with mocked Claude responses. These tests verify the module
logic without making real API calls.
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from utopia.enums import BlockerKind, StateKind


# ---------------------------------------------------------------------------
# State Estimator
# ---------------------------------------------------------------------------

class TestStateEstimator:

    @pytest.mark.asyncio
    async def test_estimate_state_parses_response(self, mock_claude):
        from utopia.ai.state_estimator import estimate_state

        mock_claude.return_value = (
            json.dumps({
                "state_kind": "recover",
                "confidence": 0.9,
                "contributing_factors": [
                    {"source": "checkin", "signal": "energy", "value": "15", "weight": "high"}
                ],
            }),
            {"model": "test", "prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80, "latency_ms": 100},
        )

        op_id = uuid.uuid4()
        evidence = {"checkin": {"energy": 15}}

        create, usage = await estimate_state(op_id, evidence)

        assert create.state_kind == StateKind.recover
        assert create.confidence == Decimal("0.9")
        assert len(create.contributing_factors) == 1
        assert usage["model"] == "test"

    @pytest.mark.asyncio
    async def test_estimate_state_handles_parse_failure(self, mock_claude):
        from utopia.ai.state_estimator import estimate_state

        mock_claude.return_value = ("not valid json at all", {"model": "test", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "latency_ms": 0})

        op_id = uuid.uuid4()
        create, _ = await estimate_state(op_id, {})

        # Should fall back to orient with low confidence
        assert create.state_kind == StateKind.orient
        assert create.confidence == Decimal("0.3")


# ---------------------------------------------------------------------------
# Blocker Classifier
# ---------------------------------------------------------------------------

class TestBlockerClassifier:

    @pytest.mark.asyncio
    async def test_classify_blocker_parses_response(self, mock_claude):
        from utopia.ai.blocker_classifier import classify_blocker

        mock_claude.return_value = (
            json.dumps({
                "blocker_kind": "physiological_depletion",
                "confidence": 0.85,
                "supporting_evidence": [
                    {"source": "whoop", "signal": "recovery", "value": "22", "reasoning": "Very low recovery"}
                ],
            }),
            {"model": "test", "prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80, "latency_ms": 100},
        )

        op_id = uuid.uuid4()
        create, _ = await classify_blocker(op_id, {}, {"state_kind": "recover"})

        assert create.blocker_kind == BlockerKind.physiological_depletion
        assert create.confidence == Decimal("0.85")


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

class TestRouter:

    @pytest.mark.asyncio
    async def test_classify_intent(self, mock_claude):
        from utopia.ai.router import classify_intent

        mock_claude.return_value = (
            json.dumps({
                "intent": "structure_problem",
                "confidence": 0.88,
                "extracted_context": {"problem_hint": "career decision", "urgency_signal": "medium"},
                "reasoning": "Operator explicitly asks to break down a decision.",
            }),
            {"model": "test", "prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80, "latency_ms": 100},
        )

        result, usage = await classify_intent(uuid.uuid4(), "Help me think about switching jobs")

        assert result["intent"] == "structure_problem"
        assert result["confidence"] == 0.88

    @pytest.mark.asyncio
    async def test_classify_intent_fallback(self, mock_claude):
        from utopia.ai.router import classify_intent

        mock_claude.return_value = ("garbage response", {"model": "test", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "latency_ms": 0})

        result, _ = await classify_intent(uuid.uuid4(), "help")

        assert result["intent"] == "assess"
        assert result["confidence"] == 0.3


# ---------------------------------------------------------------------------
# Problem Structurer
# ---------------------------------------------------------------------------

class TestProblemStructurer:

    @pytest.mark.asyncio
    async def test_structure_problem(self, mock_claude):
        from utopia.ai.problem_structurer import structure_problem

        mock_claude.return_value = (
            json.dumps({
                "objective": "Decide whether to accept job offer",
                "stakes": "Career trajectory for next 3-5 years",
                "actors": [{"name": "operator", "role": "decision maker", "incentive": "growth"}],
                "incentives": [],
                "constraints": [{"type": "time", "description": "Must respond by Friday"}],
                "assumptions": ["Current role has no growth path"],
                "unknowns": ["Team culture at new company"],
                "irreversibilities": ["Burning bridge with current employer"],
                "bottlenecks": ["Need more info about team"],
                "observable_facts": ["Offer is 30% pay increase"],
                "narrative_layer": ["I deserve better"],
                "distortion_candidates": ["Recency bias from bad week at current job"],
                "confidence": 0.75,
            }),
            {"model": "test", "prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180, "latency_ms": 300},
        )

        problem_id = uuid.uuid4()
        create, usage = await structure_problem(problem_id, "Should I take this job offer?")

        assert create.problem_id == problem_id
        assert create.objective == "Decide whether to accept job offer"
        assert len(create.constraints) == 1
        assert create.confidence == Decimal("0.75")


# ---------------------------------------------------------------------------
# Physiology Interpreter
# ---------------------------------------------------------------------------

class TestPhysiologyInterpreter:

    @pytest.mark.asyncio
    async def test_interpret_physiology(self, mock_claude):
        from utopia.ai.physiology_interpreter import interpret_physiology

        mock_claude.return_value = (
            json.dumps({
                "capacity_level": "fragile",
                "capacity_score": 35,
                "key_signals": [
                    {"signal": "recovery", "value": "28%", "interpretation": "Below baseline", "concern_level": "high"}
                ],
                "action_depth_ceiling": "narrow",
                "recovery_trajectory": "declining",
                "warnings": ["Two consecutive red recoveries"],
                "recommendation": "Limit to narrow-depth tasks. Prioritize sleep tonight.",
                "confidence": 0.82,
            }),
            {"model": "test", "prompt_tokens": 80, "completion_tokens": 60, "total_tokens": 140, "latency_ms": 250},
        )

        interp, usage = await interpret_physiology(
            uuid.uuid4(),
            {"recovery_score": 28, "hrv_rmssd": 35.2},
        )

        assert interp.capacity_level == "fragile"
        assert interp.capacity_score == 35
        assert interp.action_depth_ceiling == "narrow"
        assert len(interp.warnings) == 1


# ---------------------------------------------------------------------------
# Contradiction Checker
# ---------------------------------------------------------------------------

class TestContradictionChecker:

    @pytest.mark.asyncio
    async def test_check_contradictions_finds_issues(self, mock_claude):
        from utopia.ai.contradiction_checker import check_contradictions

        mock_claude.return_value = (
            json.dumps({
                "contradictions": [
                    {
                        "contradiction_kind": "physiology_vs_claim",
                        "description": "Claims to feel fine but recovery is 22%",
                        "evidence": [
                            {"source": "whoop", "claim": "feeling fine", "reality": "recovery 22%"}
                        ],
                        "severity": 0.8,
                    }
                ],
                "clean_signals": ["Direction is consistent with actions"],
                "confidence": 0.85,
            }),
            {"model": "test", "prompt_tokens": 100, "completion_tokens": 70, "total_tokens": 170, "latency_ms": 280},
        )

        reports, usage = await check_contradictions(
            uuid.uuid4(),
            operator_claims={"feeling": "fine"},
            physiology={"recovery_score": 22},
        )

        assert len(reports) == 1
        assert reports[0].contradiction_kind == "physiology_vs_claim"
        assert reports[0].severity == Decimal("0.8")

    @pytest.mark.asyncio
    async def test_check_contradictions_no_data(self, mock_claude):
        from utopia.ai.contradiction_checker import check_contradictions

        reports, usage = await check_contradictions(uuid.uuid4())

        assert len(reports) == 0
        assert usage["total_tokens"] == 0


# ---------------------------------------------------------------------------
# Council
# ---------------------------------------------------------------------------

class TestCouncil:

    @pytest.mark.asyncio
    async def test_deliberate(self, mock_claude):
        from utopia.ai.council import deliberate

        call_count = 0

        async def _mock_complete(*, system, user, max_tokens, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count <= 4:
                # Perspective responses
                perspective_names = ["risk_analyst", "opportunity_scout", "contrarian", "state_advisor"]
                name = perspective_names[call_count - 1]
                return (
                    json.dumps({
                        "perspective": name,
                        "key_points": [{"point": f"Point from {name}", "reasoning": "Test", "confidence": 0.7}],
                        "recommendation": f"Recommendation from {name}",
                        "dissents": [],
                    }),
                    {"model": "test", "prompt_tokens": 50, "completion_tokens": 40, "total_tokens": 90, "latency_ms": 150},
                )
            else:
                # Synthesis response
                return (
                    json.dumps({
                        "consensus_points": ["All agree the timing matters"],
                        "tension_points": [{"tension": "Risk vs opportunity", "perspectives": ["risk_analyst", "opportunity_scout"], "stakes": "Career"}],
                        "dominant_perspective": "state_advisor",
                        "synthesis": "Wait until recovery improves before deciding.",
                        "decision_readiness": "defer",
                        "confidence": 0.72,
                    }),
                    {"model": "test", "prompt_tokens": 80, "completion_tokens": 60, "total_tokens": 140, "latency_ms": 200},
                )

        mock_claude.side_effect = _mock_complete

        result = await deliberate("Should I take the job offer?")

        assert len(result.perspectives) == 4
        assert len(result.consensus_points) == 1
        assert result.decision_readiness == "defer"
        assert result.confidence == 0.72
        assert len(result.model_usage) == 5  # 4 perspectives + synthesis
