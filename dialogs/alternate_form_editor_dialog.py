# Alternate Form Editor Dialog

import uuid
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QTabWidget, QWidget, QListWidget, QListWidgetItem,
    QFormLayout, QMessageBox, QScrollArea, QGridLayout, QSizePolicy, QTextEdit,
    QInputDialog
)
from PyQt5.QtCore import Qt, QFile, QTextStream
from tools.utils import create_card_widget, format_attribute_display
from dialogs.attribute_builder_dialog import AttributeBuilderDialog
from dialogs.defect_builder_dialog import DefectBuilderDialog

class AlternateFormEditorDialog(QDialog):
    def __init__(self, parent=None, form_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Alternate Form")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.parent = parent

        self.form_data = form_data or {}
        self.original_id = form_data.get("id") if form_data else None
        
        # Ensure attributes and defects are lists
        if "attributes" not in self.form_data:
            self.form_data["attributes"] = []
        if "defects" not in self.form_data:
            self.form_data["defects"] = []
        
        # Calculate total CP spent and remaining
        self.total_cp_spent = 0
        self.remaining_cp = self.form_data.get("cp_budget", 5)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Header with name, level, and CP info ---
        header_layout = QHBoxLayout()
        
        # Left side - Form name and level
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.form_data.get("name", "New Alternate Form"))
        form_layout.addRow("Form Name:", self.name_input)

        self.level_input = QSpinBox()
        self.level_input.setRange(1, 6)  # BESM4e limits Alternate Form to 6 levels
        self.level_input.setValue(self.form_data.get("level", 1))
        self.level_input.valueChanged.connect(self.update_cp_budget)
        form_layout.addRow("Form Level:", self.level_input)
        
        header_layout.addLayout(form_layout)
        header_layout.addStretch()
        
        # Right side - CP budget info
        cp_layout = QFormLayout()
        
        self.cp_budget_label = QLabel()
        self.cp_budget_label.setText(f"CP Budget: {self.form_data.get('cp_budget', 5)}")
        cp_layout.addRow("", self.cp_budget_label)
        
        self.cp_spent_label = QLabel()
        cp_layout.addRow("", self.cp_spent_label)
        
        self.cp_remaining_label = QLabel()
        cp_layout.addRow("", self.cp_remaining_label)
        
        header_layout.addLayout(cp_layout)
        
        layout.addLayout(header_layout)
        
        # Add description
        description = QLabel("Alternate Form allows your character to transform into a different form with different attributes and defects.")
        description.setWordWrap(True)
        layout.addWidget(description)

        # --- Tabs for Stats / Attributes / Defects / Derived Values ---
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.init_stats_tab()
        self.init_attributes_tab()
        self.init_defects_tab()
        self.init_derived_values_tab()
        
        # Update CP labels
        self.calculate_cp_totals()

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.save_to_lib_btn = QPushButton("Save to Library")
        self.save_to_lib_btn.clicked.connect(self.save_to_library)
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_to_lib_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def init_stats_tab(self):
        tab = QWidget()
        form = QFormLayout()

        # Description
        description = QLabel("Stats represent your alternate form's basic capabilities. They may be different from your base form.")
        description.setWordWrap(True)
        form.addRow(description)
        
        # Stats
        self.stat_inputs = {}
        for stat in ["Body", "Mind", "Soul"]:
            spin = QSpinBox()
            spin.setRange(1, 20)
            spin.setValue(self.form_data.get("stats", {}).get(stat, 4))
            # Connect valueChanged to update both derived values and CP totals
            spin.valueChanged.connect(self.update_derived_values)
            spin.valueChanged.connect(self.calculate_cp_totals)
            self.stat_inputs[stat] = spin
            form.addRow(f"{stat}:", spin)

        tab.setLayout(form)
        self.tabs.addTab(tab, "Stats")

    def init_attributes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Attributes represent special abilities your alternate form possesses. These are in addition to your base form's attributes.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add button
        add_btn = QPushButton("Add Attribute")
        add_btn.clicked.connect(self.add_attribute)
        layout.addWidget(add_btn)
        
        # Scroll area for attributes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Container for attribute cards
        self.attr_container = QWidget()
        self.attr_layout = QVBoxLayout(self.attr_container)
        self.attr_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.attr_container)
        
        # Populate attributes
        self.populate_attributes()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Attributes")

    def init_defects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Defects represent limitations or weaknesses your alternate form possesses.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add button
        add_btn = QPushButton("Add Defect")
        add_btn.clicked.connect(self.add_defect)
        layout.addWidget(add_btn)
        
        # Scroll area for defects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Container for defect cards
        self.defect_container = QWidget()
        self.defect_layout = QVBoxLayout(self.defect_container)
        self.defect_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.defect_container)
        
        # Populate defects
        self.populate_defects()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Defects")
    
    def init_derived_values_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Derived values are automatically calculated based on your alternate form's stats.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Grid for derived values
        grid = QGridLayout()
        
        # Combat values
        self.derived_labels = {}
        row = 0
        for derived in ["Combat Value", "Attack Combat Value", "Defense Combat Value", 
                       "Health Points", "Energy Points", "Shock Value", 
                       "Damage Multiplier", "Sanity Points", "Society Points"]:
            label = QLabel(derived + ":")
            value = QLabel("0")
            self.derived_labels[derived] = value
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
            row += 1
        
        layout.addLayout(grid)
        layout.addStretch()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Derived Values")
        
        # Update derived values
        self.update_derived_values()
    
    def update_cp_budget(self):
        new_budget = self.level_input.value() * 5
        self.form_data["cp_budget"] = new_budget
        self.cp_budget_label.setText(f"CP Budget: {new_budget}")
        self.calculate_cp_totals()
        
    def calculate_cp_totals(self):
        # Get base stats from parent character (if available)
        base_stats = {}
        if hasattr(self.parent, 'character_data') and 'stats' in self.parent.character_data:
            base_stats = self.parent.character_data['stats']
        else:
            # Default base stats if parent data not available
            base_stats = {"Body": 4, "Mind": 4, "Soul": 4}
        
        # Calculate CP spent on stats (only count points above base stats)
        stats_cp = 0
        for stat, spin in self.stat_inputs.items():
            current_value = spin.value()
            base_value = base_stats.get(stat, 4)  # Default to 4 if not found
            # Only count CP if the stat is higher than the base form
            if current_value > base_value:
                stats_cp += (current_value - base_value)
        
        # Calculate CP spent on attributes
        attr_cp = sum(attr.get("cost", 0) for attr in self.form_data["attributes"])
        
        # Calculate CP gained from defects
        defect_cp = sum(defect.get("cost", 0) for defect in self.form_data["defects"])
        
        # Calculate total CP spent and remaining
        self.total_cp_spent = stats_cp + attr_cp - defect_cp
        self.remaining_cp = self.form_data["cp_budget"] - self.total_cp_spent
        
        # Update labels
        self.cp_spent_label.setText(f"CP Spent: {self.total_cp_spent} (Stats: {stats_cp}, Attrs: {attr_cp}, Defects: {defect_cp})")
        
        # Set color based on remaining CP
        if self.remaining_cp < 0:
            self.cp_remaining_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.cp_remaining_label.setStyleSheet("")
            
        self.cp_remaining_label.setText(f"CP Remaining: {self.remaining_cp}")
    
    def populate_attributes(self):
        # Clear existing widgets
        for i in reversed(range(self.attr_layout.count())): 
            widget = self.attr_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add attribute cards
        for attr in self.form_data["attributes"]:
            self.add_attribute_card(attr)
    
    def populate_defects(self):
        # Clear existing widgets
        for i in reversed(range(self.defect_layout.count())): 
            widget = self.defect_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add defect cards
        for defect in self.form_data["defects"]:
            self.add_defect_card(defect)
    
    def add_attribute(self):
        dialog = AttributeBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            attr = dialog.get_attribute_data()
            # Add ID if not present
            if "id" not in attr:
                attr["id"] = str(uuid.uuid4())
            self.form_data["attributes"].append(attr)
            self.add_attribute_card(attr)
            self.calculate_cp_totals()
    
    def add_defect(self):
        dialog = DefectBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            defect = dialog.get_defect_data()
            # Add ID if not present
            if "id" not in defect:
                defect["id"] = str(uuid.uuid4())
            self.form_data["defects"].append(defect)
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
        for i, attr in enumerate(self.form_data["attributes"]):
            if attr.get("id") == attr_id:
                del self.form_data["attributes"][i]
                break
        
        # Refresh the UI
        self.populate_attributes()
        self.calculate_cp_totals()
    
    def remove_defect(self, defect_id):
        # Find and remove the defect
        for i, defect in enumerate(self.form_data["defects"]):
            if defect.get("id") == defect_id:
                del self.form_data["defects"][i]
                break
        
        # Refresh the UI
        self.populate_defects()
        self.calculate_cp_totals()
    
    def update_derived_values(self):
        # Get current stats
        body = self.stat_inputs["Body"].value()
        mind = self.stat_inputs["Mind"].value()
        soul = self.stat_inputs["Soul"].value()
        
        # Calculate derived values
        cv = (body + mind + soul) // 3
        acv = cv
        dcv = cv
        hp = body * 10
        ep = mind * 10
        sv = body * 2
        dm = (body + soul) // 2
        sp = soul * 10
        sop = mind * 10
        
        # Update labels
        self.derived_labels["Combat Value"].setText(str(cv))
        self.derived_labels["Attack Combat Value"].setText(str(acv))
        self.derived_labels["Defense Combat Value"].setText(str(dcv))
        self.derived_labels["Health Points"].setText(str(hp))
        self.derived_labels["Energy Points"].setText(str(ep))
        self.derived_labels["Shock Value"].setText(str(sv))
        self.derived_labels["Damage Multiplier"].setText(str(dm))
        self.derived_labels["Sanity Points"].setText(str(sp))
        self.derived_labels["Society Points"].setText(str(sop))

    def get_form_data(self):
        # Update stats from inputs
        stats = {stat: spin.value() for stat, spin in self.stat_inputs.items()}
        
        # Update derived values based on stats
        body = stats["Body"]
        mind = stats["Mind"]
        soul = stats["Soul"]
        
        derived = {
            "CV": (body + mind + soul) // 3,
            "ACV": (body + mind + soul) // 3,
            "DCV": (body + mind + soul) // 3,
            "HP": body * 10,
            "EP": mind * 10,
            "SV": body * 2,
            "DM": (body + soul) // 2,
            "SP": soul * 10,
            "SOP": mind * 10
        }
        
        level = self.level_input.value()
        return {
            "id": self.original_id or str(uuid.uuid4()),
            "name": self.name_input.text(),
            "level": level,
            "cp_budget": level * 5,
            "stats": stats,
            "derived": derived,
            "attributes": self.form_data["attributes"],
            "defects": self.form_data["defects"]
        }

    def save_to_library(self):
        """Save the current alternate form to the library"""
        try:
            # Get form data to save
            form_data = self.get_form_data()
            
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
            if not form_data.get("name"):
                name, ok = QInputDialog.getText(
                    self,
                    "Save to Library",
                    "Enter a name for this alternate form:"
                )
                if not ok or not name:
                    return
                form_data["name"] = name
                
            # Ensure the data has an ID
            if "id" not in form_data:
                form_data["id"] = str(uuid.uuid4())
                
            # Check if this item already exists in the library
            existing_index = -1
            for i, obj in enumerate(libraries_data["libraries"]["alternate_forms"]):
                if obj.get("id") == form_data.get("id"):
                    existing_index = i
                    break
                    
            # Ask for confirmation to overwrite if it exists
            if existing_index >= 0:
                reply = QMessageBox.question(
                    self,
                    "Overwrite Existing",
                    f"An alternate form with this ID already exists in the library. Overwrite it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
                    
                # Update the existing item
                libraries_data["libraries"]["alternate_forms"][existing_index] = form_data
            else:
                # Add as a new item
                libraries_data["libraries"]["alternate_forms"].append(form_data)
                
            # Save the updated library data
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(libraries_data, f, indent=2)
                    
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully saved to the alternate forms library."
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save to library: {str(e)}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")