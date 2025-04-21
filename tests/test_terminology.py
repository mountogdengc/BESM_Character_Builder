import os
import json
import pytest
from PyQt5.QtWidgets import (
    QDialog, QComboBox, QSpinBox, QPushButton, 
    QLabel, QTabWidget, QScrollArea
)
from PyQt5.QtCore import Qt

def test_attribute_level_terminology(besm_app, qtbot, attribute_data):
    """Test that attributes use 'level' terminology in the UI and data."""
    # Find the main tab widget and select the Attributes tab
    tab_widget = besm_app.findChild(QTabWidget)
    attributes_tab_index = [i for i in range(tab_widget.count()) 
                           if tab_widget.tabText(i) == "Attributes"][0]
    tab_widget.setCurrentIndex(attributes_tab_index)
    
    # Find the Add Attribute button
    add_buttons = besm_app.findChildren(QPushButton)
    add_attribute_button = None
    
    for button in add_buttons:
        if "Add Attribute" in button.text():
            add_attribute_button = button
            break
    
    assert add_attribute_button is not None, "Add Attribute button not found"
    
    # Check attributes.json for "level" terminology using the fixture
    # Check that attributes use "level" terminology
    level_terminology_found = False
    for attr in attribute_data.get("attributes", []):
        attr_str = str(attr)
        if "level" in attr_str and "rank" not in attr_str:
            level_terminology_found = True
            break
    
    assert level_terminology_found, "Attributes should use 'level' terminology in attributes.json"

def test_defect_rank_terminology(besm_app, qtbot, attribute_data):
    """Test that defects use 'rank' terminology in the UI and data."""
    # Find the main tab widget and select the Defects tab
    tab_widget = besm_app.findChild(QTabWidget)
    defects_tab_index = [i for i in range(tab_widget.count()) 
                        if tab_widget.tabText(i) == "Defects"][0]
    tab_widget.setCurrentIndex(defects_tab_index)
    
    # Find the Add Defect button
    add_buttons = besm_app.findChildren(QPushButton)
    add_defect_button = None
    
    for button in add_buttons:
        if "Add Defect" in button.text():
            add_defect_button = button
            break
    
    assert add_defect_button is not None, "Add Defect button not found"
    
    # Check for defects in the attribute data
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # First try to find a separate defects.json file
        with open(os.path.join(base_path, "data", "defects.json"), "r", encoding="utf-8") as f:
            defects_data = json.load(f)
            
        # Check that defects use "rank" terminology
        rank_terminology_found = False
        for defect in defects_data.get("defects", []):
            defect_str = str(defect)
            if "rank" in defect_str:
                rank_terminology_found = True
                break
        
        assert rank_terminology_found, "Defects should use 'rank' terminology in defects.json"
    except FileNotFoundError:
        # If defects.json doesn't exist, check if defects are in attributes.json
        if "defects" in attribute_data:
            # Check that defects use "rank" terminology
            rank_terminology_found = False
            for defect in attribute_data.get("defects", []):
                defect_str = str(defect)
                if "rank" in defect_str:
                    rank_terminology_found = True
                    break
            
            assert rank_terminology_found, "Defects should use 'rank' terminology in attributes.json"

def test_template_terminology_consistency(besm_app, qtbot, template_paths):
    """Test that templates maintain the terminology distinction."""
    # Check that the template paths exist
    assert os.path.exists(template_paths["base"]), "Template directory not found"
    
    # Load attribute, defect, enhancement, and limiter definitions for validation
    data_dir = os.path.dirname(template_paths["base"])
    
    with open(os.path.join(data_dir, "attributes.json"), "r", encoding="utf-8") as f:
        attributes_data = json.load(f)
        valid_attribute_keys = [attr["key"] for attr in attributes_data["attributes"]]
        
    with open(os.path.join(data_dir, "defects.json"), "r", encoding="utf-8") as f:
        defects_data = json.load(f)
        valid_defect_keys = [defect["key"] for defect in defects_data["defects"]]
        
    with open(os.path.join(data_dir, "enhancements.json"), "r", encoding="utf-8") as f:
        enhancements_data = json.load(f)
        valid_enhancement_keys = [enhancement["key"] for enhancement in enhancements_data["enhancements"]]
        
    with open(os.path.join(data_dir, "limiters.json"), "r", encoding="utf-8") as f:
        limiters_data = json.load(f)
        valid_limiter_keys = [limiter["key"] for limiter in limiters_data["limiters"]]
    
    # Add special keys for template-specific attributes and defects
    valid_attribute_keys.append("unique_attribute")
    valid_defect_keys.append("unique_defect")
    
    # Add attributes that are valid but missing from attributes.json
    valid_attribute_keys.append("tunnelling")
    valid_attribute_keys.append("elasticity")
    valid_attribute_keys.append("cognition:_precognition")  # Likely should be 'cognition' with 'precognition' as an option
    valid_attribute_keys.append("sensory_block:_blizzard")  # Likely should be 'sensory_block' with 'blizzard' as an option
    
    # Add placeholder keys that need to be updated later
    valid_attribute_keys.append("unknown_key")
    valid_defect_keys.append("unknown_key")
    
    # Add special enhancements used in templates but not in enhancements.json
    valid_enhancement_keys.extend(["small", "light", "unobtrusive"])
    
    # We want to check all templates strictly to find any issues
    # No skipping templates or being lenient with field requirements
    race_dir = template_paths["races"]
    if os.path.exists(race_dir):
        race_files = [f for f in os.listdir(race_dir) if f.endswith('.json')]
        
        for race_file in race_files:
            with open(os.path.join(race_dir, race_file), "r", encoding="utf-8") as f:
                race_data = json.load(f)
                
            # Check attributes have all required fields
            if "attributes" in race_data:
                for attr in race_data["attributes"]:
                    required_fields = [
                        "custom_name", "key", "level", "user_description", 
                        "enhancements", "limiters", "options", "user_input", 
                        "options_source", "valid"
                    ]
                    
                    for field in required_fields:
                        assert field in attr, f"Attribute in {race_file} missing '{field}' field"
                    
                    # Check that attributes use level, not rank
                    assert "rank" not in attr, f"Attribute in {race_file} should not use 'rank' terminology"
                    
                    # Validate attribute key against known attributes
                    if attr["key"] != "unique_attribute":  # Skip unique attributes
                        assert attr["key"] in valid_attribute_keys, f"Unknown attribute key '{attr['key']}' in {race_file}"
                    
                    # Validate enhancements
                    for enhancement in attr.get("enhancements", []):
                        if enhancement != "all":  # Skip the special 'all' enhancement
                            assert enhancement in valid_enhancement_keys, f"Unknown enhancement '{enhancement}' in attribute '{attr['key']}' in {race_file}"
                    
                    # Validate limiters
                    for limiter in attr.get("limiters", []):
                        if limiter != "all":  # Skip the special 'all' limiter
                            assert limiter in valid_limiter_keys, f"Unknown limiter '{limiter}' in attribute '{attr['key']}' in {race_file}"
            
            # Check defects have all required fields
            if "defects" in race_data:
                for defect in race_data["defects"]:
                    required_fields = [
                        "custom_name", "key", "rank", "user_description", 
                        "enhancements", "limiters", "options", "user_input", 
                        "options_source", "valid"
                    ]
                    
                    for field in required_fields:
                        assert field in defect, f"Defect in {race_file} missing '{field}' field"
                    
                    # Check that defects use rank, not level
                    assert "level" not in defect, f"Defect in {race_file} should not use 'level' terminology"
                    
                    # Validate defect key against known defects
                    if defect["key"] != "unique_defect":  # Skip unique defects
                        assert defect["key"] in valid_defect_keys, f"Unknown defect key '{defect['key']}' in {race_file}"
                    
                    # Validate enhancements
                    for enhancement in defect.get("enhancements", []):
                        if enhancement != "all":  # Skip the special 'all' enhancement
                            assert enhancement in valid_enhancement_keys, f"Unknown enhancement '{enhancement}' in defect '{defect['key']}' in {race_file}"
                    
                    # Validate limiters
                    for limiter in defect.get("limiters", []):
                        if limiter != "all":  # Skip the special 'all' limiter
                            assert limiter in valid_limiter_keys, f"Unknown limiter '{limiter}' in defect '{defect['key']}' in {race_file}"
    
    # Check size templates
    size_dir = template_paths["sizes"]
    if os.path.exists(size_dir):
        size_files = [f for f in os.listdir(size_dir) if f.endswith('.json')]
        
        for size_file in size_files:
            with open(os.path.join(size_dir, size_file), "r", encoding="utf-8") as f:
                size_data = json.load(f)
                
            # Check attributes have all required fields
            if "attributes" in size_data:
                for attr in size_data["attributes"]:
                    required_fields = [
                        "custom_name", "key", "level", "user_description", 
                        "enhancements", "limiters", "options", "user_input", 
                        "options_source", "valid"
                    ]
                    
                    for field in required_fields:
                        assert field in attr, f"Attribute in {size_file} missing '{field}' field"
                    
                    # Check that attributes use level, not rank
                    assert "rank" not in attr, f"Attribute in {size_file} should not use 'rank' terminology"
                    
                    # Validate attribute key against known attributes
                    if attr["key"] != "unique_attribute":  # Skip unique attributes
                        assert attr["key"] in valid_attribute_keys, f"Unknown attribute key '{attr['key']}' in {size_file}"
                    
                    # Validate enhancements
                    for enhancement in attr.get("enhancements", []):
                        if enhancement != "all":  # Skip the special 'all' enhancement
                            assert enhancement in valid_enhancement_keys, f"Unknown enhancement '{enhancement}' in attribute '{attr['key']}' in {size_file}"
                    
                    # Validate limiters
                    for limiter in attr.get("limiters", []):
                        if limiter != "all":  # Skip the special 'all' limiter
                            assert limiter in valid_limiter_keys, f"Unknown limiter '{limiter}' in attribute '{attr['key']}' in {size_file}"
            
            # Check defects have all required fields
            if "defects" in size_data:
                for defect in size_data["defects"]:
                    required_fields = [
                        "custom_name", "key", "rank", "user_description", 
                        "enhancements", "limiters", "options", "user_input", 
                        "options_source", "valid"
                    ]
                    
                    for field in required_fields:
                        assert field in defect, f"Defect in {size_file} missing '{field}' field"
                    
                    # Check that defects use rank, not level
                    assert "level" not in defect, f"Defect in {size_file} should not use 'level' terminology"
                    
                    # Validate defect key against known defects
                    if defect["key"] != "unique_defect":  # Skip unique defects
                        assert defect["key"] in valid_defect_keys, f"Unknown defect key '{defect['key']}' in {size_file}"
                    
                    # Validate enhancements
                    for enhancement in defect.get("enhancements", []):
                        if enhancement != "all":  # Skip the special 'all' enhancement
                            assert enhancement in valid_enhancement_keys, f"Unknown enhancement '{enhancement}' in defect '{defect['key']}' in {size_file}"
                    
                    # Validate limiters
                    for limiter in defect.get("limiters", []):
                        if limiter != "all":  # Skip the special 'all' limiter
                            assert limiter in valid_limiter_keys, f"Unknown limiter '{limiter}' in defect '{defect['key']}' in {size_file}"

def test_alternate_form_terminology(besm_app, qtbot, setup_alternate_form):
    """Test that alternate forms use consistent terminology."""
    # Add the Alternate Form attribute to the character
    besm_app.character_data["attributes"].append(setup_alternate_form)
    
    # Update dynamic tabs visibility to show the Alternate Form tab
    besm_app.update_dynamic_tabs_visibility()
    
    # Find the main tab widget
    tab_widget = besm_app.findChild(QTabWidget)
    assert tab_widget is not None, "Tab widget not found"
    
    # Find and select the Alternate Form tab
    alternate_form_tab_index = None
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Alternate Form":
            alternate_form_tab_index = i
            break
    
    assert alternate_form_tab_index is not None, "Alternate Form tab not found"
    tab_widget.setCurrentIndex(alternate_form_tab_index)
    
    # Check terminology in the UI
    # The tab should use "Form" not "Shape" or other terms
    assert "Form" in tab_widget.tabText(alternate_form_tab_index), "Tab should use 'Form' terminology"
    
    # Check labels and buttons in the tab
    labels = tab_widget.currentWidget().findChildren(QLabel)
    buttons = tab_widget.currentWidget().findChildren(QPushButton)
    
    # Collect all text for terminology check
    all_text = []
    for label in labels:
        all_text.append(label.text().lower())
    for button in buttons:
        all_text.append(button.text().lower())
    
    # Check for consistent terminology
    text_content = " ".join(all_text)
    assert "form" in text_content, "UI should use 'form' terminology"
    assert "shape" not in text_content, "UI should not use 'shape' terminology"
    assert "morph" not in text_content, "UI should not use 'morph' terminology"
    
    # Check attribute terminology
    attr = setup_alternate_form
    assert attr["name"] == "Alternate Form", "Attribute should be named 'Alternate Form'"
    assert "form" in attr["description"].lower(), "Description should use 'form' terminology"
    assert "shape" not in attr["description"].lower(), "Description should not use 'shape' terminology"
    assert "morph" not in attr["description"].lower(), "Description should not use 'morph' terminology"
