# items_tab

import uuid
from uuid import uuid4
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy, QMessageBox
)
from tools.utils import create_card_widget
from dialogs.item_builder_dialog import ItemBuilderDialog

def init_items_tab(self):
    tab = QWidget()
    outer_layout = QVBoxLayout(tab)

    # Scroll area
    self.items_scroll_area = QScrollArea()
    self.items_scroll_area.setWidgetResizable(True)
    outer_layout.addWidget(self.items_scroll_area)

    # Card container and layout
    self.items_card_container = QWidget()
    self.items_layout = QVBoxLayout(self.items_card_container)
    self.items_layout.setContentsMargins(8, 8, 8, 8)
    self.items_layout.setSpacing(6)
    self.items_layout.setAlignment(Qt.AlignTop)

    self.items_scroll_area.setWidget(self.items_card_container)

    # No Add button - items are created when the Item attribute is added

    self.items_tab = tab
    self.tabs.addTab(tab, "Items")

def sync_items_from_attributes(self):
    self.character_data["items"].clear()
    clear_items_ui(self)

    for attr in self.character_data["attributes"]:
        # Check for both singular and plural forms of the attribute name
        if attr.get("base_name", attr["name"]) in ["Item", "Items"]:
            # Ensure the attribute has an ID
            if "id" not in attr:
                attr["id"] = str(uuid4())
                
            attr_id = attr["id"]
            
            # Get all items from the attribute's custom fields
            stored_items = attr.get("custom_fields", {}).get("items", [])
            
            # If there are no stored items yet, create a default one
            if not stored_items:
                item_name = attr.get("custom_fields", {}).get("item_name", "New Item")
                item_id = str(uuid4())
                item_data = {
                    "id": item_id,
                    "name": item_name,
                    "description": attr.get("custom_fields", {}).get("item_description", ""),
                    "cost": 0,  # Initial cost is 0
                    "attributes": [],
                    "defects": [],
                    "total_cp": 0,
                    "parent_attribute_id": attr_id  # Connect to parent attribute
                }
                self.character_data["items"].append(item_data)
            else:
                # Add all stored items to the character data
                for item in stored_items:
                    # Ensure the item has an ID
                    if "id" not in item:
                        item["id"] = str(uuid4())
                    
                    # Calculate the item cost (half of total CP, rounded down)
                    total_cp = item.get("total_cp", 0)
                    item_cost = max(0, total_cp // 2)  # Integer division to round down
                    
                    # Create a copy of the item with the calculated cost
                    item_data = item.copy()
                    item_data["cost"] = item_cost
                    item_data["parent_attribute_id"] = attr_id  # Connect to parent attribute
                    
                    self.character_data["items"].append(item_data)

    populate_items_ui(self)

def clear_items_ui(self):
    # Delete old layout by replacing the card container entirely
    if hasattr(self, "items_card_container"):
        self.items_card_container.deleteLater()

    # Create a new container and layout
    from PyQt5.QtWidgets import QWidget, QVBoxLayout

    self.items_card_container = QWidget()
    self.items_layout = QVBoxLayout(self.items_card_container)
    self.items_layout.setContentsMargins(8, 8, 8, 8)
    self.items_layout.setSpacing(6)
    self.items_layout.setAlignment(Qt.AlignTop)

    self.items_scroll_area.setWidget(self.items_card_container)

def populate_items_ui(self):
    clear_items_ui(self)
    for item in self.character_data["items"]:
        lines = []

        # Basic info - show the final CP cost (half of total CP, rounded down)
        total_cp = item.get('total_cp', 0)
        item_cost = max(0, total_cp // 2)  # Integer division to round down, minimum 0
        lines.append(f"Item Cost: {item_cost} CP")
        
        if item.get("description"):
            lines.append(f"Description: {item['description']}")

        # Attributes/Defects summary
        attr_names = [a["name"] for a in item.get("attributes", [])]
        defect_names = [d["name"] for d in item.get("defects", [])]

        if attr_names:
            lines.append("Attributes: " + ", ".join(attr_names))
        if defect_names:
            lines.append("Defects: " + ", ".join(defect_names))

        card = create_card_widget(
            title=item["name"],
            lines=lines,
            on_click=lambda uid=item["id"]: self.edit_item(uid)
        )
        self.items_layout.insertWidget(0, card)

def edit_item(self, item_id):
    # Find the item data by ID
    item_data = None
    for item in self.character_data["items"]:
        if item["id"] == item_id:
            item_data = item
            break
    
    if not item_data:
        QMessageBox.warning(self, "Error", "Item not found.")
        return
    
    # Open the item builder dialog
    dialog = ItemBuilderDialog(self, item_data)
    if dialog.exec_():
        # Get updated item data
        updated_data = dialog.get_item_data()
        
        # Update the item in character data
        for i, item in enumerate(self.character_data["items"]):
            if item["id"] == item_id:
                self.character_data["items"][i] = updated_data
                break
        
        # Refresh the UI
        populate_items_ui(self)

__all__ = [
    "init_items_tab",
    "sync_items_from_attributes",
    "clear_items_ui",
    "populate_items_ui",
    "edit_item"
]