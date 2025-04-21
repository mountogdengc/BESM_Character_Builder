import uuid
from uuid import uuid4
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea
)

from tools.utils import create_card_widget

def init_defects_tab(app, layout):
    """
    Initializes the defects tab. Sets up a scrollable card layout
    and a button row with an Add button that calls the add_defect method.
    """
    # Scroll area
    app.defects_scroll_area = QScrollArea()
    app.defects_scroll_area.setWidgetResizable(True)
    layout.addWidget(app.defects_scroll_area)

    # Card container and layout
    app.defect_card_container = QWidget()
    app.defects_layout = QVBoxLayout(app.defect_card_container)
    app.defects_layout.setContentsMargins(8, 8, 8, 8)
    app.defects_layout.setSpacing(6)
    app.defects_layout.setAlignment(Qt.AlignTop)

    app.defects_scroll_area.setWidget(app.defect_card_container)
    
    # Make sure we have a defects list in character_data
    if not hasattr(app, 'character_data') or 'defects' not in app.character_data:
        app.character_data['defects'] = []

def sync_defects(self):
    """
    Calls populate_defects_ui to rebuild the defect cards from
    self.character_data['defects'].
    """
    print(f"sync_defects called. Defects in character data: {len(self.character_data.get('defects', []))}")
    # Ensure character_data has a defects list
    if 'defects' not in self.character_data:
        self.character_data['defects'] = []
    
    # Debug the defects data
    for i, defect in enumerate(self.character_data.get('defects', [])):
        print(f"[DEBUG] Checking defect: {defect.get('name', 'Unnamed')} (Rank: {defect.get('rank', 0)}), details: {defect.get('details', '')}, sources: {defect.get('sources', [])}")
    
    # Rebuild the UI
    populate_defects_ui(self)

def clear_defects_ui(self):
    """
    Clears the existing card layout by destroying the old container
    and creating a fresh one.
    """
    print("clear_defects_ui called")
    
    # First, check if we have the defect_card_container
    if hasattr(self, "defect_card_container") and self.defect_card_container is not None:
        print("Clearing defect_card_container")
        # Remove all widgets from the layout
        if self.defect_card_container.layout() is not None:
            layout = self.defect_card_container.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
    else:
        print("Creating new defect_card_container")
        self.defect_card_container = QWidget()
        self.defects_layout = QVBoxLayout(self.defect_card_container)
        self.defects_layout.setContentsMargins(8, 8, 8, 8)
        self.defects_layout.setSpacing(6)
        self.defects_layout.setAlignment(Qt.AlignTop)
        
        if hasattr(self, "defects_scroll_area") and self.defects_scroll_area is not None:
            print("Setting defect_card_container as widget for defects_scroll_area")
            self.defects_scroll_area.setWidget(self.defect_card_container)

def populate_defects_ui(self):
    """
    Creates and inserts card widgets for each defect in
    self.character_data['defects'].
    """
    print("populate_defects_ui called")
    clear_defects_ui(self)
    print(f"UI cleared. Creating cards for {len(self.character_data.get('defects', []))} defects")

    # Loop through all defects and create a card widget for each
    for defect in self.character_data.get("defects", []):
        print(f"Creating card for defect: {defect.get('name', 'Unnamed')}")
        
        # Create a unique identifier for this defect if it doesn't have one
        if "id" not in defect:
            defect["id"] = str(uuid4())
            
        # Create the remove function for this specific defect
        def make_remove_handler(defect_id):
            def remove_handler():
                self.remove_defect_by_id(defect_id)
            return remove_handler
        
        # Create the edit function for this specific defect
        def make_edit_handler(defect_id):
            def edit_handler():
                self.edit_defect_by_id(defect_id)
            return edit_handler
        
        lines = [
            f"Rank: {defect.get('rank', 0)}",
            f"Cost: {defect.get('cost', 0)} CP",
            f"Enhancements: {', '.join(defect.get('enhancements', [])) or 'None'}",
            f"Limiters: {', '.join(defect.get('limiters', [])) or 'None'}",
            f"Tags: {', '.join(defect.get('custom_fields', {}).values()) or 'None'}"
        ]
        
        card = create_card_widget(
            title=defect.get("name", "Unnamed Defect"),
            lines=lines,
            style="padding: 12px;",
            on_remove=make_remove_handler(defect["id"]),
            on_click=make_edit_handler(defect["id"]),
            card_type="defect"
        )
        
        # Add the card to the layout
        if hasattr(self, 'defects_layout') and self.defects_layout is not None:
            print("Adding card to defects_layout")
            self.defects_layout.insertWidget(0, card)
            print("Card added successfully")
        elif hasattr(self, 'defect_card_container') and self.defect_card_container is not None:
            layout = self.defect_card_container.layout()
            if layout is not None:
                print("Adding card to defect_card_container layout")
                layout.insertWidget(0, card)
                print("Card added successfully")
            else:
                print("ERROR: defect_card_container has no layout!")
        else:
            print("ERROR: No suitable layout found for adding defect card!")
