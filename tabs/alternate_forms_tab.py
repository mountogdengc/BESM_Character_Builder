# Alternate Form Tab

import uuid
from uuid import uuid4
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QLabel
)
from tools.utils import create_card_widget

def init_alternate_forms_tab(self):
    # Create the tab
    tab = QWidget()
    tab_layout = QVBoxLayout(tab)

    # Add title and description
    title = QLabel("Alternate Forms")
    title.setObjectName("tabTitle")
    description = QLabel("Manage your character's alternate forms. Each form represents a different physical or mental state with its own stats, attributes, and defects.")
    description.setWordWrap(True)
    tab_layout.addWidget(title)
    tab_layout.addWidget(description)

    # Create a scroll area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    tab_layout.addWidget(scroll)

    # Create a container for the alternate form cards
    self.card_container = QWidget()
    self.alternate_form_layout = QVBoxLayout(self.card_container)
    self.alternate_form_layout.setContentsMargins(8, 8, 8, 8)
    self.alternate_form_layout.setSpacing(6)
    self.alternate_form_layout.setAlignment(Qt.AlignTop)

    # Set the container as the scroll area widget
    scroll.setWidget(self.card_container)

    # Store the tab
    self.alternate_forms_tab = tab

    return tab

def sync_alternate_forms_from_attributes(self):
    # Clear existing forms
    self.character_data["alternate_forms"].clear()

    # Find all Alternate Form attributes
    for attr in self.character_data["attributes"]:
        if attr.get("base_name") == "Alternate Form":
            form_data = {
                "id": attr["id"],
                "name": attr["name"],
                "description": attr.get("description", ""),
                "cp": attr["cost"]
            }
            self.character_data["alternate_forms"].append(form_data)

    # Update the UI
    populate_alternate_form_ui(self)

def clear_alternate_form_ui(self):
    # Clear existing widgets from the layout
    if hasattr(self, 'alternate_form_layout'):
        while self.alternate_form_layout.count():
            child = self.alternate_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

def populate_alternate_form_ui(self):
    # Clear existing cards
    clear_alternate_form_ui(self)

    # Add new cards
    for form in self.character_data["alternate_forms"]:
        card = create_card_widget(
            title=form["name"],
            lines=[
                f"Description: {form['description']}",
                f"Cost: {form['cp']} CP"
            ],
            on_remove=lambda uid=form["id"]: self.remove_alternate_form(uid),
            on_click=lambda uid=form["id"]: self.edit_alternate_form(uid),
            card_type="alternate_form"
        )
        self.alternate_form_layout.insertWidget(0, card)

def remove_alternate_form(self, uid):
    """Remove an alternate form by its ID."""
    # Remove from character data
    self.character_data["alternate_forms"] = [
        form for form in self.character_data["alternate_forms"]
        if form.get("id") != uid
    ]
    
    # Remove the corresponding attribute
    self.character_data["attributes"] = [
        attr for attr in self.character_data["attributes"]
        if attr.get("id") != uid
    ]
    
    # Update the UI
    populate_alternate_form_ui(self)
    
    # Update points
    self.update_point_total()

__all__ = [
    "init_alternate_forms_tab",
    "sync_alternate_forms_from_attributes",
    "clear_alternate_form_ui",
    "populate_alternate_form_ui",
    "remove_alternate_form"
]