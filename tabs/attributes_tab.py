import uuid
from uuid import uuid4
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea
)

from tools.utils import create_card_widget

def init_attributes_tab(app, layout):
    """
    Initializes the Attributes tab. Sets up a scrollable card layout
    and a button row with an Add button that calls the add_attribute method.
    """
    tab = QWidget()
    outer_layout = QVBoxLayout(tab)

    # Scroll area
    app.attributes_scroll_area = QScrollArea()
    app.attributes_scroll_area.setWidgetResizable(True)
    outer_layout.addWidget(app.attributes_scroll_area)

    # Card container and layout
    app.attr_card_container = QWidget()
    app.attributes_layout = QVBoxLayout(app.attr_card_container)
    app.attributes_layout.setContentsMargins(8, 8, 8, 8)
    app.attributes_layout.setSpacing(6)
    app.attributes_layout.setAlignment(Qt.AlignTop)

    app.attributes_scroll_area.setWidget(app.attr_card_container)

    # Add the button to the provided layout
    add_button = QPushButton("Add Attribute")
    add_button.clicked.connect(app.add_attribute)
    layout.addWidget(add_button)

    app.attributes_tab = tab
    app.tabs.addTab(tab, "Attributes")

def sync_attributes(self):
    """
    Calls populate_attributes_ui to rebuild the attribute cards from
    self.character_data['attributes'].
    """
    populate_attributes_ui(self)

def clear_attributes_ui(self):
    """
    Clears the existing card layout by destroying the old container
    and creating a fresh one.
    """
    if hasattr(self, "attr_card_container"):
        self.attr_card_container.deleteLater()

    self.attr_card_container = QWidget()
    self.attributes_layout = QVBoxLayout(self.attr_card_container)
    self.attributes_layout.setContentsMargins(8, 8, 8, 8)
    self.attributes_layout.setSpacing(6)
    self.attributes_layout.setAlignment(Qt.AlignTop)

    self.attributes_scroll_area.setWidget(self.attr_card_container)

def populate_attributes_ui(self):
    """
    Creates and inserts card widgets for each attribute in
    self.character_data['attributes'].
    """
    clear_attributes_ui(self)

    # Loop through all attributes and create a card widget for each
    for attr in self.character_data.get("attributes", []):
        # Create a unique identifier for this attribute if it doesn't have one
        if "id" not in attr:
            attr["id"] = str(uuid4())
            
        # Create the remove function for this specific attribute
        def make_remove_handler(attr_id):
            def remove_handler():
                self.remove_attribute_by_id(attr_id)
            return remove_handler
        
        # Create the edit function for this specific attribute
        def make_edit_handler(attr_id):
            def edit_handler():
                self.edit_attribute_by_id(attr_id)
            return edit_handler
        
        # Format the display lines based on attribute type
        if attr.get("base_name", attr["name"]) in ["Item", "Items"]:
            # For Items, don't show level, show total cost from all items
            items = attr.get("custom_fields", {}).get("items", [])
            total_item_cost = sum(item.get("cost", 0) for item in items)
            
            # Get list of item names
            item_names = [item.get("name", "Unnamed Item") for item in items]
            item_list = ", ".join(item_names) if item_names else "None"
            
            lines = [
                f"Cost: {total_item_cost} CP",
                f"Items: {item_list}",
                f"Enhancements: {', '.join(attr.get('enhancements', [])) or 'None'}",
                f"Limiters: {', '.join(attr.get('limiters', [])) or 'None'}"
            ]
        else:
            # For all other attributes, show normal display
            lines = [
                f"Level: {attr.get('level', 0)}",
                f"Cost: {attr.get('cost', 0)} CP"
            ]
            
            # Add official description if available
            if "description" in attr and attr["description"]:
                lines.append(f"Description: {attr['description']}")
            
            # Add enhancements and limiters
            lines.append(f"Enhancements: {', '.join(attr.get('enhancements', [])) or 'None'}")
            lines.append(f"Limiters: {', '.join(attr.get('limiters', [])) or 'None'}")
            
            # Add tags if any
            if attr.get('custom_fields') and any(attr.get('custom_fields').values()):
                lines.append(f"Tags: {', '.join(attr.get('custom_fields', {}).values())}")
                
            # Add user description if available
            if "user_description" in attr and attr["user_description"]:
                lines.append(f"Notes: {attr['user_description']}")
        
        # Create the card widget
        card = create_card_widget(
            title=attr.get("name", "Unnamed Attribute"),
            lines=lines,
            on_remove=make_remove_handler(attr["id"]),
            on_click=make_edit_handler(attr["id"]),
            card_type="attribute"
        )
        
        # Add the card to the layout
        self.attributes_layout.insertWidget(0, card)
