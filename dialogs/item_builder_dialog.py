# item_builder_dialog.py

import uuid
import math
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from tools.utils import create_card_widget, format_attribute_display
from dialogs.attribute_builder_dialog import AttributeBuilderDialog
from dialogs.defect_builder_dialog import DefectBuilderDialog

class ItemBuilderDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Item Builder")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.item_data = item_data or {"attributes": [], "defects": []}
        self.original_id = item_data.get("id") if item_data else None
        
        self.total_cp_spent = 0
        self.item_cost = 0

        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Header with name, type inputs and CP cost info
        header_layout = QtWidgets.QHBoxLayout()
        
        # Left side - Basic info
        form_layout = QtWidgets.QFormLayout()
        
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setText(self.item_data.get("name", ""))
        form_layout.addRow("Name:", self.name_input)
        
        self.item_type_input = QtWidgets.QComboBox()
        self.item_type_input.addItems([
            "Weapon", "Armor", "Equipment", "Vehicle", "Facility", "Magical Item", 
            "Divine Item", "Cybernetic", "Bioware", "Other"
        ])
        if "type" in self.item_data:
            index = self.item_type_input.findText(self.item_data["type"])
            if index >= 0:
                self.item_type_input.setCurrentIndex(index)
        form_layout.addRow("Item Type:", self.item_type_input)
        
        header_layout.addLayout(form_layout)
        header_layout.addStretch()
        
        # Right side - CP info
        cp_layout = QtWidgets.QFormLayout()
        
        self.cp_spent_label = QtWidgets.QLabel("0 CP")
        cp_layout.addRow("Total CP Value:", self.cp_spent_label)
        
        self.item_cost_label = QtWidgets.QLabel("0 CP")
        cp_layout.addRow("Item Cost:", self.item_cost_label)
        
        header_layout.addLayout(cp_layout)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QtWidgets.QTabWidget()
        self.init_attributes_tab()
        self.init_defects_tab()
        self.init_description_tab()
        self.init_examples_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Bottom buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.save_to_library_btn = QtWidgets.QPushButton("Save to Library")
        self.save_to_library_btn.clicked.connect(self.save_to_library)
        
        self.import_from_library_btn = QtWidgets.QPushButton("Import from Library")
        self.import_from_library_btn.clicked.connect(self.import_from_library)
        
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_to_library_btn)
        button_layout.addWidget(self.import_from_library_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(button_layout)
        
        # Calculate initial CP totals
        self.calculate_cp_totals()
        
        # Populate attribute and defect lists
        self.populate_attributes()
        self.populate_defects()

    def init_attributes_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        # Description
        description = QtWidgets.QLabel("Attributes represent your item's special abilities and features. " +
                            "Add attributes to your item to give it special powers or capabilities.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Button to add new attribute
        add_btn = QtWidgets.QPushButton("Add Attribute")
        add_btn.clicked.connect(self.add_attribute)
        layout.addWidget(add_btn)
        
        # Scroll area for attribute cards
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.attr_card_container = QtWidgets.QWidget()
        self.attr_layout = QtWidgets.QVBoxLayout(self.attr_card_container)
        self.attr_layout.setContentsMargins(8, 8, 8, 8)
        self.attr_layout.setSpacing(6)
        self.attr_layout.setAlignment(QtCore.Qt.AlignTop)
        
        scroll.setWidget(self.attr_card_container)
        layout.addWidget(scroll)
        
        # Populate with existing attributes
        self.populate_attributes()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Attributes")

    def init_defects_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        # Description
        description = QtWidgets.QLabel("Defects represent your item's weaknesses or limitations. " +
                            "Add defects to your item to reduce its cost or represent design flaws.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Button to add new defect
        add_btn = QtWidgets.QPushButton("Add Defect")
        add_btn.clicked.connect(self.add_defect)
        layout.addWidget(add_btn)
        
        # Scroll area for defect cards
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.defect_card_container = QtWidgets.QWidget()
        self.defect_layout = QtWidgets.QVBoxLayout(self.defect_card_container)
        self.defect_layout.setContentsMargins(8, 8, 8, 8)
        self.defect_layout.setSpacing(6)
        self.defect_layout.setAlignment(QtCore.Qt.AlignTop)
        
        scroll.setWidget(self.defect_card_container)
        layout.addWidget(scroll)
        
        # Populate with existing defects
        self.populate_defects()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Defects")

    def init_description_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        # Description input
        description_label = QtWidgets.QLabel("Item Description:")
        layout.addWidget(description_label)
        
        self.description_input = QtWidgets.QTextEdit()
        self.description_input.setText(self.item_data.get("description", ""))
        layout.addWidget(self.description_input)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Description")

    def init_examples_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        # Description
        description = QtWidgets.QLabel("Here are some example items from the BESM 4e rulebook for reference:")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Scroll area for examples
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        
        examples_container = QtWidgets.QWidget()
        examples_layout = QtWidgets.QVBoxLayout(examples_container)
        
        # Example 1: Modern Melee Weapons
        weapons_label = QtWidgets.QLabel("<b>Modern Melee Weapons</b>")
        examples_layout.addWidget(weapons_label)
        
        weapons_example = QtWidgets.QLabel("Knife: Damage Level 1: 1 Point, Item Cost: 0\n" +
                                "Baseball Bat: Damage Level 2: 2 Points, Item Cost: 1\n" +
                                "Sword: Damage Level 3: 3 Points, Item Cost: 1\n" +
                                "Chainsaw: Damage Level 4: 4 Points, Item Cost: 2")
        weapons_example.setWordWrap(True)
        examples_layout.addWidget(weapons_example)
        
        # Example 2: Archaic Armor
        armor_label = QtWidgets.QLabel("<b>Archaic Armor</b>")
        examples_layout.addWidget(armor_label)
        
        armor_example = QtWidgets.QLabel("Leather Armor: Armor Level 1: 1 Point, Item Cost: 0\n" +
                              "Chain Mail: Armor Level 2: 2 Points, Item Cost: 1\n" +
                              "Plate Mail: Armor Level 3: 3 Points, Item Cost: 1\n" +
                              "Full Plate: Armor Level 4: 4 Points, Item Cost: 2")
        armor_example.setWordWrap(True)
        examples_layout.addWidget(armor_example)
        
        # Example 3: HAZMAT Suit
        hazmat_label = QtWidgets.QLabel("<b>HAZMAT Suit</b>")
        examples_layout.addWidget(hazmat_label)
        
        hazmat_example = QtWidgets.QLabel("Armor Level 2: 2 Points\n" +
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
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            attr = dialog.get_attribute_data()
            # Add ID if not present
            if "id" not in attr:
                attr["id"] = str(uuid.uuid4())
            self.item_data["attributes"].append(attr)
            self.add_attribute_card(attr)
            self.calculate_cp_totals()
    
    def add_defect(self):
        dialog = DefectBuilderDialog(self.parent)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
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

    def save_to_library(self):
        """Save the current item to the library"""
        try:
            # Get item data to save
            item_data = self.get_item_data()
            
            # Load the libraries data
            import os
            import json
            import uuid
            from PyQt5.QtWidgets import QMessageBox, QInputDialog
            
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_path, "data", "libraries.json")
            
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        libraries_data = json.load(f)
                else:
                    libraries_data = {
                        "version": "1.0",
                        "libraries": {
                            "items": [],
                            "companions": [],
                            "minions": [],
                            "metamorphosis": [],
                            "alternate_forms": []
                        }
                    }
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load libraries data: {str(e)}")
                return
                
            # Prompt for a name if not set
            if not item_data.get("name"):
                name, ok = QInputDialog.getText(
                    self,
                    "Save to Library",
                    "Enter a name for this item:"
                )
                if not ok or not name:
                    return
                item_data["name"] = name
                
            # Ensure the data has an ID
            if "id" not in item_data:
                item_data["id"] = str(uuid.uuid4())
                
            # Check if this item already exists in the library
            existing_index = -1
            for i, obj in enumerate(libraries_data["libraries"]["items"]):
                if obj.get("id") == item_data.get("id"):
                    existing_index = i
                    break
                    
            # Ask for confirmation to overwrite if it exists
            if existing_index >= 0:
                reply = QMessageBox.question(
                    self,
                    "Overwrite Existing",
                    f"An item with this ID already exists in the library. Overwrite it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
                    
                # Update the existing item
                libraries_data["libraries"]["items"][existing_index] = item_data
            else:
                # Add as a new item
                libraries_data["libraries"]["items"].append(item_data)
                
            # Save the updated library data
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(libraries_data, f, indent=2)
                    
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully saved to the items library."
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save to library: {str(e)}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def import_from_library(self):
        """Import an item from the library"""
        from dialogs.library_selector_dialog import LibrarySelectorDialog
        
        # Create and show the library selector dialog
        selector = LibrarySelectorDialog(self, library_type="items")
        if selector.exec_():
            # Get the selected item data
            selected_item = selector.selected_object
            if selected_item:
                # Update the current item data
                self.item_data = selected_item
                
                # Update UI elements
                self.name_input.setText(selected_item.get("name", ""))
                
                if "type" in selected_item:
                    index = self.item_type_input.findText(selected_item["type"])
                    if index >= 0:
                        self.item_type_input.setCurrentIndex(index)
                
                # Clear existing attributes and defects
                self.item_data["attributes"] = selected_item.get("attributes", [])
                self.item_data["defects"] = selected_item.get("defects", [])
                
                # Repopulate lists and recalculate CP
                self.populate_attributes()
                self.populate_defects()
                self.calculate_cp_totals()
                
                # Show success message
                QtWidgets.QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Successfully imported '{selected_item.get('name', 'Unnamed')}' from the library."
                )
