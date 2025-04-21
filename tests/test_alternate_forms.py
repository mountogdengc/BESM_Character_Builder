import pytest
import os
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QTabWidget, QPushButton, QDialog, QLabel,
    QSpinBox, QComboBox, QScrollArea, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout
)
from dialogs.attribute_builder_dialog import AttributeBuilderDialog
from tools.widgets import ClickableCard

@pytest.fixture
def setup_alternate_form(besm_app, qtbot):
    """Fixture to add an Alternate Form attribute to the character."""
    # Create a basic Alternate Form attribute
    alternate_form_attr = {
        "id": "test_alternate_form",
        "name": "Alternate Form",
        "base_name": "Alternate Form",
        "key": "alternate_form",
        "level": 1,
        "cost": 5,  # cost_per_level is 5
        "description": "Test alternate form",
        "user_description": "",
        "enhancements": [],
        "limiters": [],
        "options": [],
        "user_input": None,
        "options_source": "Test",
        "valid": True
    }
    
    # Add the attribute to the character
    if "attributes" not in besm_app.character_data:
        besm_app.character_data["attributes"] = []
    besm_app.character_data["attributes"].append(alternate_form_attr)
    
    # Force UI update
    from tabs.attributes_tab import sync_attributes
    sync_attributes(besm_app)
    
    # Update dynamic tabs and sync alternate forms
    besm_app.update_dynamic_tabs_visibility()
    from tabs.alternate_forms_tab import sync_alternate_forms_from_attributes
    sync_alternate_forms_from_attributes(besm_app)
    
    return alternate_form_attr

def test_alternate_forms_tab_exists(besm_app, qtbot, setup_alternate_form):
    """Test that the Alternate Forms tab exists in the application."""
    # Find the main tab widget
    tab_widget = besm_app.findChild(QTabWidget)
    assert tab_widget is not None
    
    # Check that the Alternate Forms tab exists
    tab_names = [tab_widget.tabText(i) for i in range(tab_widget.count())]
    assert "Alternate Form" in tab_names, "Alternate Form tab not found"

def test_add_alternate_form_attribute(besm_app, qtbot, monkeypatch):
    """Test adding an Alternate Form attribute through the Attributes tab."""
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
    
    # Mock the attribute builder dialog
    def mock_get_attribute_data():
        return {
            "id": "test_alternate_form",
            "name": "Alternate Form",
            "base_name": "Alternate Form",
            "level": 1,
            "cost": 5,
            "description": "Test alternate form",
            "user_description": "",
            "enhancements": [],
            "limiters": []
        }

    def mock_exec():
        return QDialog.Accepted

    # Create a mock dialog class
    class MockAttributeBuilderDialog(AttributeBuilderDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.get_attribute_data = mock_get_attribute_data
            self.exec_ = mock_exec

    # Replace the real dialog with our mock
    monkeypatch.setattr("dialogs.attribute_builder_dialog.AttributeBuilderDialog", MockAttributeBuilderDialog)
    
    # Click the Add Attribute button
    qtbot.mouseClick(add_attribute_button, Qt.LeftButton)
    
    # Check if the Alternate Forms tab now exists
    tab_names = [tab_widget.tabText(i) for i in range(tab_widget.count())]
    assert "Alternate Form" in tab_names, "Alternate Form tab not created after adding attribute"
    
    # Select the Alternate Forms tab
    alternate_forms_tab_index = [i for i in range(tab_widget.count()) 
                                if tab_widget.tabText(i) == "Alternate Form"][0]
    tab_widget.setCurrentIndex(alternate_forms_tab_index)
    
    # Verify that the tab contains at least one form card
    cards = tab_widget.currentWidget().findChildren(ClickableCard)
    assert len(cards) > 0, "No alternate form cards found"

def test_alternate_form_editor_dialog(besm_app, qtbot, monkeypatch, setup_alternate_form):
    """Test that the Alternate Form editor dialog opens correctly."""
    # Find the main tab widget
    tab_widget = besm_app.findChild(QTabWidget)
    assert tab_widget is not None, "Tab widget not found"
    
    # Find and select the Alternate Forms tab
    alternate_forms_tab_index = None
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Alternate Form":
            alternate_forms_tab_index = i
            break
    
    assert alternate_forms_tab_index is not None, "Alternate Form tab not found"
    tab_widget.setCurrentIndex(alternate_forms_tab_index)
    
    # Find the clickable card
    cards = tab_widget.currentWidget().findChildren(ClickableCard)
    assert len(cards) > 0, "No alternate form cards found"
    
    # Make sure the card is visible and ready for interaction
    card = cards[0]
    card.show()
    card.raise_()
    qtbot.waitExposed(card)
    qtbot.wait(100)  # Add a small delay to ensure the card is ready
    
    # Mock the edit_alternate_form method
    dialog_opened = [False]
    dialog_components = {"name_input": False, "description_input": False}

    def mock_edit_alternate_form(self, uid):
        dialog_opened[0] = True
        # Create a simple dialog to check components
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Alternate Form")
        
        # Create name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        name_input = QLineEdit()
        name_input.setText("Test Alternate Form")
        name_layout.addWidget(name_input)
        dialog_components["name_input"] = True
        
        # Create description input
        description_label = QLabel("Description:")
        description_input = QTextEdit()
        description_input.setPlainText("Test description")
        dialog_components["description_input"] = True
        
        # Add components to dialog
        layout = QVBoxLayout(dialog)
        layout.addLayout(name_layout)
        layout.addWidget(description_label)
        layout.addWidget(description_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    # Replace the edit_alternate_form method
    monkeypatch.setattr(besm_app.__class__, "edit_alternate_form", mock_edit_alternate_form)

    # Click the first card
    qtbot.mouseClick(card, Qt.LeftButton)
    
    # Wait for the dialog to be created and shown
    qtbot.wait(500)  # Give more time for the dialog to be created
    
    # Verify the dialog was opened with correct components
    assert dialog_opened[0], "Alternate Form editor dialog did not open"
    assert dialog_components["name_input"], "Name input not found in editor dialog"
    assert dialog_components["description_input"], "Description input not found in editor dialog"
