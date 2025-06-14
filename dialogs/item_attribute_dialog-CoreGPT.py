# item_attribute_dialog.py

import uuid
from uuid import uuid4
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QScrollArea, QWidget, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt

from tools.utils import create_card_widget
from dialogs.item_builder_dialog import ItemBuilderDialog

class ItemAttributeDialog(QDialog):
    def __init__(self, parent=None, attribute_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Item Attribute")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.parent = parent

        # Initialize attribute data
        self.attribute_data = attribute_data or {}
        self.original_id = self.attribute_data.get("id")
        
        # Ensure we have the basic structure
        if "custom_fields" not in self.attribute_data:
            self.attribute_data["custom_fields"] = {}
        if "items" not in self.attribute_data["custom_fields"]:
            self.attribute_data["custom_fields"]["items"] = []
            
        # Set up the layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header with attribute name and description
        header_layout = QFormLayout()
        
        # Attribute name
        self.name_input = QLineEdit()
        self.name_input.setText(self.attribute_data.get("name", "Items"))
        header_layout.addRow("Attribute Name:", self.name_input)
        
        # Description
        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        
        self.description_input = QTextEdit()
        self.description_input.setPlainText(self.attribute_data.get("user_description", ""))
        self.description_input.setFixedHeight(80)
        layout.addWidget(self.description_input)
        
        # Official description (read-only)
        official_description = QLabel("Items are devices that enhance a character or serve as useful tools, vehicles, bases, or weapons. " +
                                     "The cost of an item is half the total CP value of its attributes and defects (rounded down).")
        official_description.setWordWrap(True)
        layout.addWidget(official_description)
        
        # Items section
        items_label = QLabel("Items:")
        items_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(items_label)
        
        # Add item button
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.add_item)
        layout.addWidget(add_item_btn)
        
        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(8, 8, 8, 8)
        self.items_layout.setSpacing(6)
        self.items_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.items_container)
        layout.addWidget(scroll)
        
        # Total CP cost display
        self.total_cp_label = QLabel()
        layout.addWidget(self.total_cp_label)
        
        # Populate with existing items
        self.populate_items()
        
        # Update the total CP cost
        self.update_total_cp()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def populate_items(self):
        # Clear existing items
        for i in reversed(range(self.items_layout.count())):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add item cards
        for item in self.attribute_data["custom_fields"]["items"]:
            self.add_item_card(item)
    
    def add_item(self):
        # Create a new item
        dialog = ItemBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            # Get the item data
            item_data = dialog.get_item_data()
            
            # Add to our items list
            self.attribute_data["custom_fields"]["items"].append(item_data)
            
            # Add card to UI
            self.add_item_card(item_data)
            
            # Update total CP
            self.update_total_cp()
    
    def add_item_card(self, item):
        # Create a function to remove this specific item
        def remove_this_item():
            self.remove_item(item["id"])
        
        # Create a function to edit this specific item
        def edit_this_item():
            self.edit_item(item["id"])
        
        # Calculate item cost (half of total CP, rounded down)
        total_cp = item.get("total_cp", 0)
        item_cost = max(0, total_cp // 2)  # Integer division to round down
        
        # Create lines for the card
        lines = [
            f"Item Cost: {item_cost} CP",
        ]
        
        if item.get("description"):
            lines.append(f"Description: {item['description']}")
        
        # Add attributes/defects summary
        attr_names = [a["name"] for a in item.get("attributes", [])]
        defect_names = [d["name"] for d in item.get("defects", [])]
        
        if attr_names:
            lines.append("Attributes: " + ", ".join(attr_names))
        if defect_names:
            lines.append("Defects: " + ", ".join(defect_names))
        
        # Create the card
        card = create_card_widget(
            title=item["name"],
            lines=lines,
            on_remove=remove_this_item,
            on_click=edit_this_item,
            card_type="item"  # Use a custom type for items
        )
        
        self.items_layout.addWidget(card)
    
    def edit_item(self, item_id):
        # Find the item
        for i, item in enumerate(self.attribute_data["custom_fields"]["items"]):
            if item.get("id") == item_id:
                # Open the item builder dialog
                dialog = ItemBuilderDialog(self.parent, item)
                if dialog.exec_() == QDialog.Accepted:
                    # Update the item data
                    updated_data = dialog.get_item_data()
                    self.attribute_data["custom_fields"]["items"][i] = updated_data
                    
                    # Refresh the UI
                    self.populate_items()
                    
                    # Update total CP
                    self.update_total_cp()
                break
    
    def remove_item(self, item_id):
        # Find and remove the item
        for i, item in enumerate(self.attribute_data["custom_fields"]["items"]):
            if item.get("id") == item_id:
                del self.attribute_data["custom_fields"]["items"][i]
                break
        
        # Refresh the UI
        self.populate_items()
        
        # Update total CP
        self.update_total_cp()
    
    def update_total_cp(self):
        # Calculate total CP from all items
        total_cp = 0
        for item in self.attribute_data["custom_fields"]["items"]:
            # Item cost is half of total CP, rounded down
            item_cp = item.get("total_cp", 0)
            item_cost = max(0, item_cp // 2)  # Integer division to round down
            total_cp += item_cost
        
        # Update the label
        self.total_cp_label.setText(f"Total CP Cost: {total_cp} CP")
        
        # Update the attribute data
        self.attribute_data["cost"] = total_cp
    
    def get_attribute_data(self):
        # Create the final attribute data
        attribute_data = {
            "id": self.original_id or str(uuid4()),
            "name": self.name_input.text(),
            "base_name": "Items",  # Always use the base name "Items"
            "level": 1,  # Level is always 1 for Items
            "cost": self.attribute_data["cost"],
            "user_description": self.description_input.toPlainText(),
            "enhancements": self.attribute_data.get("enhancements", []),
            "limiters": self.attribute_data.get("limiters", []),
            "custom_fields": self.attribute_data["custom_fields"]
        }
        
        return attribute_data
