import json
import os
import pytest

SIMULATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "simulations")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")

def test_all_20_simulations_exist_and_valid_json():
    assert os.path.exists(SIMULATIONS_DIR), f"Directory not found: {SIMULATIONS_DIR}"
    
    for i in range(1, 21):
        filename = f"conversation_{i:02d}.json"
        filepath = os.path.join(SIMULATIONS_DIR, filename)
        assert os.path.exists(filepath), f"Simulation file missing: {filepath}"
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        assert data.get("conversation_id") == f"SIM-CONV-{i:02d}"
        assert "title" in data
        assert "intent_domain" in data
        assert "primary_intent" in data
        assert "customer_profile" in data
        assert "design_patterns_demonstrated" in data
        assert "anti_patterns_avoided" in data
        assert "dialogue_turns" in data
        assert len(data["dialogue_turns"]) >= 2
        assert "final_outcome" in data
        assert "audit_compliance" in data

def test_design_patterns_coverage_across_simulations():
    mandatory_patterns = {
        "Empathy-First Pattern",
        "Progressive Disclosure Pattern",
        "Confirmation-Before-Action Pattern",
        "Graceful Degradation Pattern",
        "Context Carry-Over Pattern"
    }
    
    found_patterns = set()
    for i in range(1, 21):
        filepath = os.path.join(SIMULATIONS_DIR, f"conversation_{i:02d}.json")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            found_patterns.update(data.get("design_patterns_demonstrated", []))
            
    missing_patterns = mandatory_patterns - found_patterns
    assert not missing_patterns, f"Missing required design patterns: {missing_patterns}"

def test_audit_logging_and_risk_matrix_docs_exist():
    audit_path = os.path.join(DOCS_DIR, "architecture", "audit-logging.md")
    risk_path = os.path.join(DOCS_DIR, "architecture", "risk-matrix.md")
    
    assert os.path.exists(audit_path), f"File missing: {audit_path}"
    assert os.path.exists(risk_path), f"File missing: {risk_path}"
    
    with open(audit_path, "r", encoding="utf-8") as f:
        audit_content = f.read()
        assert "interaction-audit-log.json" in audit_content
        assert "turn-audit-log.json" in audit_content
        assert "7 Years" in audit_content or "7-Year" in audit_content
        assert "AES-256" in audit_content
        
    with open(risk_path, "r", encoding="utf-8") as f:
        risk_content = f.read()
        assert "Technical Risk Matrix" in risk_content
        assert "Business Risk Matrix" in risk_content
        assert "Ethical Risk Assessment" in risk_content
        assert "TR-001" in risk_content
        assert "BR-001" in risk_content
