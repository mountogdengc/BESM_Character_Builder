# companion_builder_dialog.py

import uuid
import math
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QTabWidget, QWidget, QListWidget, QListWidgetItem,
    QFormLayout, QMessageBox, QScrollArea, QGridLayout, QSizePolicy,
    QTextEdit
)
from PyQt5.QtCore import Qt
from tools.utils import create_card_widget, format_attribute_display
from dialogs.attribute_builder_dialog import AttributeBuilderDialog
from dialogs.defect_builder_dialog import DefectBuilderDialog

class CompanionBuilderDialog(QDialog):
    def __init__(self, parent=None, companion_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Companion")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.parent = parent

        self.companion_data = companion_data or {}
        self.original_id = companion_data.get("id") if companion_data else None
        
        # Ensure attributes and defects are lists
        if "attributes" not in self.companion_data:
            self.companion_data["attributes"] = []
        if "defects" not in self.companion_data:
            self.companion_data["defects"] = []
        
        # Initialize level and CP budget
        self.companion_data["level"] = self.companion_data.get("level", 1)
        self.companion_data["cp_budget"] = self.companion_data.get("cp_budget", self.companion_data["level"] * 10)
        
        # Calculate total CP spent and remaining
        self.total_cp_spent = 0
        self.remaining_cp = self.companion_data["cp_budget"]

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Header with name, level, and CP info ---
        header_layout = QHBoxLayout()
        
        # Left side - Companion name and level
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.companion_data.get("name", ""))
        form_layout.addRow("Companion Name:", self.name_input)

        self.level_input = QSpinBox()
        self.level_input.setRange(1, 6)  # BESM4e limits Companion to 6 levels
        self.level_input.setValue(self.companion_data.get("level", 1))
        self.level_input.valueChanged.connect(self.update_cp_budget)
        form_layout.addRow("Companion Level:", self.level_input)
        
        header_layout.addLayout(form_layout)
        header_layout.addStretch()
        
        # Right side - CP budget info
        cp_layout = QFormLayout()
        
        self.cp_budget_label = QLabel()
        self.cp_budget_label.setText(f"CP Budget: {self.companion_data.get('cp_budget', 10)}")
        cp_layout.addRow("", self.cp_budget_label)
        
        self.cp_spent_label = QLabel()
        cp_layout.addRow("", self.cp_spent_label)
        
        self.cp_remaining_label = QLabel()
        cp_layout.addRow("", self.cp_remaining_label)
        
        header_layout.addLayout(cp_layout)
        
        layout.addLayout(header_layout)
        
        # Add description
        description = QLabel("Companions are NPCs controlled by the GM, but they will normally be loyal to their masters, and work toward that character's best interests (as they perceive them).")
        description.setWordWrap(True)
        layout.addWidget(description)

        # --- Tabs for Stats / Attributes / Defects / Derived Values / Description ---
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.init_stats_tab()
        self.init_attributes_tab()
        self.init_defects_tab()
        self.init_derived_values_tab()
        self.init_description_tab()
        
        # Update CP labels
        self.calculate_cp_totals()

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.save_to_library_btn = QPushButton("Save to Library")
        self.import_from_library_btn = QPushButton("Import from Library")
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.save_to_library_btn.clicked.connect(self.save_to_library)
        self.import_from_library_btn.clicked.connect(self.import_from_library)
        btn_layout.addWidget(self.save_to_library_btn)
        btn_layout.addWidget(self.import_from_library_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def init_stats_tab(self):
        tab = QWidget()
        form = QFormLayout()

        # Description
        description = QLabel("Stats represent your companion's basic capabilities.")
        description.setWordWrap(True)
        form.addRow(description)
        
        # Stats
        self.stat_inputs = {}
        for stat in ["Body", "Mind", "Soul"]:
            spin = QSpinBox()
            spin.setRange(0, 99)
            spin.setValue(self.companion_data.get("stats", {}).get(stat, 0))
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
        description = QLabel("Attributes represent your companion's special abilities.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Scrollable area for attribute cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Container for attribute cards
        attr_container = QWidget()
        self.attr_layout = QVBoxLayout(attr_container)
        self.attr_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(attr_container)
        
        # Add button
        add_btn = QPushButton("Add Attribute")
        add_btn.clicked.connect(self.add_attribute)
        layout.addWidget(add_btn)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Attributes")
        
        # Populate with existing attributes
        self.populate_attributes()

    def init_defects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Defects represent your companion's weaknesses and limitations.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Scrollable area for defect cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Container for defect cards
        defect_container = QWidget()
        self.defect_layout = QVBoxLayout(defect_container)
        self.defect_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(defect_container)
        
        # Add button
        add_btn = QPushButton("Add Defect")
        add_btn.clicked.connect(self.add_defect)
        layout.addWidget(add_btn)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Defects")
        
        # Populate with existing defects
        self.populate_defects()

    def init_derived_values_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Derived values are calculated from your companion's stats.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Grid for derived values
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)  # Make the second column stretch
        
        # Create labels for each derived value
        self.derived_labels = {}
        derived_values = [
            "Combat Value", "Attack Combat Value", "Defense Combat Value",
            "Health Points", "Energy Points", "Shock Value",
            "Damage Multiplier", "Sanity Points", "Society Points"
        ]
        
        row = 0
        for name in derived_values:
            label = QLabel(name + ":")
            value = QLabel("0")
            value.setStyleSheet("font-weight: bold;")
            self.derived_labels[name] = value
            
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
            row += 1
        
        layout.addLayout(grid)
        layout.addStretch()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Derived Values")
        
        # Update derived values
        self.update_derived_values()

    def init_description_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Add details about your companion's appearance, personality, and background.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Text area for description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter your companion's description here...")
        self.description_input.setText(self.companion_data.get("description", ""))
        layout.addWidget(self.description_input)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Description")

    def update_cp_budget(self):
        new_budget = self.level_input.value() * 10  # 10 CP per level for companions
        self.companion_data["cp_budget"] = new_budget
        self.cp_budget_label.setText(f"CP Budget: {new_budget}")
        self.calculate_cp_totals()
        
    def calculate_cp_totals(self):
        # Calculate CP spent on stats (1 CP per point)
        stats_cp = sum(spin.value() for spin in self.stat_inputs.values())
        
        # Calculate CP spent on attributes
        attr_cp = sum(attr.get("cost", 0) for attr in self.companion_data["attributes"])
        
        # Calculate CP gained from defects
        defect_cp = sum(defect.get("cost", 0) for defect in self.companion_data["defects"])
        
        # Calculate total CP spent and remaining
        self.total_cp_spent = stats_cp + attr_cp - defect_cp
        self.remaining_cp = self.companion_data["cp_budget"] - self.total_cp_spent
        
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
        for attr in self.companion_data["attributes"]:
            self.add_attribute_card(attr)
    
    def populate_defects(self):
        # Clear existing widgets
        for i in reversed(range(self.defect_layout.count())): 
            widget = self.defect_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add defect cards
        for defect in self.companion_data["defects"]:
            self.add_defect_card(defect)
    
    def add_attribute(self):
        dialog = AttributeBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            attr = dialog.get_attribute_data()
            # Add ID if not present
            if "id" not in attr:
                attr["id"] = str(uuid.uuid4())
            self.companion_data["attributes"].append(attr)
            self.add_attribute_card(attr)
            self.calculate_cp_totals()
    
    def add_defect(self):
        dialog = DefectBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            defect = dialog.get_defect_data()
            # Add ID if not present
            if "id" not in defect:
                defect["id"] = str(uuid.uuid4())
            self.companion_data["defects"].append(defect)
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
        for i, attr in enumerate(self.companion_data["attributes"]):
            if attr.get("id") == attr_id:
                del self.companion_data["attributes"][i]
                break
        
        # Refresh the UI
        self.populate_attributes()
        self.calculate_cp_totals()
    
    def remove_defect(self, defect_id):
        # Find and remove the defect
        for i, defect in enumerate(self.companion_data["defects"]):
            if defect.get("id") == defect_id:
                del self.companion_data["defects"][i]
                break
        
        # Refresh the UI
        self.populate_defects()
        self.calculate_cp_totals()
    
    def update_derived_values(self):
        # Update the companion_data with current stats from inputs
        current_stats = {stat: spin.value() for stat, spin in self.stat_inputs.items()}
        self.companion_data["stats"] = current_stats
        
        # Use the main application's calculate_derived_values function
        if hasattr(self.parent, 'calculate_derived_values'):
            # Calculate derived values using the main app's function
            derived_values = self.parent.calculate_derived_values(self.companion_data)
            
            # Update the companion data
            self.companion_data["derived"] = derived_values
            
            # Update labels
            self.derived_labels["Combat Value"].setText(str(derived_values["CV"]))
            self.derived_labels["Attack Combat Value"].setText(str(derived_values["ACV"]))
            self.derived_labels["Defense Combat Value"].setText(str(derived_values["DCV"]))
            self.derived_labels["Health Points"].setText(str(derived_values["HP"]))
            self.derived_labels["Energy Points"].setText(str(derived_values["EP"]))
            self.derived_labels["Shock Value"].setText(str(derived_values["SV"]))
            self.derived_labels["Damage Multiplier"].setText(str(derived_values["DM"]))
            self.derived_labels["Sanity Points"].setText(str(derived_values["SP"]))
            self.derived_labels["Society Points"].setText(str(derived_values["SOP"]))
        else:
            # Fallback if the main app's function is not available
            body = current_stats["Body"]
            mind = current_stats["Mind"]
            soul = current_stats["Soul"]
            
            # Calculate derived values
            cv = math.floor((body + mind + soul) / 3)
            acv = cv
            dcv = cv
            hp = body * 10
            ep = mind * 10
            sv = body * 2
            dm = math.floor((body + soul) / 2)
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

    def get_companion_data(self):
        # Update stats from inputs
        stats = {stat: spin.value() for stat, spin in self.stat_inputs.items()}
        
        # Get the current level
        level = self.level_input.value()
        
        # Calculate CP budget based on level
        cp_budget = level * 10
        
        # Create a temporary data structure with the current companion data
        temp_data = {
            "id": self.original_id or str(uuid.uuid4()),
            "name": self.name_input.text(),
            "level": level,
            "cp_budget": cp_budget,  # Always set CP budget based on current level
            "description": self.description_input.toPlainText(),
            "stats": stats,
            "attributes": self.companion_data["attributes"],
            "defects": self.companion_data["defects"]
        }
        
        # Calculate derived values using the main app's function if available
        if hasattr(self.parent, 'calculate_derived_values'):
            derived = self.parent.calculate_derived_values(temp_data)
        else:
            # Fallback to basic calculation if main app's function is not available
            body = stats["Body"]
            mind = stats["Mind"]
            soul = stats["Soul"]
            
            derived = {
                "CV": math.floor((body + mind + soul) / 3),
                "ACV": math.floor((body + mind + soul) / 3),
                "DCV": math.floor((body + mind + soul) / 3),
                "HP": body * 10,
                "EP": mind * 10,
                "SV": body * 2,
                "DM": math.floor((body + soul) / 2),
                "SP": soul * 10,
                "SOP": mind * 10
            }
        
        # Add the derived values to the data
        temp_data["derived"] = derived
        
        return temp_data

    def save_to_library(self):
        # Implement saving to library if needed
        QMessageBox.information(self, "Save to Library", "Feature not yet implemented.")

    def import_from_library(self):
        from dialogs.library_selector_dialog import LibrarySelectorDialog
        selector = LibrarySelectorDialog(self, "companions")
        if selector.exec_() == QDialog.Accepted:
            selected_obj = selector.get_selected_object()
            if selected_obj and selected_obj != "CREATE_NEW":
                self.populate_from_library(selected_obj)

    def populate_from_library(self, data):
        # Populate dialog fields from imported data
        self.name_input.setText(data.get("name", ""))
        self.level_input.setValue(data.get("level", 1))
        stats = data.get("stats", {})
        for stat, spin in self.stat_inputs.items():
            spin.setValue(stats.get(stat, 4))
        self.companion_data.update(data)
        self.calculate_cp_totals()
        self.update_derived_values()
        self.populate_attributes()
        self.populate_defects()
