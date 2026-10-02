import pytest
from typing import Dict, Any

def calculate_escalation_proximity(
    consecutive_fallback_count: int,
    sentiment_score: float,
    failed_auth_attempts: int,
    has_guardrail_breach: bool
) -> float:
    c_fallback = 1.0 if consecutive_fallback_count >= 2 else (0.5 if consecutive_fallback_count == 1 else 0.0)
    s_negative = max(0.0, (abs(sentiment_score) - 0.40) / 0.60) if sentiment_score < -0.40 else 0.0
    a_auth = 1.0 if failed_auth_attempts >= 3 else (0.5 if failed_auth_attempts == 2 else 0.0)
    g_flag = 1.0 if has_guardrail_breach else 0.0

    raw_score = 0.35 * c_fallback + 0.30 * s_negative + 0.25 * a_auth + 0.40 * g_flag
    return min(1.0, round(raw_score, 4))

def test_dialogue_state_schema_keys(sample_dialogue_state: Dict[str, Any]):
    required_keys = [
        "session_id", "conversation_id", "customer_id", "current_turn_index",
        "auth_level", "active_intent", "intent_confidence", "slot_state",
        "sentiment_trajectory", "guardrail_flags", "escalation_proximity",
        "turn_history"
    ]
    for key in required_keys:
        assert key in sample_dialogue_state, f"Missing required key: {key}"

def test_escalation_proximity_calculation():
    p_clean = calculate_escalation_proximity(0, 0.2, 0, False)
    assert p_clean == 0.0

    p_severe = calculate_escalation_proximity(2, -0.80, 0, False)
    assert p_severe >= 0.50

    p_critical = calculate_escalation_proximity(1, -0.5, 3, True)
    assert p_critical >= 0.75
