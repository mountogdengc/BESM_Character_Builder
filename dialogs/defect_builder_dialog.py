import os
import json

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QPushButton, QScrollArea, QWidget, QFormLayout,
    QGroupBox, QListWidget, QListWidgetItem, QCompleter
)
from PyQt5.QtCore import Qt, QStringListModel, QEvent, QTimer

class DefectBuilderDialog(QDialog):
    def __init__(self, parent=None, existing_defect=None):
        super().__init__(parent)
        
        # Store the existing defect data if provided
        self.existing_defect = existing_defect
        
        # Load defect, enhancement, limiter data
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Adjust base path

        with open(os.path.join(base_path, "data", "defects.json"), "r", encoding="utf-8") as f:  # Correct path to data folder
            raw_defects = json.load(f)["defects"]
            self.defects = {defect["name"]: defect for defect in raw_defects}

        with open(os.path.join(base_path, "data", "enhancements.json"), "r", encoding="utf-8") as f:
            self.raw_enhancements = json.load(f)["enhancements"]

        with open(os.path.join(base_path, "data", "limiters.json"), "r", encoding="utf-8") as f:
            self.raw_limiters = json.load(f)["limiters"]
        
        self.setWindowTitle("Defect Builder")
        self.setMinimumWidth(500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.custom_inputs = {}  # Dictionary to hold dynamically added fields
        self.custom_input_widgets = {}  # Keyed by field name to retrieve later

        form_layout = QFormLayout()

        self.autocomplete_links = {}  # maps controller -> dependent
        self.autocomplete_data = {}   # maps field_key -> autocomplete_by_category

        self.custom_field_group = QGroupBox("Custom Defect Fields")
        self.custom_field_form = QFormLayout()
        self.custom_field_group.setLayout(self.custom_field_form)
        self.custom_field_group.setVisible(False)  # Hidden unless fields are needed

        # Defect selection
        self.defect_dropdown = QComboBox()
        # Don't connect yet
        self.defect_dropdown.blockSignals(True)
        self.defect_dropdown.addItems(sorted(self.defects.keys()))
        self.defect_dropdown.blockSignals(False)

        # Delay connection until after caller has a chance to set defect
        QTimer.singleShot(0, lambda: self.defect_dropdown.currentTextChanged.connect(self.update_defect_info))
        
        form_layout.addRow("Defect:", self.defect_dropdown)

        # Editable name
        self.custom_name_input = QLineEdit()
        form_layout.addRow("Custom Name:", self.custom_name_input)
        
        # Rank for defects
        self.rank_spin = QSpinBox()
        self.rank_spin.setRange(1, 10)
        self.rank_spin.setValue(1)
        self.rank_spin.valueChanged.connect(self.update_cp_cost)
        form_layout.addRow("Rank:", self.rank_spin)

        # CP Cost (calculated)
        self.cp_cost_label = QLabel("0")
        form_layout.addRow("CP Cost:", self.cp_cost_label)

        self.cp_cost_label.setStyleSheet("font-weight: bold; color: darkblue;")

        # enhancement multi-select list
        self.enhancement_list = QListWidget()
        self.enhancement_list.setSelectionMode(QListWidget.MultiSelection)
        form_layout.addRow("enhancements:", self.enhancement_list)

        # Limiter multi-select list
        self.limiter_list = QListWidget()
        self.limiter_list.setSelectionMode(QListWidget.MultiSelection)
        form_layout.addRow("Limiters:", self.limiter_list)

        self.enhancement_list.itemSelectionChanged.connect(self.update_cp_cost)
        self.limiter_list.itemSelectionChanged.connect(self.update_cp_cost)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.custom_field_group)

        # Description
        self.description = QTextEdit()
        self.description.setReadOnly(True)
        self.description.setFixedHeight(80)
        self.layout.addWidget(QLabel("Description:"))
        self.layout.addWidget(self.description)

        # User description
        self.user_description = QTextEdit()
        self.user_description.setPlaceholderText("Enter your own notes about this defect here...")
        self.layout.addWidget(QLabel("Your Notes:"))
        self.layout.addWidget(self.user_description)
        
        # Store whether we're in edit mode for later use
        self.edit_mode = self.existing_defect is not None
        
        # If we have an existing defect, populate the fields
        if self.edit_mode:
            # Set the base defect type
            base_name = self.existing_defect.get("base_name", self.existing_defect.get("name", ""))
            if base_name in self.defects:
                self.defect_dropdown.setCurrentText(base_name)
            
            # Set the custom name
            custom_name = self.existing_defect.get("name", "")
            self.custom_name_input.setText(custom_name)
            
            # Set the rank
            self.existing_rank = self.existing_defect.get("rank", 1)
            self.rank_spin.setValue(self.existing_rank)
            
            # Set the user description
            notes = self.existing_defect.get("notes", "")
            self.user_description.setPlainText(notes)
            
            # We need to wait until after update_defect_info is called to set enhancements and limiters
            QTimer.singleShot(100, self.populate_existing_enhancements_and_limiters)

        # Initialize with first defect
        self._custom_name_edited = False
        self.custom_name_input.textEdited.connect(self._track_custom_name_edit)
        
        # Update defect info before adding buttons to ensure all fields are properly initialized
        self.update_defect_info()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Defect" if not self.existing_defect else "Update Defect")
        self.add_button.clicked.connect(self.finalize_and_accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(button_layout)

    def finalize_and_accept(self):
        # Validate any required fields
        # (Add validation logic here if needed)
        
        # If all is well, accept the dialog
        self.accept()

    def _track_custom_name_edit(self):
        self._custom_name_edited = True

    def set_defect_by_name(self, name):
        self.defect_dropdown.setCurrentText(name)

    def clear_custom_fields(self):
        # Clear any existing custom fields
        for i in reversed(range(self.custom_field_form.count())):
            self.custom_field_form.removeRow(i)

    def update_defect_info(self):
        defect_name = self.defect_dropdown.currentText()
        
        if not defect_name or defect_name not in self.defects:
            return
            
        defect = self.defects[defect_name]
        
        # Set the custom name to the defect name initially
        if not self._custom_name_edited:
            self.custom_name_input.setText(defect_name)
            self._custom_name_edited = False  # Reset so we can track new edits
            
        # Set the rank spinner range
        max_rank = defect.get("max_rank", 3)
        # Ensure max_rank is never None
        if max_rank is None:
            max_rank = 3
        self.rank_spin.setRange(1, max_rank)
        
        # Only set the default rank if we're not in edit mode
        # If we're in edit mode, we want to keep the rank that was set in the constructor
        if not self.edit_mode:
            self.rank_spin.setValue(defect.get("rank", 1))
        
        # Set the description
        self.description.setText(defect.get("description", "No description available."))
        
        # Clear and rebuild enhancements list
        self.enhancement_list.clear()
        for enhancement in self.raw_enhancements:
            if defect_name in enhancement.get("applicable_to", []) or "All" in enhancement.get("applicable_to", []):
                item = QListWidgetItem(enhancement["name"])
                item.setToolTip(enhancement.get("description", ""))
                self.enhancement_list.addItem(item)
        
        # Clear and rebuild limiters list
        self.limiter_list.clear()
        for limiter in self.raw_limiters:
            if defect_name in limiter.get("applicable_to", []) or "All" in limiter.get("applicable_to", []):
                item = QListWidgetItem(limiter["name"])
                item.setToolTip(limiter.get("description", ""))
                self.limiter_list.addItem(item)
        
        # Handle custom fields
        self.clear_custom_fields()
        self.custom_field_group.setVisible(False)
        
        custom_fields = defect.get("custom_fields", [])
        if custom_fields:
            self.custom_field_group.setVisible(True)
            for field in custom_fields:
                self.add_custom_field_widget(field)
                
        # Update the cost calculation
        self.update_cp_cost()

    def update_cp_cost(self):
        defect_name = self.defect_dropdown.currentText()
        
        if not defect_name or defect_name not in self.defects:
            self.cp_cost_label.setText("0")
            return
            
        defect = self.defects[defect_name]
        rank = self.rank_spin.value()
        
        # Base cost calculation - use cp_refund for defects
        cp_refund = defect.get("cp_refund", 0)
        rank_type = defect.get("rank_type", "")
        
        # Calculate cost based on rank and rank_type
        if rank_type == "Lesser":
            total_cost = rank * 1  # 1 CP per rank for Lesser defects
        elif rank_type == "Greater":
            total_cost = rank * 2  # 2 CP per rank for Greater defects
        elif rank_type == "Serious":
            total_cost = rank * 3  # 3 CP per rank for Serious defects
        elif rank_type == "Custom" and cp_refund is not None:
            total_cost = rank * cp_refund
        else:
            # Default fallback
            total_cost = rank * (cp_refund if cp_refund is not None else 1)
        
        # Apply enhancements (increase cost)
        enhancement_multiplier = 1.0
        for i in range(self.enhancement_list.count()):
            item = self.enhancement_list.item(i)
            if item.isSelected():
                enhancement_name = item.text()
                enhancement = next((e for e in self.raw_enhancements if e["name"] == enhancement_name), None)
                if enhancement:
                    enhancement_multiplier += enhancement.get("cost_multiplier", 0)
        
        total_cost = total_cost * enhancement_multiplier
        
        # Apply limiters (decrease cost)
        limiter_multiplier = 1.0
        for i in range(self.limiter_list.count()):
            item = self.limiter_list.item(i)
            if item.isSelected():
                limiter_name = item.text()
                limiter = next((l for l in self.raw_limiters if l["name"] == limiter_name), None)
                if limiter:
                    limiter_multiplier -= limiter.get("cost_reduction", 0)
        
        # Ensure limiter_multiplier doesn't go below minimum (usually 0.5)
        limiter_multiplier = max(limiter_multiplier, 0.5)
        
        total_cost = total_cost * limiter_multiplier
        
        # Round to nearest integer
        total_cost = round(total_cost)
        
        # For defects, cost is negative
        total_cost = -total_cost
        
        self.cp_cost_label.setText(str(total_cost))

    def get_defect_data(self):
        defect_name = self.defect_dropdown.currentText()
        custom_name = self.custom_name_input.text()
        rank = self.rank_spin.value()
        
        # Get the base defect data
        defect_data = self.defects.get(defect_name, {}).copy()
        
        # Collect selected enhancements
        enhancements = []
        for i in range(self.enhancement_list.count()):
            item = self.enhancement_list.item(i)
            if item.isSelected():
                enhancements.append(item.text())
        
        # Collect selected limiters
        limiters = []
        for i in range(self.limiter_list.count()):
            item = self.limiter_list.item(i)
            if item.isSelected():
                limiters.append(item.text())
        
        # Collect custom field values
        custom_field_values = {}
        for field_name, widget in self.custom_input_widgets.items():
            if isinstance(widget, QLineEdit):
                custom_field_values[field_name] = widget.text()
            elif isinstance(widget, QComboBox):
                custom_field_values[field_name] = widget.currentText()
            # Add more widget types as needed
        
        # Build the final defect data structure
        result = {
            "name": custom_name or defect_name,
            "base_name": defect_name,
            "rank": rank,
            "cost": int(self.cp_cost_label.text()),
            "enhancements": enhancements,
            "limiters": limiters,
            "custom_fields": custom_field_values,
            "notes": self.user_description.toPlainText()
        }
        
        return result

    def add_custom_field_widget(self, field):
        field_type = field.get("type", "text")
        field_key = field.get("key", "")
        label = field.get("label", field_key)
        default = field.get("default", "")
        options = field.get("options", [])
        
        widget = None
        
        if field_type == "text":
            widget = QLineEdit()
            widget.setText(default)
            
        elif field_type == "dropdown":
            widget = QComboBox()
            widget.addItems(options)
            if default and default in options:
                widget.setCurrentText(default)
                
        elif field_type == "editable_dropdown":
            widget = QComboBox()
            widget.setEditable(True)
            widget.addItems(options)
            
            # Add autocomplete
            completer = QCompleter(options)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            widget.setCompleter(completer)
            
            if default:
                widget.setCurrentText(default)
                
            # Install event filter for popup on click
            widget.lineEdit().installEventFilter(self)
            
        # Store the widget for later retrieval
        if widget and field_key:
            self.custom_input_widgets[field_key] = widget
            self.custom_field_form.addRow(label + ":", widget)

        if not self._custom_name_edited:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda _: self._set_dynamic_custom_name(self.defect_dropdown.currentText()))
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(lambda _: self._set_dynamic_custom_name(self.defect_dropdown.currentText()))

    def populate_existing_enhancements_and_limiters(self):
        """Populate enhancements and limiters from existing defect data"""
        if not self.existing_defect:
            return
            
        # Select enhancements
        enhancements = self.existing_defect.get("enhancements", [])
        for i in range(self.enhancement_list.count()):
            item = self.enhancement_list.item(i)
            if item.text() in enhancements:
                item.setSelected(True)
                
        # Select limiters
        limiters = self.existing_defect.get("limiters", [])
        for i in range(self.limiter_list.count()):
            item = self.limiter_list.item(i)
            if item.text() in limiters:
                item.setSelected(True)
                
        # Populate custom fields
        custom_fields = self.existing_defect.get("custom_fields", {})
        for field_name, value in custom_fields.items():
            if field_name in self.custom_input_widgets:
                widget = self.custom_input_widgets[field_name]
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            for widget in self.custom_input_widgets.values():
                if isinstance(widget, QComboBox) and widget.isEditable():
                    if widget.lineEdit() is source:
                        widget.showPopup()
        return super().eventFilter(source, event)
    
    def _set_dynamic_custom_name_wrapper(self, defect_name):
        print(f"[DYNAMIC NAME] Setting name for {defect_name}")
        return lambda _: self._set_dynamic_custom_name(defect_name)

    def _set_dynamic_custom_name(self, defect_name):
        # Fallback
        fallback_name = defect_name

        def get(key):
            w = self.custom_input_widgets.get(key)
            return w.currentText() if isinstance(w, QComboBox) else (w.text() if isinstance(w, QLineEdit) else "")

        # Add custom naming logic for specific defects here
        # For example:
        if defect_name == "Marked":
            mark_type = get("mark_type")
            if mark_type:
                self.custom_name_input.setText(f"Marked: {mark_type}")
                return

        elif defect_name == "Nemesis":
            enemy = get("enemy_name")
            if enemy:
                self.custom_name_input.setText(f"Nemesis: {enemy}")
                return

        # Default fallback
        self.custom_name_input.setText(fallback_name)

    def load_defect_data(self, defect_data):
        """Load existing defect data into the dialog"""
        if not defect_data:
            return
            
        # First determine the correct base defect name
        base_name = None
        if "key" in defect_data:
            # Find the defect name that matches this key
            for defect_name, defect_info in self.defects.items():
                if defect_info.get("key") == defect_data["key"]:
                    base_name = defect_name
                    break
        
        if not base_name:
            base_name = defect_data.get("base_name", defect_data.get("name", ""))
        
        # Set the base defect type if it exists in our defects list
        if base_name in self.defects:
            self.defect_dropdown.setCurrentText(base_name)
            self.update_defect_info()
        
        # Set the custom name
        custom_name = defect_data.get("name", "")
        self.custom_name_input.setText(custom_name)
        self._custom_name_edited = custom_name != base_name
        
        # Set the rank
        rank = defect_data.get("rank", 1)
        self.rank_spin.setValue(rank)
        
        # Set the user description/notes
        notes = defect_data.get("notes", "")
        self.user_description.setPlainText(notes)
        
        # Select enhancements
        enhancements = defect_data.get("enhancements", [])
        for i in range(self.enhancement_list.count()):
            item = self.enhancement_list.item(i)
            if item.text() in enhancements:
                item.setSelected(True)
                
        # Select limiters
        limiters = defect_data.get("limiters", [])
        for i in range(self.limiter_list.count()):
            item = self.limiter_list.item(i)
            if item.text() in limiters:
                item.setSelected(True)
                
        # Populate custom fields
        custom_fields = defect_data.get("custom_fields", {})
        for field_name, value in custom_fields.items():
            if field_name in self.custom_input_widgets:
                widget = self.custom_input_widgets[field_name]
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                elif isinstance(widget, QTextEdit):
                    widget.setPlainText(value)
