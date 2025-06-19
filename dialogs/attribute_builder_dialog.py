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
        
    def load_existing_attribute(self, existing_attr):
        """Load data from an existing attribute"""
        try:
            # Set base attribute name
            base_name = existing_attr.get("base_name", existing_attr.get("name", ""))
            if base_name in self.attributes:
                self.attr_dropdown.setCurrentText(base_name)
                
            # Set custom name if different
            custom_name = existing_attr.get("name", "")
            if custom_name != base_name:
                self.custom_name_input.setText(custom_name)
                self._custom_name_edited = True
                
            # Set level
            level = existing_attr.get("level", 1)
            self.level_spin.setValue(level)
            
            # Set user description if any
            user_desc = existing_attr.get("user_description", "")
            self.user_description.setPlainText(user_desc)
            
            # Load existing enhancements and limiters if any
            if "enhancements" in existing_attr and existing_attr["enhancements"]:
                for enhancement in existing_attr["enhancements"]:
                    # Handle both string and dictionary enhancements
                    if isinstance(enhancement, str):
                        enhancement_name = enhancement
                        self.enhancement_counts[enhancement_name] = 1
                    else:
                        enhancement_name = enhancement.get("name")
                        count = enhancement.get("count", 1)
                        self.enhancement_counts[enhancement_name] = count
            
            # Load existing limiters if any
            if "limiters" in existing_attr and existing_attr["limiters"]:
                for limiter in existing_attr["limiters"]:
                    # Handle both string and dictionary limiters
                    if isinstance(limiter, str):
                        limiter_name = limiter
                        self.limiter_counts[limiter_name] = 1
                    else:
                        limiter_name = limiter.get("name")
                        count = limiter.get("count", 1)
                        self.limiter_counts[limiter_name] = count
        except Exception as e:
            print(f"Error loading enhancements and limiters: {e}")

        # Load dynamic cost info BEFORE building fields if available in existing_attr
        self.dynamic_cost_map = existing_attr.get("dynamic_cost", {})
        self.dynamic_cost_category_key = None  # will be set in add_custom_field_widget
        
        # Get the base attribute data for the current attribute
        attr_name = existing_attr.get("base_name", self.attr_dropdown.currentText())
        attr_data = self.attributes.get(attr_name, {})
        
        # Load custom fields from attribute definition
        user_fields = attr_data.get("user_input_required", [])
        for field in user_fields:
            self.add_custom_field_widget(field)
            
        # Load values for custom fields
        custom_fields = existing_attr.get("custom_fields", {})
        for field_name, value in custom_fields.items():
            if field_name in self.custom_input_widgets:
                widget = self.custom_input_widgets[field_name]
                if isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                # Add support for other widget types as needed
                
        # Update the enhanced/limiter displays
        self.update_selected_enhancements_display()
        self.update_selected_limiters_display()
                
        # Update CP cost
        self.update_cp_cost()

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
        
        # Handle dynamic cost map for Skill Group and other attributes with variable costs
        if "dynamic_cost" in attr_data:
            self.dynamic_cost_map = attr_data["dynamic_cost"]
            
            # For Skill Group, the category determines the cost
            if attr_name == "Skill Group":
                self.dynamic_cost_category_key = "category"
            else:
                # Other attributes might use different keys
                self.dynamic_cost_category_key = ""
        else:
            self.dynamic_cost_map = {}
            self.dynamic_cost_category_key = ""
        
        # Clear and recreate custom fields
        self.clear_custom_fields()
        
        # Reset custom field trackers
        self.custom_input_widgets = {}
        
        # Add custom fields if any
        user_input_fields = attr_data.get("user_input_required", [])
        if user_input_fields and len(user_input_fields) > 0:
            for field in user_input_fields:
                self.add_custom_field_widget(field)
                
            # Show the custom fields group
            self.custom_field_group.setVisible(True)
            
            # For Skill Group, connect signals to update the name
            if attr_name == "Skill Group":
                print("Setting up Skill Group signal connections")
                try:
                    cat_widget = self.custom_input_widgets.get("category")
                    name_widget = self.custom_input_widgets.get("skill_group_name")
                    
                    if cat_widget and hasattr(cat_widget, 'currentTextChanged'):
                        cat_widget.currentTextChanged.connect(self._update_skill_group_name)
                        
                    if name_widget and hasattr(name_widget, 'currentTextChanged'):
                        name_widget.currentTextChanged.connect(self._update_skill_group_name)
                        
                    # Trigger an initial update of the name
                    QTimer.singleShot(100, self._update_skill_group_name)
                except Exception as e:
                    print(f"Error connecting skill group signals: {str(e)}")
        else:
            # Hide the custom fields group if no fields
            self.custom_field_group.setVisible(False)
        
        # Update the CP cost
        self.update_cp_cost()

    def clear_custom_fields(self):
        self.custom_input_widgets.clear()
        while self.custom_field_form.rowCount() > 0:
            self.custom_field_form.removeRow(0)

    def add_custom_field_widget(self, field):
        """Add a widget for a custom field"""
        field_name = field.get("name", "")
        field_key = field.get("key", field_name)  # Use key if available, otherwise name
        field_type = field.get("type", field.get("field_type", "text"))  # Check both type and field_type
        field_label = field.get("label", field_name)
        field_options = field.get("options", [])
        
        print(f"Creating field: {field_key}, type: {field_type}, label: {field_label}")
        
        # Create appropriate widget based on field type
        if field_type in ["select", "dropdown"]:
            # Create dropdown for select/dropdown fields
            widget = QComboBox()
            widget.addItems(field_options)
            print(f"Added dropdown with options: {field_options}")
        elif field_type == "combo_editable":
            # Create editable combo box
            widget = QComboBox()
            widget.setEditable(True)
            widget.addItems(field_options)
        elif field_type == "list":
            # Create multiline text edit for list input
            widget = QTextEdit()
            widget.setMaximumHeight(100)
        else:
            # Default to text input
            widget = QLineEdit()
            if "placeholder" in field:
                widget.setPlaceholderText(field.get("placeholder"))
        
        # Store reference to widget using the key
        self.custom_input_widgets[field_key] = widget
        
        # Add to form layout
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

        # Calculate base cost
        base_cost = self.level_spin.value() * cost_per_level
        
        # Add costs for enhancements
        enhancement_multiplier = 1.0
        for name, count in self.enhancement_counts.items():
            enhancement = next((e for e in self.raw_enhancements if e["name"] == name), None)
            if enhancement:
                # Each enhancement typically adds 0.5x per assignment
                enhancement_multiplier += count * 0.5
        
        total_cost = base_cost * enhancement_multiplier
        
        # Apply limiters (reduce cost)
        limiter_multiplier = 1.0
        for name, count in self.limiter_counts.items():
            limiter = next((l for l in self.raw_limiters if l["name"] == name), None)
            if limiter:
                # Each limiter typically reduces by 0.1x per assignment
                limiter_multiplier -= count * 0.1
        
        # Ensure limiter multiplier doesn't go below minimum (usually 0.5)
        limiter_multiplier = max(limiter_multiplier, 0.5)
        
        total_cost = total_cost * limiter_multiplier
        
        # Apply any custom field-based cost modifications
        if hasattr(self, 'dynamic_cost_map') and self.dynamic_cost_map:
            try:
                # Check if we have a dynamic cost category
                if self.dynamic_cost_category_key and self.dynamic_cost_category_key in self.custom_input_widgets:
                    category_widget = self.custom_input_widgets[self.dynamic_cost_category_key]
                    if isinstance(category_widget, QComboBox):
                        selected_category = category_widget.currentText()
                        category_multiplier = self.dynamic_cost_map.get(selected_category, 1.0)
                        total_cost *= category_multiplier
            except Exception as e:
                print(f"Error applying dynamic cost: {e}")
                
        # Round to nearest integer
        total_cost = round(total_cost)
        
        # Update UI
        self.cp_cost_label.setText(str(total_cost))

    def get_attribute_data(self):
        """Return the attribute data based on the dialog inputs"""
        # Get base attribute name and custom name
        base_name = self.attr_dropdown.currentText()
        name = self.custom_name_input.text() or base_name
        
        # Build attribute data structure
        attribute = {
            "name": name,
            "base_name": base_name,
            "level": self.level_spin.value(),
            "cost": int(self.cp_cost_label.text()),
            "user_description": self.user_description.toPlainText()
        }
        
        # Get custom field values
        custom_fields = {}
        for field_name, widget in self.custom_input_widgets.items():
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
            else:
                value = ""
            
            custom_fields[field_name] = value
            
        # Add custom fields if any
        if custom_fields:
            attribute["custom_fields"] = custom_fields
            
        # Add description from base attribute
        base_attr = self.attributes.get(base_name, {})
        if "description" in base_attr:
            attribute["description"] = base_attr["description"]
            
        # Get the official attribute key if available
        if "key" in base_attr:
            attribute["key"] = base_attr["key"]
            
        # Add selected enhancements if any
        enhancements = self.get_selected_enhancements()
        if enhancements:
            attribute["enhancements"] = enhancements
            
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
            
        return attribute

    def _track_custom_name_edit(self):
        self._custom_name_edited = True
        
    def _update_skill_group_name(self):
        """Update the custom name field based on the selections in the skill group dropdowns.
        Also sets the skill_group_type in custom fields for cost calculation."""
        try:
            # Skip if custom name has been manually edited
            if hasattr(self, '_custom_name_edited') and self._custom_name_edited:
                return  # don't overwrite user input
            
            # Get references to the category and name widgets
            cat_widget = self.custom_input_widgets.get("category")
            name_widget = self.custom_input_widgets.get("skill_group_name")
            
            # If the widgets don't exist, create them with default values
            # This is a fallback to prevent crashes
            if not cat_widget:
                print("Warning: category widget not found, creating one")
                cat_widget = QComboBox()
                cat_widget.addItems(["Background", "Field", "Action"])
                self.custom_input_widgets["category"] = cat_widget
                
            if not name_widget:
                print("Warning: skill_group_name widget not found, creating one")
                name_widget = QComboBox()
                name_widget.addItems([
                    "Academic", "Artistic", "Domestic", "Occupation", 
                    "Business", "Social", "Street", "Technical", 
                    "Adventuring", "Detective", "Military", "Scientific"
                ])
                self.custom_input_widgets["skill_group_name"] = name_widget
            
            # Get the selected values (with fallbacks)
            category = cat_widget.currentText() if hasattr(cat_widget, 'currentText') else ""
            group_name = name_widget.currentText() if hasattr(name_widget, 'currentText') else ""
            
            # Debug output
            print(f"Skill Group Update: Category={category}, Name={group_name}")
            
            # Check that we have valid selections before updating the name
            if category and group_name:
                # Update the custom name field
                self.custom_name_input.setText(f"Skill Group: {group_name} ({category})")
                
                # Store the category as skill_group_type for cost calculation
                if "custom_fields" not in self.__dict__:
                    self.custom_fields = {}
                self.custom_fields["skill_group_type"] = category
                
                # Update the cost based on the category
                try:
                    self.update_cp_cost()
                except Exception as cost_error:
                    print(f"Error updating cost: {str(cost_error)}")
        except Exception as e:
            # Provide detailed error information without crashing
            print(f"Error in _update_skill_group_name: {str(e)}")
            import traceback
            traceback.print_exc()

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
