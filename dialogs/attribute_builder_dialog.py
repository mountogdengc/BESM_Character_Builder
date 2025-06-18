import json
import os
import uuid

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QPushButton, QScrollArea, QWidget, QFormLayout,
    QGroupBox, QListWidget, QListWidgetItem, QCompleter, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt, QStringListModel, QEvent, QTimer

from dialogs.enhancement_dialog import EnhancementDialog
from dialogs.limiter_dialog import LimiterDialog

class AttributeBuilderDialog(QDialog):
    def __init__(self, parent=None, existing_attr=None, base_attributes=None):
        super().__init__(parent)
        
        # Load attribute, enhancement, limiter data
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Adjust base path

        with open(os.path.join(base_path, "data", "attributes.json"), "r", encoding="utf-8") as f:  # Correct path to data folder
            raw_attributes = json.load(f)["attributes"]
            self.attributes = {attr["name"]: attr for attr in raw_attributes}

        with open(os.path.join(base_path, "data", "enhancements.json"), "r", encoding="utf-8") as f:
            self.raw_enhancements = json.load(f)["enhancements"]
            # Group enhancements by category
            self.enhancement_categories = self._group_by_category(self.raw_enhancements)

        with open(os.path.join(base_path, "data", "limiters.json"), "r", encoding="utf-8") as f:
            self.raw_limiters = json.load(f)["limiters"]
            # Group limiters by category
            self.limiter_categories = self._group_by_category(self.raw_limiters)

        # Load power packs
        with open(os.path.join(base_path, "data", "power_packs.json"), "r", encoding="utf-8") as f:
            self.power_packs = json.load(f)["power_packs"]
        
        # Initialize enhancement and limiter counts
        self.enhancement_counts = {}
        self.limiter_counts = {}
        
        # Initialize attribute cost per level
        self.attribute_cost_per_level = 1  # Default cost per level
        
        # Define maximum number of times each enhancement can be selected
        self.max_enhancement_picks = {
            "Area": 6,
            "Duration": 6,
            "Potent": 6,
            "Range": 6,
            "Targets": 6
        }
        
        # Define maximum number of times each limiter can be selected
        self.max_limiter_picks = {
            "Maximum (Lvl 3-4 Max)": 1,
            "Maximum (Lvl 5+ Max)": 1,
            "Maximum (Lvl 2 Max)": 1
        }
        
        # Track if an existing attribute is being edited
        self.existing_attribute_id = None
        if existing_attr and "id" in existing_attr:
            self.existing_attribute_id = existing_attr["id"]
            
        # Allow caller to customize attributes
        self.custom_attributes = base_attributes
        
        self.setWindowTitle("Attribute Builder")
        self.setMinimumWidth(600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        form_layout = QFormLayout()
        
        # Attribute dropdown
        self.attr_dropdown = QComboBox()
        # Don't connect yet
        self.attr_dropdown.blockSignals(True)
        self.attr_dropdown.addItems(sorted(self.attributes.keys()))
        self.attr_dropdown.blockSignals(False)

        # Delay connection until after caller has a chance to set attr
        QTimer.singleShot(0, lambda: self.attr_dropdown.currentTextChanged.connect(self.update_attribute_info))

        form_layout.addRow("Attribute:", self.attr_dropdown)

        # Editable name
        self.custom_name_input = QLineEdit()
        form_layout.addRow("Custom Name:", self.custom_name_input)

        # Level
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 10)
        self.level_spin.setValue(1)
        self.level_spin.valueChanged.connect(self.update_cp_cost)
        form_layout.addRow("Level:", self.level_spin)

        # CP Cost (calculated)
        self.cp_cost_label = QLabel("0")
        form_layout.addRow("CP Cost:", self.cp_cost_label)

        self.cp_cost_label.setStyleSheet("font-weight: bold; color: darkblue;")

        # Selected Enhancements and Limiters Section
        self.customization_group = QGroupBox("Customization")
        customization_layout = QVBoxLayout()
        
        # Selected Enhancements list
        self.selected_enhancements_label = QLabel("Selected Enhancements:")
        customization_layout.addWidget(self.selected_enhancements_label)
        
        self.selected_enhancements_list = QListWidget()
        self.selected_enhancements_list.setMaximumHeight(100)
        customization_layout.addWidget(self.selected_enhancements_list)
        
        # Button to add enhancements
        self.add_enhancement_btn = QPushButton("Add Enhancements")
        self.add_enhancement_btn.clicked.connect(self.open_enhancement_dialog)
        customization_layout.addWidget(self.add_enhancement_btn)
        
        # Selected Limiters list
        self.selected_limiters_label = QLabel("Selected Limiters:")
        customization_layout.addWidget(self.selected_limiters_label)
        
        self.selected_limiters_list = QListWidget()
        self.selected_limiters_list.setMaximumHeight(100)
        customization_layout.addWidget(self.selected_limiters_list)
        
        # Button to add limiters
        self.add_limiter_btn = QPushButton("Add Limiters")
        self.add_limiter_btn.clicked.connect(self.open_limiter_dialog)
        customization_layout.addWidget(self.add_limiter_btn)
        
        self.customization_group.setLayout(customization_layout)
        form_layout.addRow(self.customization_group)

        # Custom fields group
        self.custom_field_group = QGroupBox("Custom Fields")
        self.custom_field_form = QFormLayout()
        self.custom_field_group.setLayout(self.custom_field_form)
        self.custom_input_widgets = {}

        # Power pack button
        self.power_pack_button = QPushButton("Use Power Pack")
        self.power_pack_button.clicked.connect(self.show_power_pack_dialog)
        form_layout.addRow(self.power_pack_button)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.custom_field_group)

        # Description - match the attribute builder dialog's approach
        self.description = QTextEdit()
        self.description.setReadOnly(True)
        self.description.setFixedHeight(80)
        self.layout.addWidget(QLabel("Description:"))
        self.layout.addWidget(self.description)

        # User description
        self.user_description = QTextEdit()
        self.user_description.setFixedHeight(80)
        self.layout.addWidget(QLabel("Notes:"))
        self.layout.addWidget(self.user_description)

        # Buttons for Ok/Cancel
        button_box = QHBoxLayout()
        self.save_to_library_btn = QPushButton("Save to Library")
        self.save_to_library_btn.clicked.connect(self.save_to_library)
        self.save_to_library_btn.setVisible(False)  # Only show for special types
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(self.save_to_library_btn)
        button_box.addStretch()
        button_box.addWidget(self.ok_button)
        button_box.addWidget(cancel_button)
        
        self.layout.addLayout(button_box)
        
        # Flag to track if the custom name has been edited
        self._custom_name_edited = False
        self.custom_name_input.textEdited.connect(self._track_custom_name_edit)
        
        # Load existing attribute data if provided
        if existing_attr:
            self.load_existing_attribute(existing_attr)
            
    def open_enhancement_dialog(self):
        """Open dialog to select enhancements"""
        dialog = EnhancementDialog(
            self, 
            self.get_selected_enhancements(), 
            self.enhancement_counts
        )
        
        if dialog.exec_() == QDialog.Accepted:
            self.enhancement_counts = dialog.get_selected_enhancements()
            self.update_selected_enhancements_display()
            self.update_cp_cost()
    
    def open_limiter_dialog(self):
        """Open dialog to select limiters"""
        dialog = LimiterDialog(
            self, 
            self.get_selected_limiters(), 
            self.limiter_counts
        )
        
        if dialog.exec_() == QDialog.Accepted:
            self.limiter_counts = dialog.get_selected_limiters()
            self.update_selected_limiters_display()
            self.update_cp_cost()
    
    def get_selected_enhancements(self):
        """Get list of enhancement names that have a count > 0"""
        return [name for name, count in self.enhancement_counts.items() if count > 0]
    
    def get_selected_limiters(self):
        """Get list of limiter names that have a count > 0"""
        return [name for name, count in self.limiter_counts.items() if count > 0]
    
    def update_selected_enhancements_display(self):
        """Update the selected enhancements list display"""
        self.selected_enhancements_list.clear()
        
        for name, count in self.enhancement_counts.items():
            if count > 0:
                max_count = self.max_enhancement_picks.get(name, 1)
                item = QListWidgetItem(f"(E) {name} ({count}/{max_count})")
                self.selected_enhancements_list.addItem(item)
    
    def update_selected_limiters_display(self):
        """Update the selected limiters list display"""
        self.selected_limiters_list.clear()
        
        for name, count in self.limiter_counts.items():
            if count > 0:
                max_count = self.max_limiter_picks.get(name, 1)
                item = QListWidgetItem(f"(L) {name} ({count}/{max_count})")
                self.selected_limiters_list.addItem(item)

    def _group_by_category(self, items):
        """Group the items by category for display"""
        categories = {}
        for item in items:
            category = item.get("category", "Uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        return categories
        
    def load_existing_attribute(self, attribute_data):
        """Load an existing attribute into the dialog for editing"""
        try:
            # Set the attribute dropdown
            attr_name = attribute_data.get("name", "")
            if attr_name:
                index = self.attr_dropdown.findText(attr_name)
                if index >= 0:
                    self.attr_dropdown.setCurrentIndex(index)
                    self.update_attribute_info()
                
            # Set the custom name
            self.custom_name_input.setText(attr_name)
            self._custom_name_edited = True
            
            # Set the level
            level = attribute_data.get("level", 1)
            self.level_spin.setValue(level)
            
            # Set the user description
            user_description = attribute_data.get("user_description", "")
            self.user_description.setPlainText(user_description)
            
            # Special handling for Skill Group attribute
            attr_key = attribute_data.get("key", "")
            if attr_key == "skill_group":
                print(f"\n--- DEBUG: Loading Skill Group attribute ---")
                print(f"Attribute data: {attribute_data}")
                
                # Get the attribute definition from attributes.json
                attr_def = self.attributes.get(attr_name, {})
                if not attr_def and "base_name" in attribute_data:
                    attr_def = self.attributes.get(attribute_data["base_name"], {})
                    
                print(f"Attribute definition: {attr_def}")
                
                # Set dynamic cost information from the attribute definition
                self.dynamic_cost_map = attr_def.get("dynamic_cost_map", {})
                self.dynamic_cost_category_key = attr_def.get("dynamic_cost_category_key", None)
                
                print(f"Dynamic cost map: {self.dynamic_cost_map}")
                print(f"Dynamic cost category key: {self.dynamic_cost_category_key}")
            
            # Load custom fields if any
            if "custom_fields" in attribute_data and isinstance(attribute_data["custom_fields"], dict):
                print(f"Loading custom fields: {attribute_data['custom_fields']}")
                for key, value in attribute_data["custom_fields"].items():
                    # Find the widget for this key
                    for i in range(self.custom_field_layout.count()):
                        widget_item = self.custom_field_layout.itemAt(i)
                        if widget_item and widget_item.widget():
                            field_widget = widget_item.widget()
                            if hasattr(field_widget, "objectName") and field_widget.objectName() == key:
                                # Set the value based on widget type
                                if isinstance(field_widget, QLineEdit):
                                    field_widget.setText(str(value))
                                elif isinstance(field_widget, QTextEdit):
                                    field_widget.setPlainText(str(value))
                                elif isinstance(field_widget, QComboBox):
                                    index = field_widget.findText(str(value))
                                    if index >= 0:
                                        field_widget.setCurrentIndex(index)
                                elif isinstance(field_widget, QSpinBox):
                                    field_widget.setValue(int(value))
                                print(f"Set field {key} to {value}")
                                break
            
            # Load enhancements if any
            if "enhancements" in attribute_data and isinstance(attribute_data["enhancements"], list):
                for enhancement in attribute_data["enhancements"]:
                    self.add_enhancement(enhancement)
                    
            # Load limiters if any
            if "limiters" in attribute_data and isinstance(attribute_data["limiters"], list):
                for limiter in attribute_data["limiters"]:
                    self.add_limiter(limiter)
                    
            # Update the CP cost
            self.update_cp_cost()
        except Exception as e:
            print(f"Error loading existing attribute: {e}")
            import traceback
            traceback.print_exc()
            import traceback
            traceback.print_exc()
    
    def get_selected_enhancements(self):
        """Get list of enhancement names that have a count > 0"""
        return [name for name, count in self.enhancement_counts.items() if count > 0]
        
    def get_selected_limiters(self):
        """Get list of limiter names that have a count > 0"""
        return [name for name, count in self.limiter_counts.items() if count > 0]
        
    def update_selected_enhancements_display(self):
        """Update the selected enhancements list display"""
        self.selected_enhancements_list.clear()
            
        for name, count in self.enhancement_counts.items():
            if count > 0:
                max_count = self.max_enhancement_picks.get(name, 1)
                item = QListWidgetItem(f"(E) {name} ({count}/{max_count})")
                self.selected_enhancements_list.addItem(item)
        
    def update_selected_limiters_display(self):
        """Update the selected limiters list display"""
        self.selected_limiters_list.clear()
            
        for name, count in self.limiter_counts.items():
            if count > 0:
                max_count = self.max_limiter_picks.get(name, 1)
                item = QListWidgetItem(f"(L) {name} ({count}/{max_count})")
                self.selected_limiters_list.addItem(item)

    def _group_by_category(self, items):
        """Group the items by category for display"""
        categories = {}
        for item in items:
            category = item.get("category", "Uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        return categories

    def add_custom_field_widget(self, field):
        """Add a widget for a custom field"""
        field_key = field.get("key", "")
        field_type = field.get("field_type", "text")
        field_label = field.get("label", field_key)
        field_options = field.get("options", [])
        field_description = field.get("description", "")
        
        # Create widget based on field type
        if field_type == "dropdown":
            # Create dropdown for select fields
            widget = QComboBox()
            widget.addItems(field_options)
            
            # If this is the dynamic cost category field, connect it to update costs
            if self.dynamic_cost_category_key and field_key == self.dynamic_cost_category_key:
                widget.currentTextChanged.connect(self.update_cp_cost)
                
        elif field_type == "textarea":
            # Create text area for longer text
            widget = QTextEdit()
            widget.setMaximumHeight(80)
            
        elif field_type == "number":
            # Create number input
            widget = QSpinBox()
            widget.setRange(0, 100)
            
        elif field_type == "list":
            # Create list input with autocomplete
            widget = QLineEdit()
            if "autocomplete_options" in field and field["autocomplete_options"]:
                completer = QCompleter(field["autocomplete_options"])
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                widget.setCompleter(completer)
                
        else:
            # Default to text input
            widget = QLineEdit()
            
        # Store reference to widget
        self.custom_input_widgets[field_key] = widget
        
        # Add to form layout with description if available
        if field_description:
            # Create a container for the field and its description
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add the widget
            container_layout.addWidget(widget)
            
            # Add description label
            desc_label = QLabel(field_description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("font-size: 8pt; color: gray;")
            container_layout.addWidget(desc_label)
            
            self.custom_field_form.addRow(field_label + ":", container)
        else:
            self.custom_field_form.addRow(field_label + ":", widget)

    def update_cp_cost(self):
        """Calculate and update the CP cost based on selections"""
        attribute_name = self.attr_dropdown.currentText()
        if not attribute_name:
            return
            
        # Calculate base attribute cost
        attribute = self.attributes.get(attribute_name)
        if not attribute:
            self.cp_cost_label.setText("0")
            return

        # Get the cost per level - handle dictionary costs
        try:
            if isinstance(attribute.get("cost_per_level"), dict):
                # Handle level bands
                level = self.level_spin.value()
                cost_map = attribute.get("cost_per_level")
                cost_per_level = 0
                
                # Find the right level band
                for level_band, cost in cost_map.items():
                    level_min, level_max = level_band.split("-")
                    level_min = int(level_min)
                    level_max = int(level_max) if level_max != "max" else float('inf')
                    
                    if level_min <= level <= level_max:
                        cost_per_level = cost
                        break
            else:
                cost_per_level = attribute.get("cost_per_level", 1)
        except Exception as e:
            print(f"Error calculating cost: {e}")
            cost_per_level = 1

    def update_cp_cost(self):
        """Update the CP cost based on level and modifiers"""
        # Get the cost per level from the attribute data
        attr_name = self.attr_dropdown.currentText()
        attr_data = self.attributes.get(attr_name, {})
        cost_per_level = attr_data.get("cost_per_level", self.attribute_cost_per_level)
        
        # Store the original cost per level before any dynamic adjustments
        original_cost_per_level = cost_per_level
        
        # For attributes with null cost_per_level (like Unknown Power), use level as cost
        if cost_per_level is None:
            base_cost = self.level_spin.value()
        else:
            base_cost = self.level_spin.value() * cost_per_level
        
        # Calculate enhancement multiplier
        enhancement_multiplier = 1.0
        for name, count in self.enhancement_counts.items():
            if count > 0:
                enhancement_data = self.enhancement_data.get(name, {})
                enhancement_value = enhancement_data.get("value", 0.1)
                enhancement_multiplier += enhancement_value * count
        
        # Apply enhancement multiplier
        total_cost = base_cost * enhancement_multiplier
        
        # Calculate limiter multiplier
        limiter_multiplier = 1.0
        for name, count in self.limiter_counts.items():
            if count > 0:
                limiter_data = self.limiter_data.get(name, {})
                limiter_value = limiter_data.get("value", 0.1)
                limiter_multiplier -= limiter_value * count
        
        # Ensure limiter multiplier doesn't go below 0.5
        limiter_multiplier = max(0.5, limiter_multiplier)
        
        total_cost = total_cost * limiter_multiplier
        
        # Apply any custom field-based cost modifications
        if hasattr(self, 'dynamic_cost_map') and self.dynamic_cost_map:
            try:
                # Check if we have a dynamic cost category
                if self.dynamic_cost_category_key and self.dynamic_cost_category_key in self.custom_input_widgets:
                    category_widget = self.custom_input_widgets[self.dynamic_cost_category_key]
                    if isinstance(category_widget, QComboBox):
                        selected_category = category_widget.currentText()
                        
                        # For Skill Group, we need to adjust the base cost per level
                        if selected_category in self.dynamic_cost_map:
                            # Replace the cost_per_level with the dynamic cost
                            dynamic_cost = self.dynamic_cost_map[selected_category]
                            
                            # Store the dynamic cost for later use in get_attribute_data
                            self.attribute_cost_per_level = dynamic_cost
                            
                            # Recalculate the base cost with the new cost per level
                            base_cost = self.level_spin.value() * dynamic_cost
                            
                            # Recalculate total cost with the new base cost
                            total_cost = base_cost * enhancement_multiplier * limiter_multiplier
                            
                            # Update the cost display to show the dynamic cost
                            cost_info = f"CP Cost: {total_cost} ({dynamic_cost} CP/level)"
                            self.cp_cost_label.setText(cost_info)
                            self.current_cp_cost = total_cost
                            return
            except Exception as e:
                print(f"Error applying dynamic cost: {e}")
                import traceback
                traceback.print_exc()
        
        # Reset to original cost per level if no dynamic cost was applied
        self.attribute_cost_per_level = original_cost_per_level
                
        # Round to nearest integer
        total_cost = round(total_cost)
        
        # Update UI
        self.cp_cost_label.setText(f"CP Cost: {total_cost}")
        self.current_cp_cost = total_cost
        
    def get_attribute_data(self):
        """Return the attribute data based on the dialog inputs"""
        # Get base attribute name and custom name
        base_name = self.attr_dropdown.currentText()
        name = self.custom_name_input.text() or base_name
        
        # Get custom field values
        custom_fields = {}
        for field_key, widget in self.custom_input_widgets.items():
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QTextEdit):
                value = widget.toPlainText()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            else:
                value = ""
            
            custom_fields[field_key] = value
        
        # Build attribute data structure
        attribute = {
            "name": name,
            "base_name": base_name,
            "level": self.level_spin.value(),
            "cost": self.current_cp_cost,  # Use the stored cost value instead of parsing the label
            "user_description": self.user_description.toPlainText(),
            "custom_fields": custom_fields
        }
        
        # Add description from base attribute
        base_attr = self.attributes.get(base_name, {})
        if "description" in base_attr:
            attribute["description"] = base_attr["description"]
            
        # Get the official attribute key if available
        if "key" in base_attr:
            attribute["key"] = base_attr["key"]
            
            # Special handling for specific attribute types
            if attribute["key"] == "unknown_power":
                # For Unknown Power, we need to track how many CP the player spent
                attribute["cp_spent"] = attribute["level"]
                # Calculate GM points (50% bonus rounded up)
                import math
                attribute["gm_points"] = math.ceil(attribute["level"] * 1.5)
                print(f"\n--- DEBUG: Unknown Power Processing ---")
                print(f"Level: {attribute['level']}, CP Spent: {attribute['cp_spent']}, GM Points: {attribute['gm_points']}")
            
            elif attribute["key"] == "skill_group":
                # For Skill Group, we need to include the selected group type
                print("\n--- DEBUG: Skill Group Attribute Processing ---")
                print(f"Initial attribute data: {attribute}")
                print(f"Dynamic cost category key: {self.dynamic_cost_category_key}")
                print(f"Custom fields: {attribute['custom_fields']}")
                print(f"Dynamic cost map: {self.dynamic_cost_map}")
                
                # Attempt to load dynamic cost info
                if not self.dynamic_cost_map:
                    # Try the newer naming 'dynamic_cost' first
                    self.dynamic_cost_map = base_attr.get("dynamic_cost", {})
                    if not self.dynamic_cost_map:
                        # Fallback to legacy key
                        self.dynamic_cost_map = base_attr.get("dynamic_cost_map", {})
                if not self.dynamic_cost_category_key:
                    # In current schema, the category dropdown is stored with key 'category'
                    self.dynamic_cost_category_key = base_attr.get("dynamic_cost_category_key", "category")
                print(f"Resolved dynamic cost map: {self.dynamic_cost_map}")
                print(f"Resolved dynamic cost category key: {self.dynamic_cost_category_key}")
                
                if self.dynamic_cost_category_key and self.dynamic_cost_category_key in attribute['custom_fields']:
                    selected_group = attribute['custom_fields'][self.dynamic_cost_category_key]
                    print(f"Selected group: {selected_group}")
                    
                    # Extract the cost from the selected group
                    if selected_group:
                        # Update the user description to include the selected group
                        if attribute["user_description"]:
                            # Only add the group type if it's not already in the description
                            if selected_group not in attribute["user_description"]:
                                attribute["user_description"] = f"{attribute['user_description']} ({selected_group})"
                        else:
                            attribute["user_description"] = f"({selected_group})"
                        
                        # Store the cost per level for reference
                        if selected_group in self.dynamic_cost_map:
                            cost_per_level = self.dynamic_cost_map[selected_group]
                            attribute["cost_per_level"] = cost_per_level
                            
                            # Recalculate the cost based on the dynamic cost per level
                            attribute["cost"] = cost_per_level * attribute["level"]
                            print(f"Updated cost calculation: {cost_per_level} * {attribute['level']} = {attribute['cost']}")
                        else:
                            print(f"WARNING: Selected group '{selected_group}' not found in dynamic_cost_map!")
                    else:
                        print("WARNING: Selected group is empty!")
                else:
                    print(f"WARNING: Dynamic cost category key '{self.dynamic_cost_category_key}' not found in custom fields!")
                    
                print(f"Final attribute data: {attribute}")
            
        # Add enhancement counts if any
        if self.enhancement_counts:
            attribute["enhancement_counts"] = self.enhancement_counts
            
        # Add selected limiters if any
        limiters = self.get_selected_limiters()
        if limiters:
            attribute["limiters"] = limiters
            
        # Add limiter counts if any
        if self.limiter_counts:
            attribute["limiter_counts"] = self.limiter_counts
        
        # Preserve the existing ID if editing an existing attribute
        if hasattr(self, 'existing_attribute_id') and self.existing_attribute_id:
            attribute["id"] = self.existing_attribute_id
            
        print(f"Attribute data: {attribute}")
        return attribute

    def _track_custom_name_edit(self):
        self._custom_name_edited = True
        
    def clear_custom_fields(self):
        """Clear all custom field widgets"""
        self.custom_input_widgets.clear()
        while self.custom_field_form.rowCount() > 0:
            self.custom_field_form.removeRow(0)
    
    def update_attribute_info(self):
        """Update attribute info based on the selected attribute"""
        attr_name = self.attr_dropdown.currentText()
        attr_data = self.attributes.get(attr_name, {})
        
        # Show/hide save to library button based on attribute type
        base_name = attr_data.get("base_name", attr_name)
        special_types = ["Item", "Companion", "Companions", "Minions", "Metamorphosis", "Alternate Form"]
        self.save_to_library_btn.setVisible(base_name in special_types)
        
        # Skip for the blank first item
        if not attr_name:
            return
            
        # If custom name hasn't been edited, update it to match the attribute
        if not self._custom_name_edited:
            self.custom_name_input.setText(attr_name)
            
        # Set the description
        description = attr_data.get("description", "No description available.")
        self.description.setPlainText(description)
        
        # Get the max level if specified
        max_level = attr_data.get("max_level", 10)
        self.level_spin.setMaximum(max_level)
        
        # Update cost per level
        self.attribute_cost_per_level = attr_data.get("cost_per_level", 1)
        
        # Clear and recreate custom fields
        self.clear_custom_fields()
        
        # Check for dynamic cost attributes (like Skill Group)
        self.dynamic_cost_map = attr_data.get("dynamic_cost_map", {})
        self.dynamic_cost_category_key = attr_data.get("dynamic_cost_category_key", None)
        
        # Add custom fields if any
        if "user_input_required" in attr_data and isinstance(attr_data["user_input_required"], list):
            for field in attr_data["user_input_required"]:
                self.add_custom_field_widget(field)
        elif "custom_fields" in attr_data and isinstance(attr_data["custom_fields"], list):
            for field in attr_data["custom_fields"]:
                self.add_custom_field_widget(field)
                
        # Show/hide the custom fields group
        has_custom_fields = ("custom_fields" in attr_data and len(attr_data["custom_fields"]) > 0) or \
                           ("user_input_required" in attr_data and len(attr_data["user_input_required"]) > 0)
        self.custom_field_group.setVisible(has_custom_fields)
        
        # Update the CP cost
        self.update_cp_cost()

    def show_power_pack_dialog(self):
        """Show dialog to select and apply a power pack"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Power Pack")
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Add description
        description = QLabel("Power Packs are pre-defined sets of enhancements and limiters that represent common power sources or themes.")
        description.setWordWrap(True)
        layout.addWidget(description)

        # Create combo box for power pack selection
        pack_combo = QComboBox()
        pack_combo.addItems([pack["name"] for pack in self.power_packs])
        layout.addWidget(pack_combo)

        # Add description text area
        pack_description = QTextEdit()
        pack_description.setReadOnly(True)
        pack_description.setFixedHeight(100)
        layout.addWidget(pack_description)

        # Update description when selection changes
        def update_description():
            selected_pack = self.power_packs[pack_combo.currentIndex()]
            pack_description.setText(selected_pack["description"])
        
        pack_combo.currentIndexChanged.connect(update_description)
        update_description()  # Initial update

        # Add buttons
        button_box = QHBoxLayout()
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(apply_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

        # Connect buttons
        def apply_with_show_all():
            self.apply_power_pack(self.power_packs[pack_combo.currentIndex()])
            dialog.accept()
            
        apply_button.clicked.connect(apply_with_show_all)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec_()

    def apply_power_pack(self, power_pack):
        """Apply the selected power pack's enhancements and limiters"""
        # Clear current selections
        self.enhancement_counts = {}
        self.limiter_counts = {}
        
        # Apply enhancements
        for enhancement in power_pack.get("enhancements", []):
            name = enhancement["name"]
            count = enhancement["count"]
            self.enhancement_counts[name] = count
        
        # Apply limiters
        for limiter in power_pack.get("limiters", []):
            name = limiter["name"]
            count = limiter["count"]
            self.limiter_counts[name] = count
        
        # Update the UI
        self.update_selected_enhancements_display()
        self.update_selected_limiters_display()
        self.update_cp_cost()
        
        # Show confirmation with details
        message = f"Applied {power_pack['name']} Power Pack:\n\n"
        
        if power_pack.get("enhancements"):
            message += "Enhancements:\n"
            for enhancement in power_pack.get("enhancements", []):
                message += f"- {enhancement['name']} (×{enhancement['count']})\n"
            message += "\n"
        
        if power_pack.get("limiters"):
            message += "Limiters:\n"
            for limiter in power_pack.get("limiters", []):
                message += f"- {limiter['name']} (×{limiter['count']})\n"
        
        QMessageBox.information(self, "Power Pack Applied", message)

    def save_to_library(self):
        """Save the current attribute to the library for reuse"""
        try:
            # Get attribute data to save
            attr_data = self.get_attribute_data()
            if not attr_data:
                return
                
            # Only specific types can be saved to library
            base_name = attr_data.get("base_name", "")
            library_type = None
            
            if base_name == "Item":
                library_type = "items"
            elif base_name in ["Companion", "Companions"]:
                library_type = "companions"
            elif base_name == "Minions":
                library_type = "minions"
            elif base_name == "Metamorphosis":
                library_type = "metamorphosis"
            elif base_name == "Alternate Form":
                library_type = "alternate_forms"
                
            if not library_type:
                QMessageBox.information(
                    self,
                    "Cannot Save",
                    f"Only special attribute types can be saved to the library."
                )
                return
                
            # Load the libraries data
            import os
            import json
            
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
            if not attr_data.get("name"):
                from PyQt5.QtWidgets import QInputDialog
                name, ok = QInputDialog.getText(
                    self,
                    "Save to Library",
                    "Enter a name for this item:"
                )
                if not ok or not name:
                    return
                attr_data["name"] = name
                
            # Ensure the data has an ID
            if "id" not in attr_data:
                attr_data["id"] = str(uuid.uuid4())
                
            # Check if this item already exists in the library
            existing_index = -1
            for i, obj in enumerate(libraries_data["libraries"][library_type]):
                if obj.get("id") == attr_data.get("id"):
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
                libraries_data["libraries"][library_type][existing_index] = attr_data
            else:
                # Add as a new item
                libraries_data["libraries"][library_type].append(attr_data)
                
            # Save the updated library data
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(libraries_data, f, indent=2)
                    
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully saved to the {library_type.rstrip('s')} library."
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save to library: {str(e)}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
