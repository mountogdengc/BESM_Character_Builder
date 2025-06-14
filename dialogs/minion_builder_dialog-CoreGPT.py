# minion_builder_dialog.py

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

class MinionBuilderDialog(QDialog):
    def __init__(self, parent=None, minion_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Minions")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.parent = parent

        self.minion_data = minion_data or {}
        self.original_id = minion_data.get("id") if minion_data else None
        
        # Ensure attributes and defects are lists
        if "attributes" not in self.minion_data:
            self.minion_data["attributes"] = []
        if "defects" not in self.minion_data:
            self.minion_data["defects"] = []
        
        # Initialize attributes that will be set later
        self.stat_inputs = {}
        self.derived_labels = {}
        self.total_cp_spent = 0
        self.max_cp = self.calculate_max_cp()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Header with name, level, and CP info ---
        header_layout = QHBoxLayout()
        
        # Left side - Minion name and count
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.minion_data.get("name", ""))
        form_layout.addRow("Minion Group Name:", self.name_input)

        self.level_input = QSpinBox()
        self.level_input.setRange(1, 6)  # BESM4e limits Minions to 6 levels
        self.level_input.setValue(self.minion_data.get("level", 1))
        self.level_input.valueChanged.connect(self.update_minion_count)
        form_layout.addRow("Minion Level:", self.level_input)
        
        self.count_label = QLabel()
        form_layout.addRow("Number of Minions:", self.count_label)
        
        header_layout.addLayout(form_layout)
        header_layout.addStretch()
        
        # Right side - CP info
        cp_layout = QFormLayout()
        
        self.max_cp_label = QLabel()
        self.max_cp_label.setText(f"Max CP per Minion: {self.max_cp}")
        cp_layout.addRow("", self.max_cp_label)
        
        self.cp_spent_label = QLabel()
        cp_layout.addRow("", self.cp_spent_label)
        
        self.cp_remaining_label = QLabel()
        cp_layout.addRow("", self.cp_remaining_label)
        
        # Now that all labels are created, update the minion count and CP info
        self.update_minion_count()
        
        header_layout.addLayout(cp_layout)
        
        layout.addLayout(header_layout)
        
        # Add description
        description = QLabel("Minions are loyal and dedicated human or creature resources eager to carry out your character's commands. " +
                           "They ask for very little in return and always aim to please, even at their own expense. " +
                           "All minions created by this attribute normally have identical Stats, Attributes, and Defects.")
        description.setWordWrap(True)
        layout.addWidget(description)

        # --- Tabs for Stats / Attributes / Defects / Description ---
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.init_stats_tab()
        self.init_attributes_tab()
        self.init_defects_tab()
        self.init_description_tab()
        
        # Now that all UI elements are initialized, update CP labels
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

    def init_stats_tab(self):
        tab = QWidget()
        form = QFormLayout()

        # Description
        description = QLabel("Set the base stats for all minions in this group. Each minion has the same stats.")
        description.setWordWrap(True)
        form.addRow(description)
        
        # Stats
        self.stat_inputs = {}
        for stat in ["Body", "Mind", "Soul"]:
            spin = QSpinBox()
            spin.setRange(1, 12)  # Standard BESM range
            spin.setValue(self.minion_data.get("stats", {}).get(stat, 4))  # Default to 4
            spin.valueChanged.connect(self.calculate_cp_totals)
            self.stat_inputs[stat] = spin
            form.addRow(f"{stat}:", spin)
        
        # Derived values
        self.derived_labels = {}
        derived_grid = QGridLayout()
        
        row = 0
        col = 0
        for derived in ["Combat Value", "Attack Combat Value", "Defense Combat Value", 
                       "Health Points", "Energy Points", "Shock Value", 
                       "Damage Multiplier", "Sanity Points", "Society Points"]:
            label = QLabel(derived + ":")
            value = QLabel("0")
            value.setStyleSheet("font-weight: bold;")
            self.derived_labels[derived] = value
            
            derived_grid.addWidget(label, row, col * 2)
            derived_grid.addWidget(value, row, col * 2 + 1)
            
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
        
        form.addRow(QLabel("Derived Values:"))
        form.addRow(derived_grid)
        
        # Update derived values when stats change
        for stat_input in self.stat_inputs.values():
            stat_input.valueChanged.connect(self.update_derived_values)
        
        # Initial update of derived values after all labels are created
        self.update_derived_values()
        
        tab.setLayout(form)
        self.tabs.addTab(tab, "Stats")

    def init_attributes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Attributes represent your minions' special abilities and features.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add button
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Attribute")
        add_btn.clicked.connect(self.add_attribute)
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Scroll area for attributes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        attr_container = QWidget()
        self.attr_layout = QVBoxLayout(attr_container)
        self.attr_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(attr_container)
        layout.addWidget(scroll)
        
        # Populate existing attributes
        self.populate_attributes()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Attributes")

    def init_defects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description
        description = QLabel("Defects represent your minions' weaknesses and limitations.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add button
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Defect")
        add_btn.clicked.connect(self.add_defect)
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Scroll area for defects
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        defect_container = QWidget()
        self.defect_layout = QVBoxLayout(defect_container)
        self.defect_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(defect_container)
        layout.addWidget(scroll)
        
        # Populate existing defects
        self.populate_defects()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Defects")

    def init_description_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Description field
        layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter a description of your minions here...")
        self.description_input.setText(self.minion_data.get("description", ""))
        layout.addWidget(self.description_input)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Description")

    def calculate_max_cp(self):
        # Minions can have up to 1/5 of the character's total CP
        character_cp = self.parent.character_data.get("total_cp", 60)
        return math.floor(character_cp / 5)

    def update_minion_count(self):
        level = self.level_input.value()
        count_ranges = {
            1: "Up to 5 Minions",
            2: "6-10 Minions",
            3: "11-25 Minions",
            4: "26-50 Minions",
            5: "51-100 Minions",
            6: "101-200 Minions"
        }
        self.count_label.setText(count_ranges.get(level, "Unknown"))
        
        # Update max CP label when level changes
        self.max_cp = self.calculate_max_cp()
        self.max_cp_label.setText(f"Max CP per Minion: {self.max_cp}")
        
        # Recalculate CP totals
        self.calculate_cp_totals()

    def calculate_cp_totals(self):
        # Calculate CP from stats
        stat_cp = sum(spin.value() * 2 for spin in self.stat_inputs.values())
        
        # Calculate CP from attributes
        attr_cp = sum(attr.get("cost", 0) for attr in self.minion_data["attributes"])
        
        # Calculate CP from defects (negative)
        defect_cp = sum(defect.get("cost", 0) for defect in self.minion_data["defects"])
        
        # Total CP spent
        self.total_cp_spent = stat_cp + attr_cp + defect_cp
        
        # Update labels
        self.cp_spent_label.setText(f"CP Spent: {self.total_cp_spent}")
        
        remaining = self.max_cp - self.total_cp_spent
        self.cp_remaining_label.setText(f"CP Remaining: {remaining}")
        
        # Highlight if over budget
        if remaining < 0:
            self.cp_remaining_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.cp_remaining_label.setStyleSheet("color: green; font-weight: bold;")

    def populate_attributes(self):
        # Clear existing widgets
        for i in reversed(range(self.attr_layout.count())): 
            widget = self.attr_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add attribute cards
        for attr in self.minion_data["attributes"]:
            self.add_attribute_card(attr)
    
    def populate_defects(self):
        # Clear existing widgets
        for i in reversed(range(self.defect_layout.count())): 
            widget = self.defect_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add defect cards
        for defect in self.minion_data["defects"]:
            self.add_defect_card(defect)
    
    def add_attribute(self):
        dialog = AttributeBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            attr = dialog.get_attribute_data()
            # Add ID if not present
            if "id" not in attr:
                attr["id"] = str(uuid.uuid4())
            self.minion_data["attributes"].append(attr)
            self.add_attribute_card(attr)
            self.calculate_cp_totals()
    
    def add_defect(self):
        dialog = DefectBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            defect = dialog.get_defect_data()
            # Add ID if not present
            if "id" not in defect:
                defect["id"] = str(uuid.uuid4())
            self.minion_data["defects"].append(defect)
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
        for i, attr in enumerate(self.minion_data["attributes"]):
            if attr.get("id") == attr_id:
                del self.minion_data["attributes"][i]
                break
        
        # Refresh the UI
        self.populate_attributes()
        self.calculate_cp_totals()
    
    def remove_defect(self, defect_id):
        # Find and remove the defect
        for i, defect in enumerate(self.minion_data["defects"]):
            if defect.get("id") == defect_id:
                del self.minion_data["defects"][i]
                break
        
        # Refresh the UI
        self.populate_defects()
        self.calculate_cp_totals()
    
    def update_derived_values(self):
        # Update the minion_data with current stats from inputs
        current_stats = {stat: spin.value() for stat, spin in self.stat_inputs.items()}
        self.minion_data["stats"] = current_stats
        
        # Use the main application's calculate_derived_values function
        if hasattr(self.parent, 'calculate_derived_values'):
            # Calculate derived values using the main app's function
            derived_values = self.parent.calculate_derived_values(self.minion_data)
            
            # Update the minion data
            self.minion_data["derived"] = derived_values
            
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

    def get_minion_data(self):
        # Update stats from inputs
        stats = {stat: spin.value() for stat, spin in self.stat_inputs.items()}
        
        # Get level and calculate count range
        level = self.level_input.value()
        count_ranges = {
            1: "Up to 5",
            2: "6-10",
            3: "11-25",
            4: "26-50",
            5: "51-100",
            6: "101-200"
        }
        count = count_ranges.get(level, "Unknown")
        
        # Create a temporary data structure with the current minion data
        temp_data = {
            "id": self.original_id or str(uuid.uuid4()),
            "name": self.name_input.text(),
            "level": level,
            "count": count,
            "description": self.description_input.toPlainText(),
            "stats": stats,
            "attributes": self.minion_data["attributes"],
            "defects": self.minion_data["defects"],
            "total_cp": self.total_cp_spent
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
