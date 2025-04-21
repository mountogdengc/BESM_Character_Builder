import pytest
import os
import json
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (
    QComboBox, QPushButton, QMessageBox,
    QDialog, QVBoxLayout, QLabel
)

def test_template_loading(besm_app, qtbot):
    """Test that templates are loaded correctly from the new directory structure."""
    # Check that the template manager has loaded templates
    assert hasattr(besm_app, 'template_manager'), "Template manager not initialized"
    
    # Check that race templates are loaded
    race_templates = getattr(besm_app.template_manager, 'race_templates', [])
    assert len(race_templates) > 0, "No race templates loaded"
    
    # Check that size templates are loaded
    size_templates = getattr(besm_app.template_manager, 'size_templates', [])
    assert len(size_templates) > 0, "No size templates loaded"
    
    # Verify at least one specific template we know exists
    android_template_found = False
    for template in race_templates:
        if template.get('race_name') == 'Android Battle Maid' or template.get('key') == 'android_battle_maid':
            android_template_found = True
            break
    
    assert android_template_found, "Android Battle Maid template not found"

def test_template_structure(besm_app, qtbot):
    """Test that templates follow the expected structure with proper fields."""
    # Get the base path
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_path, "data", "templates")
    
    # Check that the index.json file exists
    index_path = os.path.join(template_path, "index.json")
    assert os.path.exists(index_path), "Template index.json not found"
    
    # Load the index file
    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    
    # Check that the index has the expected structure
    assert "races" in index_data, "Races not found in template index"
    assert "sizes" in index_data, "Sizes not found in template index"
    assert isinstance(index_data["races"], list), "Races should be a list"
    assert isinstance(index_data["sizes"], list), "Sizes should be a list"
    
    # Check a race template
    if index_data["races"]:
        race_name = index_data["races"][0]
        race_path = os.path.join(template_path, "races", f"{race_name}.json")
        assert os.path.exists(race_path), f"Race template {race_name}.json not found"
        
        with open(race_path, "r", encoding="utf-8") as f:
            race_data = json.load(f)
        
        # Check required fields
        assert "race_name" in race_data, "race_name field missing in race template"
        assert "key" in race_data, "key field missing in race template"
        
        # Check attributes structure if present
        if "attributes" in race_data:
            for attr in race_data["attributes"]:
                assert "key" in attr, "key field missing in attribute"
                assert "level" in attr, "level field missing in attribute"
        
        # Check defects structure if present
        if "defects" in race_data:
            for defect in race_data["defects"]:
                assert "key" in defect, "key field missing in defect"
                assert "rank" in defect, "rank field missing in defect"
    
    # Check a size template
    if index_data["sizes"]:
        size_name = index_data["sizes"][0]
        size_path = os.path.join(template_path, "sizes", f"{size_name}.json")
        assert os.path.exists(size_path), f"Size template {size_name}.json not found"
        
        with open(size_path, "r", encoding="utf-8") as f:
            size_data = json.load(f)
        
        # Check for stat_mods or modifiers in size templates
        assert ("stat_mods" in size_data or "modifiers" in size_data), "Neither stat_mods nor modifiers field found in size template"

def test_apply_template(besm_app, qtbot, monkeypatch):
    """Test applying a template to a character."""
    # Find the race template button
    template_button = None
    buttons = besm_app.findChildren(QPushButton)
    
    for button in buttons:
        if "Race Templates" in button.text():
            template_button = button
            break
    
    assert template_button is not None, "Race template button not found"
    
    # Mock QMessageBox to automatically accept any confirmations
    def mock_question(*args, **kwargs):
        return QMessageBox.Yes
        
    def mock_exec(*args, **kwargs):
        # Simulate selecting and applying the Android template
        # This assumes the template dialog will be mocked or handled appropriately
        from templates.template_manager import apply_template_to_character
        
        # Find the Android template in the template manager
        android_template = None
        for template in besm_app.template_manager.race_templates:
            if "ANDROID BATTLE MAID" in template.get("race_name", "") or "android_battle_maid" in template.get("key", ""):
                android_template = template
                break
                
        assert android_template is not None, "Android Battle Maid template not found in template manager"
        
        # Apply the template
        success = apply_template_to_character(besm_app, android_template, "race")
        assert success, "Failed to apply Android Battle Maid template"
        return QMessageBox.Accepted
    
    monkeypatch.setattr(QMessageBox, "question", mock_question)
    monkeypatch.setattr("templates.template_manager.TemplateDialog.exec_", mock_exec)
    
    # Click the template button
    qtbot.mouseClick(template_button, Qt.LeftButton)
    
    # Check that attributes were added
    assert len(besm_app.character_data.get("attributes", [])) > 0, "No attributes added after applying template"
    
    # Check for Android-specific attributes
    android_attrs_found = False
    for attr in besm_app.character_data.get("attributes", []):
        if attr.get("name") == "Resilient" or attr.get("key") == "resilient":
            android_attrs_found = True
            break
    
    assert android_attrs_found, "Android-specific attributes not found after applying template"
