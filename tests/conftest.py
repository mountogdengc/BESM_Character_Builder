import os
import sys
import json
import pytest
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Add the parent directory to sys.path to allow imports from the main application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# This fixture provides a QApplication instance for each test
@pytest.fixture(scope='session')
def qapp():
    """Create a QApplication instance for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    
# This fixture provides a clean application state for each test
@pytest.fixture
def besm_app(qapp, monkeypatch):
    """Create a fresh BESMCharacterApp instance for each test."""
    # Patch sys.exit to prevent the app from exiting during tests
    monkeypatch.setattr(sys, 'exit', lambda *args: None)
    
    # Patch QMessageBox to automatically accept any confirmations
    def mock_question(*args, **kwargs):
        return QMessageBox.Yes
    monkeypatch.setattr(QMessageBox, "question", mock_question)
    
    def mock_information(*args, **kwargs):
        return QMessageBox.Ok
    monkeypatch.setattr(QMessageBox, "information", mock_information)
    
    def mock_critical(*args, **kwargs):
        return QMessageBox.Ok
    monkeypatch.setattr(QMessageBox, "critical", mock_critical)
    
    # Import here to avoid circular imports
    from besm_app import BESMCharacterApp
    
    # Create a new instance of the application
    app_instance = BESMCharacterApp()
    
    # Show the window to make it visible for testing
    app_instance.show()
    
    # Return the app instance for testing
    yield app_instance
    
    # Clean up after the test
    app_instance.close()

@pytest.fixture
def template_paths():
    """Fixture to provide paths to template files."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_path = os.path.join(base_path, "data", "templates")
    
    return {
        "base": template_path,
        "index": os.path.join(template_path, "index.json"),
        "races": os.path.join(template_path, "races"),
        "sizes": os.path.join(template_path, "sizes"),
        "classes": os.path.join(template_path, "classes")
    }

@pytest.fixture
def attribute_data():
    """Fixture to provide attribute data from attributes.json."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    with open(os.path.join(base_path, "data", "attributes.json"), "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def special_attributes():
    """Fixture to provide a list of special attributes that have their own tabs."""
    return [
        "Alternate Form",
        "Companion", 
        "Item",
        "Metamorphosis",
        "Minion"
    ]

@pytest.fixture
def setup_alternate_form():
    """Fixture to provide a basic Alternate Form attribute for testing."""
    return {
        "id": "test-alternate-form",
        "name": "Alternate Form",
        "base_name": "Alternate Form",
        "level": 1,
        "cost": 5,
        "description": "Test alternate form that allows character transformation",
        "user_description": "A test alternate form",
        "enhancements": [],
        "limiters": [],
        "options": {},
        "user_input": {},
        "options_source": None,
        "valid": True
    }
