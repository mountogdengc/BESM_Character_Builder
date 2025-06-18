import json
import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QPushButton, QScrollArea, QWidget, QFormLayout,
    QGroupBox, QListWidget, QListWidgetItem, QCompleter
)
from PyQt5.QtCore import Qt, QStringListModel, QEvent, QTimer

class AttributeBuilderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load attribute, enhancement, limiter data
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Adjust base path

        with open(os.path.join(base_path, "data", "attributes.json"), "r", encoding="utf-8") as f:  # Correct path to data folder
            raw_attributes = json.load(f)["attributes"]
            self.attributes = {attr["name"]: attr for attr in raw_attributes}

        with open(os.path.join(base_path, "data", "enhancements.json"), "r", encoding="utf-8") as f:
            self.raw_enhancements = json.load(f)["enhancements"]

        with open(os.path.join(base_path, "data", "limiters.json"), "r", encoding="utf-8") as f:
            self.raw_limiters = json.load(f)["limiters"]
        
        self.setWindowTitle("Attribute Builder")
        self.setMinimumWidth(500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.custom_inputs = {}  # Dictionary to hold dynamically added fields
        self.custom_input_widgets = {}  # Keyed by field name to retrieve later

        form_layout = QFormLayout()

        self.autocomplete_links = {}  # maps controller -> dependent
        self.autocomplete_data = {}   # maps field_key -> autocomplete_by_category

        self.custom_field_group = QGroupBox("Custom Attribute Fields")
        self.custom_field_form = QFormLayout()
        self.custom_field_group.setLayout(self.custom_field_form)
        self.custom_field_group.setVisible(False)  # Hidden unless fields are needed

        # Attribute selection
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

        # level
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 10)
        self.level_spin.setValue(1)
        self.level_spin.valueChanged.connect(self.update_cp_cost)
        form_layout.addRow("level:", self.level_spin)

        # CP Cost (calculated)
        self.cp_cost_label = QLabel("0")
        form_layout.addRow("CP Cost:", self.cp_cost_label)

        self.cp_cost_label.setStyleSheet("font-weight: bold; color: darkblue;")

        # Enhancement multi-select list
        self.enhancement_list = QListWidget()
        self.enhancement_list.setSelectionMode(QListWidget.MultiSelection)
        form_layout.addRow("Enhancements:", self.enhancement_list)

        # Limiter multi-select list
        self.limiter_list = QListWidget()
        self.limiter_list.setSelectionMode(QListWidget.MultiSelection)
        form_layout.addRow("Limiters:", self.limiter_list)

        self.enhancement_list.itemSelectionChanged.connect(self.update_cp_cost)
        self.limiter_list.itemSelectionChanged.connect(self.update_cp_cost)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.custom_field_group)

        # description - match the attribute builder dialog's approach
        self.description = QTextEdit()
        self.description.setReadOnly(True)
        self.description.setFixedHeight(80)
        self.layout.addWidget(QLabel("Description:"))
        self.layout.addWidget(self.description)

        # User description
        self.user_description = QTextEdit()
        self.user_description.setPlaceholderText("Enter your own notes about this attribute here...")
        self.layout.addWidget(QLabel("Your Notes:"))
        self.layout.addWidget(self.user_description)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        self._custom_name_edited = False
        self.custom_name_input.textChanged.connect(self._track_custom_name_edit)

        self.dynamic_cost_map = {}  # Holds the current attribute's dynamic cost mapping
        self.dynamic_cost_category_key = None  # Key in custom fields (e.g., "category")

        # Initialize with first attribute's data
        self.update_attribute_info()

        self.ok_button.clicked.disconnect()
        self.ok_button.clicked.connect(self.finalize_and_accept)

    def finalize_and_accept(self):
        # 1) Force commit from editable QComboBox
        for key, widget in self.custom_input_widgets.items():
            if isinstance(widget, QComboBox) and widget.isEditable():
                widget.setCurrentText(widget.lineEdit().text())

        # 2) If user never manually edited name, auto‐generate it once more
        if not self._custom_name_edited:
            self._set_dynamic_custom_name(self.attr_dropdown.currentText())

        self.accept()
        
    def get_attribute_data(self):
        """Return the attribute data based on the dialog inputs"""
        attr_name = self.attr_dropdown.currentText()
        attr_data = self.attributes.get(attr_name, {})
        
        # Create a new attribute dictionary with the selected values
        attribute = {
            "name": self.custom_name_input.text(),
            "base_name": attr_name,  # Store the original attribute name
            "level": self.level_spin.value(),
            "cost": self.cp_cost_label.text().split()[0],  # Extract just the number
            "cost_per_level": attr_data.get("cost_per_level", 1),
            "user_description": self.user_description.toPlainText(),
            "description": self.description.toPlainText()
        }
        
        # Add custom fields if any
        if self.custom_input_widgets:
            custom_fields = {}
            for key, widget in self.custom_input_widgets.items():
                if isinstance(widget, QComboBox):
                    custom_fields[key] = widget.currentText()
                elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                    custom_fields[key] = widget.value()
                elif isinstance(widget, QLineEdit):
                    custom_fields[key] = widget.text()
                elif isinstance(widget, QTextEdit):
                    custom_fields[key] = widget.toPlainText()
            
            if custom_fields:
                attribute["custom_fields"] = custom_fields
        
        # Add selected enhancements if any
        if hasattr(self, 'enhancement_list') and self.enhancement_list.count() > 0:
            enhancements = []
            for i in range(self.enhancement_list.count()):
                item = self.enhancement_list.item(i)
                if item.isSelected():
                    enhancement_data = item.data(Qt.UserRole)
                    enhancements.append(enhancement_data["name"])
            
            if enhancements:
                attribute["enhancements"] = enhancements
                print(f"[DEBUG SUBMIT] Selected enhancements: {enhancements}")
        
        # Add selected limiters if any
        if hasattr(self, 'limiter_list') and self.limiter_list.count() > 0:
            limiters = []
            for i in range(self.limiter_list.count()):
                item = self.limiter_list.item(i)
                if item.isSelected():
                    limiter_data = item.data(Qt.UserRole)
                    limiters.append(limiter_data["name"])
            
            if limiters:
                attribute["limiters"] = limiters
                print(f"[DEBUG SUBMIT] Selected limiters: {limiters}")
        
        # Preserve the existing ID if editing an existing attribute
        if hasattr(self, 'existing_attribute_id') and self.existing_attribute_id:
            attribute["id"] = self.existing_attribute_id
            
        return attribute

    def _track_custom_name_edit(self):
        self._custom_name_edited = True

    def set_attribute_by_name(self, name):
        self.attr_dropdown.setCurrentText(name)
        self.update_attribute_info()

    def clear_custom_fields(self):
        self.custom_input_widgets.clear()
        while self.custom_field_form.rowCount() > 0:
            self.custom_field_form.removeRow(0)
            
    def create_custom_field(self, field):
        """Create a custom field widget based on field definition"""
        key = field.get("key")
        label = field.get("label", key)
        field_type = field.get("field_type", "text")
        desc = field.get("description", "")
        options = field.get("options", [])
        required = field.get("required", False)
        default = field.get("default", "")
        
        widget = None
        
        if field_type == "dropdown":
            widget = QComboBox()
            widget.addItems(options)
            widget.view().setMinimumHeight(100)  # Make dropdown list taller
            widget.currentTextChanged.connect(self.update_cp_cost)
            
            # Set default if specified
            if default and default in options:
                index = widget.findText(default)
                if index >= 0:
                    widget.setCurrentIndex(index)
        
        elif field_type == "number":
            widget = QSpinBox()
            widget.setRange(0, 100)  # Reasonable default range
            if "min" in field:
                widget.setMinimum(field["min"])
            if "max" in field:
                widget.setMaximum(field["max"])
            if default:
                try:
                    widget.setValue(int(default))
                except (ValueError, TypeError):
                    pass
            widget.valueChanged.connect(self.update_cp_cost)
            
        elif field_type == "combo_editable":
            widget = QComboBox()
            widget.setEditable(True)
            widget.addItems(options)
            widget.view().setMinimumHeight(100)
            widget.lineEdit().setPlaceholderText(desc)
            widget.currentTextChanged.connect(self.update_cp_cost)
            
            if "autocomplete_by_category" in field:
                self.autocomplete_links.setdefault("category_type", []).append(key)
                self.autocomplete_data[key] = field["autocomplete_by_category"]
                widget.lineEdit().installEventFilter(self)
                
            if default:
                widget.setCurrentText(default)
        
        elif field_type in ("text", "string"):
            widget = QLineEdit()
            widget.setPlaceholderText(desc)
            if default:
                widget.setText(default)
            widget.installEventFilter(self)
            
            if "autocomplete_by_category" in field:
                self.autocomplete_links.setdefault("category_type", []).append(key)
                self.autocomplete_data[key] = field["autocomplete_by_category"]
                widget.installEventFilter(self)
        
        elif field_type == "list":
            widget = QTextEdit()
            widget.setPlaceholderText(desc)
            widget.setFixedHeight(80)
            if default:
                widget.setPlainText(default)
            
            if "autocomplete_options" in field:
                tooltip = "Suggested: " + ", ".join(field["autocomplete_options"])
                widget.setToolTip(tooltip)
        
        # If a widget was created, add it to the form and tracking
        if widget:
            self.custom_input_widgets[key] = widget
            self.custom_field_form.addRow(label + ":", widget)
            
            # Add dynamic name update for certain fields
            if not self._custom_name_edited:
                if isinstance(widget, QLineEdit):
                    widget.textChanged.connect(lambda _: self._set_dynamic_custom_name(self.attr_dropdown.currentText()))
                elif isinstance(widget, QComboBox):
                    widget.currentTextChanged.connect(lambda _: self._set_dynamic_custom_name(self.attr_dropdown.currentText()))

    def update_attribute_info(self):
        self._custom_name_edited = False
        attr_name = self.attr_dropdown.currentText()
        attribute_data = self.attributes[attr_name]
        attr_key = attribute_data.get("key", "")

        # Initialize attribute_data property for storing the current state
        self.attribute_data = {
            "name": attr_name,
            "key": attr_key,
            "custom_fields": {}
        }

        print(f"[DEBUG] Attribute data for {attr_name}: {attribute_data}")

        # Reset name and description
        if not self._custom_name_edited:
            self._set_dynamic_custom_name(attr_name)
        
        print(f"[DEBUG] Processing attribute: {attr_name}, key: {attribute_data.get('key', 'unknown')}")
        
        # Set the description
        self.description.setText(attribute_data.get("description", "No description available."))
        print(f"[DEBUG] Setting description: '{self.description.toPlainText()[:50]}...'")
        
        # Make sure the QTextEdit is visible
        self.description.setVisible(True)

        # Clear previous custom fields
        self.clear_custom_fields()
        
        # Load dynamic cost info BEFORE building fields
        self.dynamic_cost_map = attribute_data.get("dynamic_cost", {})
        self.dynamic_cost_category_key = attribute_data.get("dynamic_cost_category", None)
        
        # Special handling for skill groups
        if attr_key == "skill_group":
            print(f"[DEBUG] Setting up skill group with dynamic cost map: {self.dynamic_cost_map}")
            # Make sure we have the right dynamic cost category key
            if not self.dynamic_cost_category_key:
                self.dynamic_cost_category_key = "category"
                print(f"[DEBUG] Setting dynamic_cost_category_key to 'category' for skill group")
        
        # Create custom fields based on attribute definition
        if "user_input_required" in attribute_data:
            self.custom_field_group.setVisible(True)
            for field in attribute_data["user_input_required"]:
                self.create_custom_field(field)
        else:
            self.custom_field_group.setVisible(False)
            
        # Populate enhancements and limiters lists
        # First, get the attribute key for compatibility checking
        attr_key = attribute_data.get("key", "").lower()
        
        # Enhancements
        self.enhancement_list.clear()
        
        # Debug counter for compatible enhancements
        enhancement_count = 0
        
        # Store compatible enhancements for later use
        self.compatible_enhancements = []
        
        for enhancement in self.raw_enhancements:
            # Handle both direct objects and nested arrays
            if isinstance(enhancement, list):
                # Skip nested arrays for now - we'll handle them separately
                continue
            
            # Get the compatible_with list or empty list if not present
            compatible_with = enhancement.get("compatible_with", [])
            
            # If compatible_with is None or empty, this enhancement is compatible with all attributes
            # Otherwise, check if our attribute key is in the compatible_with list
            is_compatible = (not compatible_with) or (attr_key and any(attr_key == key.lower() for key in compatible_with))
            
            if is_compatible:
                enhancement_count += 1
                self.compatible_enhancements.append(enhancement)
                item = QListWidgetItem(enhancement["name"])
                tooltip = enhancement.get("description", "") + "\n+1 CP"
                item.setToolTip(tooltip)
                item.setData(Qt.UserRole, enhancement)
                self.enhancement_list.addItem(item)
        
        print(f"DEBUG: Found {enhancement_count} compatible enhancements for {attr_name}")

        # Limiters
        self.limiter_list.clear()
        # We already have the attribute key from above
        
        # Debug counter for compatible limiters
        limiter_count = 0
        
        # Store compatible limiters for later use
        self.compatible_limiters = []
        
        for limiter in self.raw_limiters:
            # Handle both direct objects and nested arrays
            if isinstance(limiter, list):
                # Skip nested arrays for now
                continue
        
            # Get the compatible_with list or empty list if not present
            compatible_with = limiter.get("compatible_with", [])
            
            # If compatible_with is None or empty, this limiter is compatible with all attributes
            # Otherwise, check if our attribute key is in the compatible_with list
            is_compatible = (not compatible_with) or (attr_key and any(attr_key == key.lower() for key in compatible_with))
            
            if is_compatible:
                limiter_count += 1
                self.compatible_limiters.append(limiter)
                item = QListWidgetItem(limiter["name"])
                tooltip = limiter.get("description", "") + "\n−1 CP"
                item.setToolTip(tooltip)
                item.setData(Qt.UserRole, limiter)
                self.limiter_list.addItem(item)
        
        print(f"DEBUG: Found {limiter_count} compatible limiters for {attr_name}")

        # Trigger dependent category population
        if "category_type" in self.custom_input_widgets:
            current_type = self.custom_input_widgets["category_type"].currentText()
            self.on_category_type_changed(current_type)

        # If the dynamic field is a dropdown, hook it to cost updates
        if self.dynamic_cost_category_key:
            widget = self.custom_input_widgets.get(self.dynamic_cost_category_key)
            if isinstance(widget, QComboBox):
                try:
                    widget.currentTextChanged.disconnect()
                except Exception:
                    pass
                widget.currentTextChanged.connect(self.update_cp_cost)

        self.update_cp_cost()

        # Trigger custom name update for Skill Group after all fields are populated
        if attr_name == "Skill Group" and not self._custom_name_edited:
            self._update_skill_group_name()

        if not self._custom_name_edited and attr_name in {
            "Skill Group", "Enemy Attack", "Enemy Defence",
            "Melee Attack", "Melee Defence", "Ranged Attack",
            "Power Flux", "Dynamic Powers", "Metamorphosis"
        }:
            for key, widget in self.custom_input_widgets.items():
                try:
                    if isinstance(widget, QComboBox):
                        widget.currentTextChanged.disconnect()
                        widget.currentTextChanged.connect(lambda _: self._set_dynamic_custom_name(attr_name))
                    elif isinstance(widget, QLineEdit):
                        widget.textChanged.disconnect()
                        widget.textChanged.connect(lambda _: self._set_dynamic_custom_name(attr_name))
                except Exception:
                    # Skip if wasn't connected yet
                    pass

        self.update_cp_cost()

        # If name hasn't been custom edited, try to smart-name it again now
        if not self._custom_name_edited:
            self._set_dynamic_custom_name(attr_name)
            print("[DEBUG] Final name update triggered")

        # Debug output
        print("[DEBUG INIT] Loaded Attribute:", attr_name)
        print("[DEBUG INIT] Dynamic Cost Map:", self.dynamic_cost_map)
        print("[DEBUG INIT] Dynamic Key:", self.dynamic_cost_category_key)
        if self.dynamic_cost_category_key in self.custom_input_widgets:
            print("[DEBUG INIT] Found widget for key")
            print("[DEBUG INIT] Initial category value:", self.custom_input_widgets[self.dynamic_cost_category_key].currentText())

    def load_existing_enhancements_and_limiters(self, existing_attr):
        """Load existing enhancements and limiters for an attribute being edited"""
        try:
            # Load existing enhancements if any
            if "enhancements" in existing_attr and existing_attr["enhancements"]:
                print(f"Loading {len(existing_attr['enhancements'])} existing enhancements")
                
                # For each enhancement in the attribute, find and select it in the list
                for enhancement in existing_attr["enhancements"]:
                    # Handle both string and dictionary enhancements
                    if isinstance(enhancement, str):
                        enhancement_name = enhancement
                    else:
                        enhancement_name = enhancement.get("name")
                        
                    if not enhancement_name:
                        continue
                        
                    # Find the enhancement in the list
                    for i in range(self.enhancement_list.count()):
                        item = self.enhancement_list.item(i)
                        if item.text() == enhancement_name:
                            item.setSelected(True)
                            break
            
            # Load existing limiters if any
            if "limiters" in existing_attr and existing_attr["limiters"]:
                print(f"Loading {len(existing_attr['limiters'])} existing limiters")
                
                # For each limiter in the attribute, find and select it in the list
                for limiter in existing_attr["limiters"]:
                    # Handle both string and dictionary limiters
                    if isinstance(limiter, str):
                        limiter_name = limiter
                    else:
                        limiter_name = limiter.get("name")
                        
                    if not limiter_name:
                        continue
                        
                    # Find the limiter in the list
                    for i in range(self.limiter_list.count()):
                        item = self.limiter_list.item(i)
                        if item.text() == limiter_name:
                            item.setSelected(True)
                            break
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
            
        # Set custom field values from existing attribute if available
        if "custom_fields" in existing_attr and existing_attr["custom_fields"]:
            for key, value in existing_attr["custom_fields"].items():
                if key in self.custom_input_widgets:
                    widget = self.custom_input_widgets[key]
                    if isinstance(widget, QComboBox):
                        index = widget.findText(value)
                        if index >= 0:
                            widget.setCurrentIndex(index)
                        else:
                            # For editable combo boxes
                            if widget.isEditable():
                                widget.setCurrentText(value)
                    elif isinstance(widget, QSpinBox):
                        try:
                            widget.setValue(int(value))
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(widget, QLineEdit):
                        widget.setText(value)
                    elif isinstance(widget, QTextEdit):
                        widget.setPlainText(value)

        # For Skill Group, hook dropdowns to update custom name
        if attr_name == "Skill Group" and not self._custom_name_edited:
            cat_widget = self.custom_input_widgets.get("category")
            name_widget = self.custom_input_widgets.get("skill_group_name")

            if cat_widget:
                cat_widget.currentTextChanged.connect(self._update_skill_group_name)
            if name_widget:
                name_widget.currentTextChanged.connect(self._update_skill_group_name)

        self.custom_field_group.setVisible(bool(user_fields))

        # enhancements
        self.enhancement_list.clear()
        # Get the attribute key for compatibility checking
        attr_key = self.attributes[attr_name].get("key", "").lower()
        print(f"DEBUG: Current attribute: {attr_name}, key: {attr_key}")
        
        # Debug counter for compatible enhancements
        enhancement_count = 0
        
        # Store compatible enhancements for later use
        self.compatible_enhancements = []
        
        for enhancement in self.raw_enhancements:
            # Handle both direct objects and nested arrays
            if isinstance(enhancement, list):
                # Skip nested arrays for now - we'll handle them separately
                continue
            
            # Get the compatible_with list or empty list if not present
            compatible_with = enhancement.get("compatible_with", [])
            
            # If compatible_with is None or empty, this enhancement is compatible with all attributes
            # Otherwise, check if our attribute key is in the compatible_with list
            is_compatible = (not compatible_with) or (attr_key and any(attr_key == key.lower() for key in compatible_with))
            
            if is_compatible:
                enhancement_count += 1
                self.compatible_enhancements.append(enhancement)
                item = QListWidgetItem(enhancement["name"])
                tooltip = enhancement.get("description", "") + "\n+1 CP"
                item.setToolTip(tooltip)
                item.setData(Qt.UserRole, enhancement)
                self.enhancement_list.addItem(item)
        
        print(f"DEBUG: Found {enhancement_count} compatible enhancements for {attr_name}")

        # Limiters
        self.limiter_list.clear()
        # We already have the attribute key from above
        
        # Debug counter for compatible limiters
        limiter_count = 0
        
        # Store compatible limiters for later use
        self.compatible_limiters = []
        
        for limiter in self.raw_limiters:
            # Handle both direct objects and nested arrays
            if isinstance(limiter, list):
                # Skip nested arrays for now
                continue
            
            # Get the compatible_with list or empty list if not present
            compatible_with = limiter.get("compatible_with", [])
            
            # If compatible_with is None or empty, this limiter is compatible with all attributes
            # Otherwise, check if our attribute key is in the compatible_with list
            is_compatible = (not compatible_with) or (attr_key and any(attr_key == key.lower() for key in compatible_with))
            
            if is_compatible:
                limiter_count += 1
                self.compatible_limiters.append(limiter)
                item = QListWidgetItem(limiter["name"])
                tooltip = limiter.get("description", "") + "\n−1 CP"
                item.setToolTip(tooltip)
                item.setData(Qt.UserRole, limiter)
                self.limiter_list.addItem(item)
        
        print(f"DEBUG: Found {limiter_count} compatible limiters for {attr_name}")

        # Trigger dependent category population
        if "category_type" in self.custom_input_widgets:
            current_type = self.custom_input_widgets["category_type"].currentText()
            self.on_category_type_changed(current_type)

        # If the dynamic field is a dropdown, hook it to cost updates
        if self.dynamic_cost_category_key:
            widget = self.custom_input_widgets.get(self.dynamic_cost_category_key)
            if isinstance(widget, QComboBox):
                try:
                    widget.currentTextChanged.disconnect()
                except Exception:
                    pass
                widget.currentTextChanged.connect(self.update_cp_cost)

        self.update_cp_cost()

        # Trigger custom name update for Skill Group after all fields are populated
        if attr_name == "Skill Group" and not self._custom_name_edited:
            self._update_skill_group_name()

        if not self._custom_name_edited and attr_name in {
            "Skill Group", "Enemy Attack", "Enemy Defence",
            "Melee Attack", "Melee Defence", "Ranged Attack",
            "Power Flux", "Dynamic Powers", "Metamorphosis"
        }:
            for key, widget in self.custom_input_widgets.items():
                try:
                    if isinstance(widget, QComboBox):
                        widget.currentTextChanged.disconnect()
                        widget.currentTextChanged.connect(lambda _: self._set_dynamic_custom_name(attr_name))
                    elif isinstance(widget, QLineEdit):
                        widget.textChanged.disconnect()
                        widget.textChanged.connect(lambda _: self._set_dynamic_custom_name(attr_name))
                except Exception:
                    # Skip if wasn't connected yet
                    pass

        self.update_cp_cost()

        # If name hasn't been custom edited, try to smart-name it again now
        if not self._custom_name_edited:
            self._set_dynamic_custom_name(attr_name)
            print("[DEBUG] Final name update triggered")

        # Debug output
        print("[DEBUG INIT] Loaded Attribute:", attr_name)
        print("[DEBUG INIT] Dynamic Cost Map:", self.dynamic_cost_map)
        print("[DEBUG INIT] Dynamic Key:", self.dynamic_cost_category_key)
        if self.dynamic_cost_category_key in self.custom_input_widgets:
            print("[DEBUG INIT] Found widget for key")
            print("[DEBUG INIT] Initial category value:", self.custom_input_widgets[self.dynamic_cost_category_key].currentText())

    def on_category_type_changed(self, selected_type):
        controller_key = "category_type"
        for dependent_key in self.autocomplete_links.get("category_type", []):
            options = self.autocomplete_data.get(dependent_key, {}).get(selected_type, [])
            widget = self.custom_input_widgets.get(dependent_key)

            if isinstance(widget, QComboBox):
                widget.clear()
                widget.addItems(options)
                widget.setCurrentIndex(-1)

    def update_cp_cost(self):
        name = self.attr_dropdown.currentText()
        attribute = self.attributes[name]
        level = self.level_spin.value()
        attr_key = attribute.get("key", "")

        # Initialize category and cost
        category = None
        cost_per_level = attribute.get("cost_per_level", 0)

        # Dynamic cost support
        if self.dynamic_cost_map and self.dynamic_cost_category_key:
            widget = self.custom_input_widgets.get(self.dynamic_cost_category_key)
            if isinstance(widget, QComboBox):
                category = widget.currentText()
                if category in self.dynamic_cost_map:
                    cost_per_level = self.dynamic_cost_map.get(category, cost_per_level)
                    print(f"[DEBUG] Dynamic cost for {category}: {cost_per_level}")

        # enhancements / Limiters
        enhancement_count = len(self.enhancement_list.selectedItems())
        limiter_count = len(self.limiter_list.selectedItems())

        # Calculate total CP using the cost per level
        total_cp = cost_per_level * level
        effective_level = max(1, level - enhancement_count + limiter_count)

        # Update CP Cost label
        self.cp_cost_label.setText(f"{total_cp} CP")
        self.cp_cost_label.setToolTip(f"Effective Level: {effective_level}")

        # Debug logging to verify calculations
        print(f"[DEBUG] Attribute: {name} ({attr_key}), Level: {level}, Cost Per Level: {cost_per_level}, Total CP: {total_cp}, Effective Level: {effective_level}")
        
        # For skill groups, update the skill_group_type in custom_fields
        if attr_key == "skill_group" and category:
            # Make sure the cost is correctly reflected in the UI immediately
            print(f"[DEBUG] Skill Group: Setting cost for {category} to {cost_per_level} per level")

    def on_controller_field_changed(self, controller_key, selected_value):
        if controller_key not in self.autocomplete_links:
            return

        for dependent_key in self.autocomplete_links[controller_key]:
            data = self.autocomplete_data.get(dependent_key)
            if not data or data["controller"] != controller_key:
                continue

            options = data["options_map"].get(selected_value, [])
            widget = self.custom_fields_widgets.get(dependent_key)
            if isinstance(widget, QLineEdit):
                completer = QCompleter(options)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setFilterMode(Qt.MatchContains)
                widget.setCompleter(completer)

    def get_attribute_data(self):
        # Make sure name reflects the latest field values
        if not self._custom_name_edited:
            self._set_dynamic_custom_name(self.attr_dropdown.currentText())
        
        custom_fields = {}
        for key, widget in self.custom_input_widgets.items():
            if isinstance(widget, QLineEdit):
                custom_fields[key] = widget.text()
            elif isinstance(widget, QComboBox):
                custom_fields[key] = widget.currentText()
            # You can add more types here in the future if needed

        enhancements = [item.text() for item in self.enhancement_list.selectedItems()]
        limiters = [item.text() for item in self.limiter_list.selectedItems()]

        name = self.attr_dropdown.currentText()
        attr_key = self.attributes[name].get("key", "")
        
        attribute = self.attributes[name]
        base_cost = attribute.get("cost_per_level", attribute.get("base_cost", 0))

        # Handle dynamic cost
        cost_per_level = base_cost
        if self.dynamic_cost_map and self.dynamic_cost_category_key:
            widget = self.custom_input_widgets.get(self.dynamic_cost_category_key)
            if isinstance(widget, QComboBox):
                category = widget.currentText()
                if category in self.dynamic_cost_map:
                    cost_per_level = self.dynamic_cost_map[category]
                    
                    # For skill groups, make sure we store the category properly
                    if attr_key == "skill_group":
                        custom_fields["skill_group_type"] = category

        level = self.level_spin.value()
        enhancement_count = len(enhancements)
        limiter_count = len(limiters)
        
        total_cp = cost_per_level * level
        effective_level = max(1, level - enhancement_count + limiter_count)

        # Force dynamic name update if user hasn't manually edited it
        from PyQt5.QtWidgets import QApplication  # (already imported at top)

        # Make sure all text/selection changes are processed
        QApplication.processEvents()

        if not self._custom_name_edited:
            self._set_dynamic_custom_name(self.attr_dropdown.currentText())

        print("[DEBUG SUBMIT] Final Name:", self.custom_name_input.text())
        print("[DEBUG SUBMIT] Custom Fields:", custom_fields)
        
        # Create the attribute data
        attr_data = {
            "name": self.custom_name_input.text(),
            "base_name": name,
            "key": attr_key,
            "level": level,
            "cost": total_cp,
            "cost_per_level": cost_per_level,
            "effective_level": effective_level,
            "enhancements": enhancements,
            "limiters": limiters,
            "description": self.description.toPlainText(),
            "user_description": self.user_description.toPlainText(),
            "custom_fields": custom_fields
        }
        
        # For skill groups, add the dynamic cost category key
        if attr_key == "skill_group":
            attr_data["dynamic_cost_category_key"] = "skill_group_type"
            
        return attr_data

    def add_custom_field_widget(self, field):
        label = field.get("label", "Unnamed")
        key = field.get("key") or field.get("field_name")
        field_type = field.get("field_type", "text")
        options = field.get("options", [])
        desc = field.get("description", "")

        # Prevent duplicate keys
        if not key or key in self.custom_input_widgets:
            return

        # Track dynamic cost category key if relevant
        if self.dynamic_cost_map and self.dynamic_cost_category_key is None:
            self.dynamic_cost_category_key = field.get("key")

        widget = None

        if field_type in ("dropdown", "select"):
            widget = QComboBox()
            widget.addItems(options)
            if widget.count() > 0:
                widget.setCurrentIndex(0)
            widget.currentTextChanged.connect(self.update_cp_cost)
            widget.installEventFilter(self)

        elif field_type == "combo_editable":
            widget = QComboBox()
            widget.setEditable(True)
            widget.addItems(options)
            widget.view().setMinimumHeight(100)
            widget.lineEdit().setPlaceholderText(desc)
            widget.currentTextChanged.connect(self.update_cp_cost)

            if "autocomplete_by_category" in field:
                self.autocomplete_links.setdefault("category_type", []).append(key)
                self.autocomplete_data[key] = field["autocomplete_by_category"]
                widget.lineEdit().installEventFilter(self)

        elif field_type in ("text", "string"):
            widget = QLineEdit()
            widget.setPlaceholderText(desc)
            widget.installEventFilter(self)

            if "autocomplete_by_category" in field:
                self.autocomplete_links.setdefault("category_type", []).append(key)
                self.autocomplete_data[key] = field["autocomplete_by_category"]
                widget.installEventFilter(self)

        elif field_type == "list":
            widget = QTextEdit()
            widget.setPlaceholderText(desc)
            widget.setFixedHeight(80)

            if "autocomplete_options" in field:
                tooltip = "Suggested: " + ", ".join(field["autocomplete_options"])
                widget.setToolTip(tooltip)

        # If a widget was created, add it to the form and tracking
        if widget:
            self.custom_input_widgets[key] = widget
            self.custom_field_form.addRow(label + ":", widget)

        if not self._custom_name_edited:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda _: self._set_dynamic_custom_name(self.attr_dropdown.currentText()))
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda _: self._set_dynamic_custom_name(self.attr_dropdown.currentText()))

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            for widget in self.custom_input_widgets.values():
                if isinstance(widget, QComboBox) and widget.isEditable():
                    if widget.lineEdit() is source:
                        widget.showPopup()
        return super().eventFilter(source, event)
    
    def _set_dynamic_custom_name_wrapper(self, attr_name):
        print(f"[DYNAMIC NAME] Setting name for {attr_name}")
        return lambda _: self._set_dynamic_custom_name(attr_name)

    def _update_skill_group_name(self):
        if not hasattr(self, '_custom_name_edited') or self._custom_name_edited:
            return  # don't overwrite user input

        cat_widget = self.custom_input_widgets.get("category")
        name_widget = self.custom_input_widgets.get("skill_group_name")

        if cat_widget and name_widget:
            try:
                category = cat_widget.currentText()
                group_name = name_widget.currentText()
                if category and group_name:
                    # Update the custom name
                    self.custom_name_input.setText(f"Skill Group: {group_name} ({category})")
                    
                    # Set the skill_group_type to match the category for cost calculation
                    # This is the key fix for the crash - we need to ensure the skill_group_type
                    # matches the category for proper cost calculation
                    if "skill_group_type" not in self.custom_input_widgets:
                        print("[DEBUG] Creating skill_group_type field")
                        # We need to create this field in the custom fields
                        if not hasattr(self, 'attribute_data'):
                            self.attribute_data = {}
                        if "custom_fields" not in self.attribute_data:
                            self.attribute_data["custom_fields"] = {}
                        self.attribute_data["custom_fields"]["skill_group_type"] = category
                    
                    # Update the cost calculation
                    self.update_cp_cost()
            except Exception as e:
                print(f"Error in _update_skill_group_name: {str(e)}")

    def _set_dynamic_custom_name(self, attr_name):
        # Fallback
        fallback_name = attr_name

        def get(key):
            w = self.custom_input_widgets.get(key)
            return w.currentText() if isinstance(w, QComboBox) else (w.text() if isinstance(w, QLineEdit) else "")

        if attr_name == "Skill Group":
            category = get("category")
            group_name = get("skill_group_name")
            if category and group_name:
                name = f"Skill Group: {group_name} ({category})"
                self.custom_name_input.setText(name)
                return

        elif attr_name == "Enemy Attack":
            enemy = get("enemy_type")
            if enemy:
                self.custom_name_input.setText(f"Enemy Attack vs. {enemy}")
                return

        elif attr_name == "Enemy Defence":
            enemy = get("enemy_type")
            if enemy:
                self.custom_name_input.setText(f"Enemy Defence vs. {enemy}")
                return

        elif attr_name == "Melee Attack":
            weapon = get("weapon_class")
            if weapon:
                self.custom_name_input.setText(f"Melee Attack [{weapon}]")
                return

        elif attr_name == "Melee Defence":
            weapon = get("weapon_class")
            if weapon:
                self.custom_name_input.setText(f"Melee Defence [{weapon}]")
                return

        elif attr_name == "Ranged Attack":
            weapon = get("weapon_class")
            if weapon:
                self.custom_name_input.setText(f"Ranged Attack [{weapon}]")
                return

        elif attr_name == "Power Flux":
            category = get("flux_category")
            if category:
                self.custom_name_input.setText(f"Power Flux: {category}")
                return

        elif attr_name == "Dynamic Powers":
            category_type = get("category_type")
            controlled = get("controlled_category")
            if category_type and controlled:
                self.custom_name_input.setText(f"Dynamic Powers: {controlled} ({category_type})")
                return

        elif attr_name == "Metamorphosis":
            name = get("template_name")
            cp = get("template_cp_value")
            if name and cp:
                self.custom_name_input.setText(f"Metamorphosis: {name} ({cp} CP)")
                return

        # Default fallback
        self.custom_name_input.setText(fallback_name)