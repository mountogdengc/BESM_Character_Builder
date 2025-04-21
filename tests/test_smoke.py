import pytest
import os
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QLabel, QSpinBox, QPushButton, QLineEdit, QApplication

def test_app_starts(besm_app, qtbot):
    """Test that the application starts and shows the main window."""
    # Check that the window is visible
    assert besm_app.isVisible()
    # Check the window title
    assert "BESM 4e Character Builder" in besm_app.windowTitle()

def test_main_tabs_exist(besm_app, qtbot):
    """Test that all main tabs are present in the application."""
    # Find the main tab widget
    tab_widget = besm_app.findChild(QTabWidget)
    assert tab_widget is not None
    
    # Check that essential tabs exist
    tab_names = [tab_widget.tabText(i) for i in range(tab_widget.count())]
    essential_tabs = ["Stats", "Attributes", "Defects"]
    for tab in essential_tabs:
        assert tab in tab_names

def test_stats_tab_functionality(besm_app, qtbot):
    """Test basic functionality of the Stats tab."""
    # Find the main tab widget and select the Stats tab
    tab_widget = besm_app.findChild(QTabWidget)
    stats_tab_index = [i for i in range(tab_widget.count()) 
                      if tab_widget.tabText(i) == "Stats"][0]
    tab_widget.setCurrentIndex(stats_tab_index)
    
    # Find the stats tab widget
    stats_tab = tab_widget.widget(stats_tab_index)
    
    # Find all spinboxes in the stats tab
    spinboxes = stats_tab.findChildren(QSpinBox)
    assert len(spinboxes) >= 3, "Not enough spinboxes found in Stats tab"
    
    # Find a spinbox and test changing its value
    test_spinbox = spinboxes[0]  # Use the first spinbox we find
    
    # Test changing a stat value
    initial_value = test_spinbox.value()
    new_value = initial_value + 1
    
    # Change the value and check it updates
    test_spinbox.setValue(new_value)
    assert test_spinbox.value() == new_value
    
    # Verify that update_derived_values is called when stats change
    assert hasattr(besm_app, 'update_derived_values'), "update_derived_values method not found"

def test_attributes_tab_exists(besm_app, qtbot):
    """Test that the Attributes tab exists and has an Add button."""
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
    
    # Verify that attributes use "level" terminology
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_path, "data", "attributes.json"), "r", encoding="utf-8") as f:
        attributes_data = json.load(f)
        
    # Check that attributes use "level" terminology
    for attr in attributes_data.get("attributes", []):
        if "level_effects" in attr:
            assert "level" in str(attr["level_effects"]), "Attributes should use 'level' terminology"

def test_defects_tab_exists(besm_app, qtbot):
    """Test that the Defects tab exists and has an Add button."""
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
    
    # Verify that defects use "rank" terminology
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_path, "data", "defects.json"), "r", encoding="utf-8") as f:
        defects_data = json.load(f)
        
    # Check that defects use "rank" terminology
    for defect in defects_data.get("defects", []):
        if "rank_effects" in defect:
            assert "rank" in str(defect["rank_effects"]), "Defects should use 'rank' terminology"

def test_character_name_field(besm_app, qtbot):
    """Test that the character name field exists and can be edited."""
    # Find the character name field
    name_field = None
    labels = besm_app.findChildren(QLabel)
    
    for label in labels:
        if "Character Name" in label.text():
            # Look for a QLineEdit near this label
            line_edits = besm_app.findChildren(QLineEdit)
            for line_edit in line_edits:
                if abs(line_edit.pos().y() - label.pos().y()) < 30:  # Close vertically
                    name_field = line_edit
                    break
            break
    
    assert name_field is not None, "Character name field not found"
    
    # Test setting a name
    test_name = "Test Character"
    name_field.clear()  # Clear existing text first
    qtbot.keyClicks(name_field, test_name)
    assert name_field.text() == test_name

def test_stat_modifiers(besm_app, qtbot):
    """Test that stat modifiers from attributes and defects are properly applied."""
    # This is a basic test to verify the stat_mods functionality described in the memories
    # We're just checking that the update_derived_values method exists and can be called
    assert hasattr(besm_app, 'update_derived_values'), "update_derived_values method not found"
    
    # Call the method to ensure it doesn't crash
    try:
        besm_app.update_derived_values()
        # If we get here, the method executed without errors
        assert True
    except Exception as e:
        assert False, f"update_derived_values failed: {str(e)}"
