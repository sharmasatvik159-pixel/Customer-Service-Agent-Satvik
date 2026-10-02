import pytest
import uuid
from typing import Dict, Any

@pytest.fixture
def sample_session_id() -> str:
    return str(uuid.uuid4())

@pytest.fixture
def sample_customer_id() -> str:
    return "CUST_9918231"

@pytest.fixture
def sample_dialogue_state(sample_session_id: str, sample_customer_id: str) -> Dict[str, Any]:
    return {
        "session_id": sample_session_id,
        "conversation_id": str(uuid.uuid4()),
        "customer_id": sample_customer_id,
        "channel": "MOBILE_APP",
        "current_turn_index": 1,
        "auth_level": "OTP_VERIFIED",
        "active_intent": "transfers.wire_domestic",
        "intent_confidence": 0.94,
        "slot_state": {
            "recipient_name": {
                "raw_value": "Acme Title LLC",
                "normalized_value": "Acme Title LLC",
                "status": "VALIDATED",
                "extraction_confidence": 0.96,
                "source_turn": 1
            },
            "wire_amount": {
                "raw_value": "5000",
                "normalized_value": 5000.00,
                "status": "VALIDATED",
                "extraction_confidence": 0.98,
                "source_turn": 1
            }
        },
        "suspended_flows": [],
        "sentiment_trajectory": {
            "current_score": 0.10,
            "rolling_average_last_3": 0.15,
            "sentiment_slope": "STABLE",
            "detected_emotions": ["URGENCY"]
        },
        "guardrail_flags": {
            "pii_detected_count": 0,
            "injection_attempt_detected": False,
            "unauthorized_financial_advice_prevented": False,
            "hallucination_suppression_count": 0,
            "advisory_disclaimer_attached": True
        },
        "escalation_proximity": {
            "proximity_score": 0.20,
            "consecutive_fallback_count": 0,
            "failed_auth_attempts": 0,
            "primary_trigger": None
        },
        "turn_history": [
            {
                "turn_index": 1,
                "timestamp": "2026-10-02T12:00:00Z",
                "speaker": "USER",
                "masked_utterance": "I want to wire 5000 dollars to Acme Title LLC",
                "intent": "transfers.wire_domestic",
                "action_taken": "PROMPT_CONFIRMATION"
            }
        ]
    }
