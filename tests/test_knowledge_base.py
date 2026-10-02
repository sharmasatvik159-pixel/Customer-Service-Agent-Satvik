import json
from pathlib import Path
import pytest

KB_FILE = Path(__file__).parent.parent / "docs" / "knowledge-base" / "sample-entries.json"

REQUIRED_FIELDS = [
    "item_id", "title", "category", "sub_category", "content",
    "version", "effective_date", "regulatory_tag", "required_auth_level",
    "ttl_seconds", "access_control_flags", "verification_metadata"
]

def test_kb_file_exists_and_valid():
    assert KB_FILE.exists(), f"File does not exist: {KB_FILE}"
    with open(KB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 50, f"Expected at least 50 knowledge base entries, got {len(data)}"

def test_kb_entries_schema_compliance():
    with open(KB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for idx, entry in enumerate(data):
        for field in REQUIRED_FIELDS:
            assert field in entry, f"Entry #{idx} ({entry.get('title', 'Unknown')}) missing field: {field}"
        
        content = entry["content"]
        assert "summary" in content
        assert "full_text" in content
        assert len(content["full_text"]) >= 50

        reg_tag = entry["regulatory_tag"]
        assert "primary_regulator" in reg_tag
        assert reg_tag["primary_regulator"] in [
            "RBI", "SEBI", "IRDAI", "NPCI", "PCI_DSS", "GOI_FINANCE", "INTERNAL_POLICY"
        ]

        ac = entry["access_control_flags"]
        assert "allowed_channels" in ac
        assert "customer_segments" in ac
        assert "is_confidential" in ac

        vm = entry["verification_metadata"]
        assert "content_owner_id" in vm
        assert "compliance_approver_id" in vm
        assert "approval_timestamp" in vm
        assert "content_hash" in vm

def test_product_lines_and_regulatory_coverage():
    with open(KB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_titles = " ".join([e["title"] for e in data])
    
    assert "NexSave" in all_titles
    assert "NexFD" in all_titles
    assert "NexCredit" in all_titles
    assert "NexHome" in all_titles
    assert "Nex Personal" in all_titles
    assert "NexProtect" in all_titles
    assert "NexInvest" in all_titles
    assert "NexGold" in all_titles

    assert "RBI" in all_titles or any(e["regulatory_tag"]["primary_regulator"] == "RBI" for e in data)
    assert "PCI DSS" in all_titles or any(e["regulatory_tag"]["primary_regulator"] == "PCI_DSS" for e in data)
    assert any("UPI" in e["title"] for e in data)
    assert any("Ombudsman" in e["title"] for e in data)
