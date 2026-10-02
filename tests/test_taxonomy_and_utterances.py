import json
from pathlib import Path
import pytest

UTTERANCE_FILE = Path(__file__).parent.parent / "docs" / "intent-taxonomy" / "utterance-library.json"

EXPECTED_INTENTS = [
    "ACC-001", "ACC-002", "ACC-003", "ACC-004", "ACC-005", "ACC-006", "ACC-007",
    "TXN-001", "TXN-002", "TXN-003", "TXN-004", "TXN-005", "TXN-006",
    "CRD-001", "CRD-002", "CRD-003", "CRD-004", "CRD-005",
    "PRD-001", "PRD-002", "PRD-003", "PRD-004", "PRD-005",
    "CMP-001", "CMP-002", "CMP-003", "CMP-004", "CMP-005",
    "SEC-001", "SEC-002", "SEC-003", "SEC-004"
]

def test_utterance_file_exists_and_valid_json():
    assert UTTERANCE_FILE.exists(), f"File does not exist: {UTTERANCE_FILE}"
    with open(UTTERANCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 300, f"Expected at least 300 utterances, got {len(data)}"

def test_all_30_intents_represented():
    with open(UTTERANCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    intent_counts = {}
    for entry in data:
        intent = entry.get("intent_id")
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    for intent in EXPECTED_INTENTS:
        assert intent in intent_counts, f"Intent {intent} missing from utterance library"
        assert intent_counts[intent] >= 10, f"Intent {intent} has only {intent_counts[intent]} utterances (min 10 required)"

def test_multilingual_coverage():
    with open(UTTERANCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    languages = set(entry.get("language") for entry in data)
    assert "en" in languages, "Missing English utterances"
    assert "hi" in languages, "Missing Hindi utterances"
    assert "hi-en" in languages, "Missing Hinglish code-switching utterances"
