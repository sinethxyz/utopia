"""API route integration tests.

Tests the FastAPI endpoints with mocked AI providers and a real
(rolled-back) database transaction. Verifies request/response schemas,
status codes, and service integration.
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from utopia.models.core import Operator


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _seed_operator(db_session, operator_id: uuid.UUID) -> None:
    """Insert a test operator for FK satisfaction."""
    op = Operator(id=operator_id, display_name="Test Op", timezone="UTC")
    db_session.add(op)
    await db_session.flush()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:

    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Evidence routes
# ---------------------------------------------------------------------------

class TestEvidenceRoutes:

    @pytest.mark.asyncio
    async def test_create_checkin(self, client, db_session, operator_id):
        await _seed_operator(db_session, operator_id)

        resp = await client.post(
            "/evidence/checkins",
            json={
                "operator_id": str(operator_id),
                "energy": 55,
                "clarity": 70,
                "resistance": 30,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["energy"] == 55
        assert data["clarity"] == 70


# ---------------------------------------------------------------------------
# Execution routes
# ---------------------------------------------------------------------------

class TestExecutionRoutes:

    @pytest.mark.asyncio
    async def test_create_state_estimate(self, client, db_session, operator_id):
        await _seed_operator(db_session, operator_id)

        resp = await client.post(
            "/execution/state-estimates",
            json={
                "operator_id": str(operator_id),
                "state_kind": "execute",
                "confidence": "0.82",
                "contributing_factors": [{"source": "test"}],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["state_kind"] == "execute"

    @pytest.mark.asyncio
    async def test_create_policy_decision(self, client, db_session, operator_id):
        await _seed_operator(db_session, operator_id)

        resp = await client.post(
            "/execution/policy-decisions",
            json={
                "operator_id": str(operator_id),
                "mode": "execute",
                "intervention_kind": "execute",
                "action_depth": "moderate",
                "next_move": "Write the integration test",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["intervention_kind"] == "execute"
        assert data["action_depth"] == "moderate"


# ---------------------------------------------------------------------------
# AI routes
# ---------------------------------------------------------------------------

class TestAIRoutes:

    @pytest.mark.asyncio
    async def test_assess_endpoint(self, client, db_session, operator_id, mock_claude):
        await _seed_operator(db_session, operator_id)

        # Mock all three AI module calls in sequence
        mock_claude.side_effect = [
            # State estimator
            (
                json.dumps({"state_kind": "execute", "confidence": 0.8, "contributing_factors": []}),
                {"model": "test", "prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80, "latency_ms": 100},
            ),
            # Blocker classifier
            (
                json.dumps({"blocker_kind": "ambiguity", "confidence": 0.6, "supporting_evidence": []}),
                {"model": "test", "prompt_tokens": 60, "completion_tokens": 35, "total_tokens": 95, "latency_ms": 120},
            ),
            # Policy selector
            (
                json.dumps({
                    "intervention_kind": "execute",
                    "action_depth": "moderate",
                    "next_move": "Write the next test case",
                    "rationale": "Conditions support action",
                    "confidence": 0.75,
                    "caution_flags": [],
                }),
                {"model": "test", "prompt_tokens": 70, "completion_tokens": 50, "total_tokens": 120, "latency_ms": 200},
            ),
        ]

        resp = await client.post(
            "/ai/assess",
            json={"operator_id": str(operator_id)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["state_estimate"]["state_kind"] == "execute"
        assert data["blocker_estimate"]["blocker_kind"] == "ambiguity"
        assert data["policy_decision"]["intervention_kind"] == "execute"
        assert data["state_estimate_id"] is not None

    @pytest.mark.asyncio
    async def test_route_endpoint(self, client, mock_claude):
        mock_claude.return_value = (
            json.dumps({
                "intent": "assess",
                "confidence": 0.9,
                "extracted_context": {"urgency_signal": "high"},
                "reasoning": "Operator seems stuck",
            }),
            {"model": "test", "prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50, "latency_ms": 80},
        )

        resp = await client.post(
            "/ai/route",
            json={
                "operator_id": str(uuid.uuid4()),
                "message": "I'm stuck and don't know what to do",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "assess"
        assert data["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_structure_problem_endpoint(self, client, db_session, operator_id, mock_claude):
        await _seed_operator(db_session, operator_id)

        # First create a problem
        from utopia.schemas.reasoning import ProblemCreate
        from utopia.services.reasoning_service import ReasoningService

        svc = ReasoningService(db_session)
        problem = await svc.create_problem(
            ProblemCreate(
                operator_id=operator_id,
                title="Test problem",
                raw_prompt="Should I do X?",
            )
        )
        await db_session.flush()

        mock_claude.return_value = (
            json.dumps({
                "objective": "Decide on X",
                "stakes": "Medium",
                "actors": [],
                "incentives": [],
                "constraints": [],
                "assumptions": ["X is feasible"],
                "unknowns": ["Cost of X"],
                "irreversibilities": [],
                "bottlenecks": [],
                "observable_facts": [],
                "narrative_layer": [],
                "distortion_candidates": [],
                "confidence": 0.7,
            }),
            {"model": "test", "prompt_tokens": 80, "completion_tokens": 60, "total_tokens": 140, "latency_ms": 250},
        )

        resp = await client.post(
            "/ai/structure-problem",
            json={
                "problem_id": str(problem.id),
                "raw_prompt": "Should I do X?",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["structure"]["objective"] == "Decide on X"

    @pytest.mark.asyncio
    async def test_interpret_physiology_endpoint(self, client, mock_claude):
        mock_claude.return_value = (
            json.dumps({
                "capacity_level": "strong",
                "capacity_score": 78,
                "key_signals": [],
                "action_depth_ceiling": "deep",
                "recovery_trajectory": "improving",
                "warnings": [],
                "recommendation": "Good conditions for deep work.",
                "confidence": 0.85,
            }),
            {"model": "test", "prompt_tokens": 60, "completion_tokens": 40, "total_tokens": 100, "latency_ms": 180},
        )

        resp = await client.post(
            "/ai/interpret-physiology",
            json={
                "operator_id": str(uuid.uuid4()),
                "physiology_data": {"recovery_score": 78, "hrv_rmssd": 65.0},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["capacity_level"] == "strong"
        assert data["action_depth_ceiling"] == "deep"

    @pytest.mark.asyncio
    async def test_check_contradictions_endpoint(self, client, db_session, operator_id, mock_claude):
        await _seed_operator(db_session, operator_id)

        mock_claude.return_value = (
            json.dumps({
                "contradictions": [
                    {
                        "contradiction_kind": "narrative_vs_behavior",
                        "description": "Says productive but many failed starts",
                        "evidence": [],
                        "severity": 0.6,
                    }
                ],
                "clean_signals": [],
                "confidence": 0.8,
            }),
            {"model": "test", "prompt_tokens": 80, "completion_tokens": 50, "total_tokens": 130, "latency_ms": 220},
        )

        resp = await client.post(
            "/ai/check-contradictions",
            json={
                "operator_id": str(operator_id),
                "operator_claims": {"status": "productive"},
                "evidence": {"failed_starts": 5},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["contradictions"]) == 1

    @pytest.mark.asyncio
    async def test_deliberate_endpoint(self, client, mock_claude):
        call_count = 0

        async def _mock(*, system, user, max_tokens, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 4:
                names = ["risk_analyst", "opportunity_scout", "contrarian", "state_advisor"]
                return (
                    json.dumps({
                        "perspective": names[call_count - 1],
                        "key_points": [{"point": "Test", "reasoning": "Test", "confidence": 0.7}],
                        "recommendation": "Test rec",
                        "dissents": [],
                    }),
                    {"model": "test", "prompt_tokens": 40, "completion_tokens": 30, "total_tokens": 70, "latency_ms": 100},
                )
            return (
                json.dumps({
                    "consensus_points": ["Agree on timing"],
                    "tension_points": [],
                    "dominant_perspective": "risk_analyst",
                    "synthesis": "Wait and see.",
                    "decision_readiness": "defer",
                    "confidence": 0.65,
                }),
                {"model": "test", "prompt_tokens": 60, "completion_tokens": 40, "total_tokens": 100, "latency_ms": 150},
            )

        mock_claude.side_effect = _mock

        resp = await client.post(
            "/ai/deliberate",
            json={"problem_description": "Should I pivot the product?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["perspectives"]) == 4
        assert data["decision_readiness"] == "defer"
