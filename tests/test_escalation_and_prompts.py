import json
import os
import re
import pytest

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")

def test_prompt_templates_file_exists_and_valid():
    templates_path = os.path.join(CONFIG_DIR, "prompt-templates.json")
    assert os.path.exists(templates_path), f"File not found: {templates_path}"
    
    with open(templates_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert "templates" in data
    assert len(data["templates"]) >= 15, f"Expected >= 15 templates, found {len(data['templates'])}"

def test_prompt_template_schema_and_variable_formatting():
    templates_path = os.path.join(CONFIG_DIR, "prompt-templates.json")
    with open(templates_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    required_keys = {
        "template_id", "template_name", "layer_association",
        "trigger_condition", "dynamic_variables", "template_text",
        "safety_annotations"
    }
    
    template_ids = set()
    for tpl in data["templates"]:
        missing_keys = required_keys - set(tpl.keys())
        assert not missing_keys, f"Template {tpl.get('template_id')} missing keys: {missing_keys}"
        
        assert tpl["template_id"] not in template_ids, f"Duplicate ID: {tpl['template_id']}"
        template_ids.add(tpl["template_id"])
        
        text = tpl["template_text"]
        found_placeholders = re.findall(r"\{([a-zA-Z0-9_]+)\}", text)
        for var in tpl["dynamic_variables"]:
            assert var in found_placeholders, f"Variable '{var}' listed in dynamic_variables but not found in text: {text}"

def test_all_15_escalation_triggers_specified():
    trigger_doc_path = os.path.join(DOCS_DIR, "escalation", "trigger-conditions.md")
    assert os.path.exists(trigger_doc_path), f"File not found: {trigger_doc_path}"
    
    with open(trigger_doc_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    for i in range(1, 16):
        trigger_code = f"ESC-{i:03d}"
        assert trigger_code in content, f"Trigger code {trigger_code} missing from trigger-conditions.md"

def test_system_prompt_6_layers_specified():
    spec_path = os.path.join(CONFIG_DIR, "system-prompt-spec.md")
    assert os.path.exists(spec_path), f"File not found: {spec_path}"
    
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    for layer_num in range(6):
        layer_pattern = f"Layer {layer_num}"
        assert layer_pattern in content, f"{layer_pattern} missing from system-prompt-spec.md"
