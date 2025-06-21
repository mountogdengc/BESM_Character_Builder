import sys
import os
import json
import uuid
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QCheckBox, QGroupBox, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from dialogs.attribute_builder_dialog import AttributeBuilderDialog

class UnknownPowerDialog(QDialog):
    """Dialog for managing hidden attributes from the Unknown Power attribute"""
    
    def __init__(self, parent, unknown_power_attr):
        super().__init__(parent)
        self.parent = parent
        self.unknown_power_attr = unknown_power_attr
        self.hidden_attributes = parent.character_data.get("hidden_attributes", [])
        self.cp_spent = unknown_power_attr.get("cp_spent", 0)
        self.available_points = unknown_power_attr.get("gm_points", 0)
        self.used_points = self.calculate_used_points()
        
        self.setWindowTitle("Unknown Power Manager")
        self.resize(800, 600)
        
        self.init_ui()
        
    def calculate_used_points(self):
        """Calculate the total points used by hidden attributes"""
        total = 0
        for attr in self.hidden_attributes:
            # Get the cost per level from the attribute definition
            attr_def = self.parent.attributes_by_key.get(attr.get("key"))
            if attr_def:
                cost_per_level = attr_def.get("cost_per_level", 1)
                level = attr.get("level", 1)
                total += cost_per_level * level
        return total
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Information section
        info_group = QGroupBox("Unknown Power Information")
        info_layout = QFormLayout()
        
        # Points allocated by player (with spin box for adjustment)
        self.cp_spin = QSpinBox()
        self.cp_spin.setMinimum(1)
        self.cp_spin.setMaximum(100)  # Set a reasonable maximum
        self.cp_spin.setValue(self.cp_spent)
        self.cp_spin.valueChanged.connect(self.update_cp_spent)
        info_layout.addRow("Character Points Spent:", self.cp_spin)
        
        # GM points (with 50% bonus)
        self.gm_points_label = QLabel(f"{self.available_points}")
        info_layout.addRow("Total GM Points (with 50% bonus):", self.gm_points_label)
        
        # Points used
        self.used_points_label = QLabel(f"{self.used_points}")
        info_layout.addRow("Points Used:", self.used_points_label)
        
        # Points remaining
        self.remaining_points_label = QLabel(f"{self.available_points - self.used_points}")
        info_layout.addRow("Points Remaining:", self.remaining_points_label)
        
        # Add a note about CP adjustment
        note_label = QLabel("Note: Adjusting Character Points will recalculate GM points (50% bonus)")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        info_layout.addRow("", note_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Hidden attributes section
        hidden_attrs_group = QGroupBox("Hidden Attributes")
        hidden_attrs_layout = QVBoxLayout()
        
        # List of hidden attributes
        self.hidden_attrs_list = QListWidget()
        self.refresh_hidden_attrs_list()
        hidden_attrs_layout.addWidget(self.hidden_attrs_list)
        
        # Buttons for managing hidden attributes
        buttons_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Hidden Attribute")
        self.add_btn.clicked.connect(self.add_hidden_attribute)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_hidden_attribute)
        buttons_layout.addWidget(self.edit_btn)
        
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_hidden_attribute)
        buttons_layout.addWidget(self.remove_btn)
        
        self.reveal_btn = QPushButton("Reveal Selected")
        self.reveal_btn.clicked.connect(self.reveal_hidden_attribute)
        buttons_layout.addWidget(self.reveal_btn)
        
        hidden_attrs_layout.addLayout(buttons_layout)
        hidden_attrs_group.setLayout(hidden_attrs_layout)
        layout.addWidget(hidden_attrs_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def refresh_hidden_attrs_list(self):
        """Refresh the list of hidden attributes"""
        self.hidden_attrs_list.clear()
        
        for attr in self.hidden_attributes:
            # Get the attribute definition
            attr_def = self.parent.attributes_by_key.get(attr.get("key"))
            if attr_def:
                name = attr.get("custom_name", attr_def.get("name", "Unknown"))
                level = attr.get("level", 1)
                cost_per_level = attr_def.get("cost_per_level", 1)
                total_cost = cost_per_level * level
                revealed = attr.get("revealed", False)
                
                # Create the list item
                item_text = f"{name} (Level {level}, {total_cost} CP)"
                if revealed:
                    item_text += " [REVEALED]"
                    
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, attr)
                self.hidden_attrs_list.addItem(item)
                
        # Update the points labels
        self.used_points = self.calculate_used_points()
        self.used_points_label.setText(f"{self.used_points}")
        self.remaining_points_label.setText(f"{self.available_points - self.used_points}")
        
    def add_hidden_attribute(self):
        """Add a new hidden attribute"""
        dialog = AttributeBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            new_attr = dialog.get_attribute_data()
            
            # Calculate the cost of this attribute
            attr_def = self.parent.attributes_by_key.get(new_attr.get("key"))
            if attr_def:
                cost_per_level = attr_def.get("cost_per_level", 1)
                level = new_attr.get("level", 1)
                total_cost = cost_per_level * level
                
                # Check if we have enough points
                if total_cost > (self.available_points - self.used_points):
                    QMessageBox.warning(
                        self,
                        "Not Enough Points",
                        f"This attribute costs {total_cost} CP, but you only have {self.available_points - self.used_points} CP remaining."
                    )
                    return
                
                # Add the attribute to the hidden attributes
                new_attr["id"] = str(uuid.uuid4())
                new_attr["revealed"] = False
                self.hidden_attributes.append(new_attr)
                
                # Refresh the list
                self.refresh_hidden_attrs_list()
                
    def edit_hidden_attribute(self):
        """Edit the selected hidden attribute"""
        selected_items = self.hidden_attrs_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an attribute to edit.")
            return
            
        # Get the selected attribute
        selected_item = selected_items[0]
        attr = selected_item.data(Qt.UserRole)
        
        # Get the old cost
        attr_def = self.parent.attributes_by_key.get(attr.get("key"))
        if attr_def:
            old_cost_per_level = attr_def.get("cost_per_level", 1)
            old_level = attr.get("level", 1)
            old_total_cost = old_cost_per_level * old_level
        
        # Open the attribute builder dialog
        dialog = AttributeBuilderDialog(self.parent, attr)
        if dialog.exec_() == QDialog.Accepted:
            edited_attr = dialog.get_attribute_data()
            
            # Calculate the new cost
            attr_def = self.parent.attributes_by_key.get(edited_attr.get("key"))
            if attr_def:
                cost_per_level = attr_def.get("cost_per_level", 1)
                level = edited_attr.get("level", 1)
                new_total_cost = cost_per_level * level
                
                # Check if we have enough points for the change
                if (self.used_points - old_total_cost + new_total_cost) > self.available_points:
                    QMessageBox.warning(
                        self,
                        "Not Enough Points",
                        f"This change would increase the cost by {new_total_cost - old_total_cost} CP, "
                        f"but you only have {self.available_points - self.used_points} CP remaining."
                    )
                    return
                
                # Update the attribute
                edited_attr["id"] = attr["id"]
                edited_attr["revealed"] = attr.get("revealed", False)
                
                # Find and replace the attribute in the list
                for i, a in enumerate(self.hidden_attributes):
                    if a["id"] == attr["id"]:
                        self.hidden_attributes[i] = edited_attr
                        break
                
                # Refresh the list
                self.refresh_hidden_attrs_list()
                
    def remove_hidden_attribute(self):
        """Remove the selected hidden attribute"""
        selected_items = self.hidden_attrs_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an attribute to remove.")
            return
            
        # Get the selected attribute
        selected_item = selected_items[0]
        attr = selected_item.data(Qt.UserRole)
        
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Remove Hidden Attribute",
            f"Are you sure you want to remove '{attr.get('custom_name', attr.get('name', 'Unknown'))}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove the attribute from the list
            self.hidden_attributes = [a for a in self.hidden_attributes if a["id"] != attr["id"]]
            
            # Refresh the list
            self.refresh_hidden_attrs_list()
            
    def reveal_hidden_attribute(self):
        """Reveal the selected hidden attribute to the player"""
        selected_items = self.hidden_attrs_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an attribute to reveal.")
            return
            
        # Get the selected attribute
        selected_item = selected_items[0]
        attr = selected_item.data(Qt.UserRole)
        
        # Check if it's already revealed
        if attr.get("revealed", False):
            QMessageBox.information(self, "Already Revealed", "This attribute has already been revealed.")
            return
            
        # Confirm revelation
        reply = QMessageBox.question(
            self,
            "Reveal Hidden Attribute",
            f"Are you sure you want to reveal '{attr.get('custom_name', attr.get('name', 'Unknown'))}' to the player?\n\n"
            "This will add it to their character sheet as a regular attribute.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Mark as revealed
            for a in self.hidden_attributes:
                if a["id"] == attr["id"]:
                    a["revealed"] = True
                    
                    # Add to character's attributes
                    revealed_attr = a.copy()
                    revealed_attr["id"] = str(uuid.uuid4())  # New ID for the revealed attribute
                    revealed_attr["source"] = "Unknown Power"
                    self.parent.character_data["attributes"].append(revealed_attr)
                    break
            
            # Refresh the list and the parent's UI
            self.refresh_hidden_attrs_list()
            from tabs.attributes_tab import sync_attributes
            sync_attributes(self.parent)
            self.parent.update_derived_values()
            
    def update_cp_spent(self, value):
        """Update CP spent and recalculate GM points"""
        import math
        
        # Update the CP spent value
        self.cp_spent = value
        
        # Recalculate GM points (50% bonus rounded up)
        self.available_points = math.ceil(self.cp_spent * 1.5)
        
        # Update labels
        self.gm_points_label.setText(f"{self.available_points}")
        self.remaining_points_label.setText(f"{self.available_points - self.used_points}")
    
    def accept(self):
        """Save changes and close the dialog and update parent totals"""
        # Save hidden attributes back to the character data
        self.parent.character_data["hidden_attributes"] = self.hidden_attributes

        # Update the Unknown Power attribute with the latest CP values
        for attr in self.parent.character_data["attributes"]:
            if attr.get("key") == "unknown_power" and attr["id"] == self.unknown_power_attr["id"]:
                attr["cp_spent"] = self.cp_spent
                attr["cost"] = self.cp_spent  # Charge the player ONLY what they actually spent
                attr["gm_points"] = self.available_points
                attr["description"] = (
                    f"GM has {self.available_points} points to assign to hidden attributes that will be revealed during play."
                )
                break

        # Refresh UI elements in the parent window so the change is visible immediately
        from tabs.attributes_tab import sync_attributes
        sync_attributes(self.parent)
        self.parent.update_point_total()

        super().accept()
        
def reveal_hidden_attribute(self):
    """Reveal the selected hidden attribute to the player"""
    selected_items = self.hidden_attrs_list.selectedItems()
    if not selected_items:
        QMessageBox.warning(self, "No Selection", "Please select an attribute to reveal.")
        return
        
    # Get the selected attribute
    selected_item = selected_items[0]
    attr = selected_item.data(Qt.UserRole)
    
    # Check if it's already revealed
    if attr.get("revealed", False):
        QMessageBox.information(self, "Already Revealed", "This attribute has already been revealed.")
        return
        
    # Confirm revelation
    reply = QMessageBox.question(
        self,
        "Reveal Hidden Attribute",
        f"Are you sure you want to reveal '{attr.get('custom_name', attr.get('name', 'Unknown'))}' to the player?\n\n"
        "This will add it to their character sheet as a regular attribute.",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        # Mark as revealed
        for a in self.hidden_attributes:
            if a["id"] == attr["id"]:
                a["revealed"] = True
                
                # Add to character's attributes
                revealed_attr = a.copy()
                revealed_attr["id"] = str(uuid.uuid4())  # New ID for the revealed attribute
                revealed_attr["source"] = "Unknown Power"
                self.parent.character_data["attributes"].append(revealed_attr)
                break
        
        # Refresh the list and the parent's UI
        self.refresh_hidden_attrs_list()
        from tabs.attributes_tab import sync_attributes
        sync_attributes(self.parent)
        self.parent.update_derived_values()
        
def update_cp_spent(self, value):
    """Update CP spent and recalculate GM points"""
    import math
    
    # Update the CP spent value
    self.cp_spent = value
    
    # Recalculate GM points (50% bonus rounded up)
    self.available_points = math.ceil(self.cp_spent * 1.5)
    
    # Update labels
    self.gm_points_label.setText(f"{self.available_points}")
    self.remaining_points_label.setText(f"{self.available_points - self.used_points}")
    
def accept(self):
    """Save changes and close the dialog"""
    # Save the hidden attributes to the character data
    self.parent.character_data["hidden_attributes"] = self.hidden_attributes
    
    # Update the unknown power attribute with new CP spent and GM points
    for attr in self.parent.character_data["attributes"]:
        if attr.get("key") == "unknown_power" and attr["id"] == self.unknown_power_attr["id"]:
            attr["cp_spent"] = self.cp_spent
            # The player should only pay the CP they actually spent, NOT the GM bonus
            attr["cost"] = self.cp_spent
            attr["gm_points"] = self.available_points
            attr["description"] = (
                f"GM has {self.available_points} points to assign to hidden attributes that will be revealed during play."
            )
            break
            
    # Refresh parent's UI and CP totals so the change is visible immediately
    from tabs.attributes_tab import sync_attributes
    sync_attributes(self.parent)
    self.parent.update_point_total()
    super().accept()
