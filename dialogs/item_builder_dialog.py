# item_builder_dialog.py

import uuid
import math
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QTabWidget, QWidget, QListWidget, QListWidgetItem,
    QFormLayout, QMessageBox, QScrollArea, QGridLayout, QSizePolicy,
    QTextEdit, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt
from tools.utils import create_card_widget, format_attribute_display
from dialogs.attribute_builder_dialog import AttributeBuilderDialog
from dialogs.defect_builder_dialog import DefectBuilderDialog

class ItemBuilderDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Item")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.parent = parent

        self.item_data = item_data or {}
        self.original_id = item_data.get("id") if item_data else None
        
        # Ensure attributes and defects are lists
        if "attributes" not in self.item_data:
            self.item_data["attributes"] = []
        if "defects" not in self.item_data:
            self.item_data["defects"] = []
        
        # Calculate total CP spent and cost
        self.total_cp_spent = 0
        self.item_cost = 0  # This will be half of total_cp_spent (rounded down)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Header with name, type, and CP info ---
        header_layout = QHBoxLayout()
        
        # Left side - Item name and type
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.item_data.get("name", ""))
        form_layout.addRow("Item Name:", self.name_input)

        self.item_type_input = QComboBox()
        item_types = ["Weapon", "Armor", "Vehicle", "Tool", "Magical Item", "Tech Device", "Other"]
        self.item_type_input.addItems(item_types)
        current_type = self.item_data.get("type", "Other")
        if current_type in item_types:
            self.item_type_input.setCurrentText(current_type)
        form_layout.addRow("Item Type:", self.item_type_input)
        
        header_layout.addLayout(form_layout)
        header_layout.addStretch()
        
        # Right side - CP info
        cp_layout = QFormLayout()
        
        self.cp_spent_label = QLabel()
        cp_layout.addRow("Total CP Value:", self.cp_spent_label)
        
        self.item_cost_label = QLabel()
        cp_layout.addRow("Item Cost (1/2 CP):", self.item_cost_label)
        
        header_layout.addLayout(cp_layout)
        
        layout.addLayout(header_layout)
        
        # Add description
        description = QLabel("Items are devices that enhance a character or serve as useful tools, vehicles, bases, or weapons. " +
                            "The cost of an item is half the total CP value of its attributes and defects (rounded down).")
        description.setWordWrap(True)
        layout.addWidget(description)

        # --- Tabs for Attributes / Defects / Description / Examples ---
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.init_attributes_tab()
        self.init_defects_tab()
        self.init_description_tab()
        self.init_examples_tab()
        
        # Update CP labels
        self.calculate_cp_totals()

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def init_attributes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Attributes represent your item's special abilities and features. " +
                            "Add attributes to your item to give it special powers or capabilities.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Button to add new attribute
        add_btn = QPushButton("Add Attribute")
        add_btn.clicked.connect(self.add_attribute)
        layout.addWidget(add_btn)
        
        # Scroll area for attribute cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.attr_card_container = QWidget()
        self.attr_layout = QVBoxLayout(self.attr_card_container)
        self.attr_layout.setContentsMargins(8, 8, 8, 8)
        self.attr_layout.setSpacing(6)
        self.attr_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.attr_card_container)
        layout.addWidget(scroll)
        
        # Populate with existing attributes
        self.populate_attributes()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Attributes")

    def init_defects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Defects represent your item's weaknesses or limitations. " +
                            "Add defects to your item to reduce its cost or represent design flaws.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Button to add new defect
        add_btn = QPushButton("Add Defect")
        add_btn.clicked.connect(self.add_defect)
        layout.addWidget(add_btn)
        
        # Scroll area for defect cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.defect_card_container = QWidget()
        self.defect_layout = QVBoxLayout(self.defect_card_container)
        self.defect_layout.setContentsMargins(8, 8, 8, 8)
        self.defect_layout.setSpacing(6)
        self.defect_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.defect_card_container)
        layout.addWidget(scroll)
        
        # Populate with existing defects
        self.populate_defects()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Defects")

    def init_description_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description input
        description_label = QLabel("Item Description:")
        layout.addWidget(description_label)
        
        self.description_input = QTextEdit()
        self.description_input.setText(self.item_data.get("description", ""))
        layout.addWidget(self.description_input)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Description")

    def init_examples_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Here are some example items from the BESM 4e rulebook for reference:")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Scroll area for examples
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        examples_container = QWidget()
        examples_layout = QVBoxLayout(examples_container)
        
        # Example 1: Modern Melee Weapons
        weapons_label = QLabel("<b>Modern Melee Weapons</b>")
        examples_layout.addWidget(weapons_label)
        
        weapons_example = QLabel("Knife: Damage Level 1: 1 Point, Item Cost: 0\n" +
                                "Baseball Bat: Damage Level 2: 2 Points, Item Cost: 1\n" +
                                "Sword: Damage Level 3: 3 Points, Item Cost: 1\n" +
                                "Chainsaw: Damage Level 4: 4 Points, Item Cost: 2")
        weapons_example.setWordWrap(True)
        examples_layout.addWidget(weapons_example)
        
        # Example 2: Archaic Armor
        armor_label = QLabel("<b>Archaic Armor</b>")
        examples_layout.addWidget(armor_label)
        
        armor_example = QLabel("Leather Armor: Armor Level 1: 1 Point, Item Cost: 0\n" +
                              "Chain Mail: Armor Level 2: 2 Points, Item Cost: 1\n" +
                              "Plate Mail: Armor Level 3: 3 Points, Item Cost: 1\n" +
                              "Full Plate: Armor Level 4: 4 Points, Item Cost: 2")
        armor_example.setWordWrap(True)
        examples_layout.addWidget(armor_example)
        
        # Example 3: HAZMAT Suit
        hazmat_label = QLabel("<b>HAZMAT Suit</b>")
        examples_layout.addWidget(hazmat_label)
        
        hazmat_example = QLabel("Armor Level 2: 2 Points\n" +
                                "Environmental Control Level 2: 2 Points\n" +
                                "Resilient Level 4 (Lack of Air, Radiation; All Complete -2): 8 Points\n" +
                                "Total: 12 Points, Item Cost: 6")
        hazmat_example.setWordWrap(True)
        examples_layout.addWidget(hazmat_example)
        
        examples_layout.addStretch()
        scroll.setWidget(examples_container)
        layout.addWidget(scroll)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Examples")

    def calculate_cp_totals(self):
        # Calculate CP spent on attributes
        attr_cp = sum(attr.get("cost", 0) for attr in self.item_data["attributes"])
        
        # Calculate CP gained from defects
        defect_cp = sum(defect.get("cost", 0) for defect in self.item_data["defects"])
        
        # Calculate total CP spent and item cost (half of total, rounded down)
        self.total_cp_spent = max(0, attr_cp - defect_cp)
        self.item_cost = self.total_cp_spent // 2  # Integer division to round down
        
        # Update labels
        self.cp_spent_label.setText(f"{self.total_cp_spent} CP (Attributes: {attr_cp}, Defects: {defect_cp})")
        self.item_cost_label.setText(f"{self.item_cost} CP")
    
    def populate_attributes(self):
        # Clear existing widgets
        for i in reversed(range(self.attr_layout.count())): 
            widget = self.attr_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add attribute cards
        for attr in self.item_data["attributes"]:
            self.add_attribute_card(attr)
    
    def populate_defects(self):
        # Clear existing widgets
        for i in reversed(range(self.defect_layout.count())): 
            widget = self.defect_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add defect cards
        for defect in self.item_data["defects"]:
            self.add_defect_card(defect)
    
    def add_attribute(self):
        dialog = AttributeBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            attr = dialog.get_attribute_data()
            # Add ID if not present
            if "id" not in attr:
                attr["id"] = str(uuid.uuid4())
            self.item_data["attributes"].append(attr)
            self.add_attribute_card(attr)
            self.calculate_cp_totals()
    
    def add_defect(self):
        dialog = DefectBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            defect = dialog.get_defect_data()
            # Add ID if not present
            if "id" not in defect:
                defect["id"] = str(uuid.uuid4())
            self.item_data["defects"].append(defect)
            self.add_defect_card(defect)
            self.calculate_cp_totals()
    
    def add_attribute_card(self, attr):
        # Create a function to remove this specific attribute
        def remove_this_attribute():
            self.remove_attribute(attr["id"])
        
        # Create card
        card = create_card_widget(
            title=attr["name"],
            lines=[
                f"Level: {attr['level']}",
                f"Cost: {attr['cost']} CP",
                f"Description: {attr.get('description', 'No description')}"
            ],
            on_remove=remove_this_attribute,
            card_type="attribute"
        )
        
        self.attr_layout.addWidget(card)
    
    def add_defect_card(self, defect):
        # Create a function to remove this specific defect
        def remove_this_defect():
            self.remove_defect(defect["id"])
        
        # Create card
        card = create_card_widget(
            title=defect["name"],
            lines=[
                f"Rank: {defect['rank']}",
                f"Value: {defect['cost']} CP",
                f"Description: {defect.get('description', 'No description')}"
            ],
            on_remove=remove_this_defect,
            card_type="defect"
        )
        
        self.defect_layout.addWidget(card)
    
    def remove_attribute(self, attr_id):
        # Find and remove the attribute
        for i, attr in enumerate(self.item_data["attributes"]):
            if attr.get("id") == attr_id:
                del self.item_data["attributes"][i]
                break
        
        # Refresh the UI
        self.populate_attributes()
        self.calculate_cp_totals()
    
    def remove_defect(self, defect_id):
        # Find and remove the defect
        for i, defect in enumerate(self.item_data["defects"]):
            if defect.get("id") == defect_id:
                del self.item_data["defects"][i]
                break
        
        # Refresh the UI
        self.populate_defects()
        self.calculate_cp_totals()

    def get_item_data(self):
        return {
            "id": self.original_id or str(uuid.uuid4()),
            "name": self.name_input.text(),
            "type": self.item_type_input.currentText(),
            "description": self.description_input.toPlainText(),
            "total_cp": self.total_cp_spent,
            "cost": self.item_cost,
            "attributes": self.item_data["attributes"],
            "defects": self.item_data["defects"]
        }
