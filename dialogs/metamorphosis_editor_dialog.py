import uuid
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSpinBox, QTextEdit, QTabWidget, QWidget,
    QScrollArea, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from tools.utils import create_card_widget
from dialogs.attribute_builder_dialog import AttributeBuilderDialog
from dialogs.defect_builder_dialog import DefectBuilderDialog

class MetamorphosisEditorDialog(QDialog):
    def __init__(self, parent, metamorphosis_data=None):
        super().__init__(parent)
        self.parent = parent
        
        # Initialize with default or provided data
        self.metamorphosis_data = metamorphosis_data or {
            "id": str(uuid.uuid4()),
            "name": "New Metamorphosis Form",
            "level": 1,
            "description": "Transforms into a new form",
            "cp": 5,  # Default CP budget (level * 5)
            "attributes": [],
            "defects": []
        }
        
        # Store the original level for CP budget calculations
        self.original_level = self.metamorphosis_data.get("level", 1)
        
        # Track total CP usage
        self.total_cp_used = 0
        
        # Setup UI
        self.setup_ui()
        self.update_cp_display()
        
    def setup_ui(self):
        self.setWindowTitle("Edit Metamorphosis Form")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        main_layout = QVBoxLayout(self)
        
        # Basic info section
        info_layout = QVBoxLayout()
        
        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit(self.metamorphosis_data.get("name", ""))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        info_layout.addLayout(name_layout)
        
        # Level display (read-only)
        level_layout = QHBoxLayout()
        level_label = QLabel("Level:")
        self.level_display = QLabel(str(self.metamorphosis_data.get("level", 1)))
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_display)
        level_layout.addStretch()
        info_layout.addLayout(level_layout)
        
        # CP Budget display
        cp_layout = QHBoxLayout()
        cp_label = QLabel("CP Budget:")
        self.cp_budget_display = QLabel(f"{self.metamorphosis_data.get('cp', 5)} CP")
        cp_layout.addWidget(cp_label)
        cp_layout.addWidget(self.cp_budget_display)
        
        # CP Used display
        cp_used_label = QLabel("CP Used:")
        self.cp_used_display = QLabel("0 CP")
        cp_layout.addWidget(cp_used_label)
        cp_layout.addWidget(self.cp_used_display)
        cp_layout.addStretch()
        info_layout.addLayout(cp_layout)
        
        # Description field
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Description:")
        self.desc_input = QTextEdit(self.metamorphosis_data.get("description", ""))
        self.desc_input.setMaximumHeight(80)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        info_layout.addLayout(desc_layout)
        
        main_layout.addLayout(info_layout)
        
        # Tab widget for attributes and defects
        self.tabs = QTabWidget()
        
        # Attributes tab
        self.attributes_tab = QWidget()
        attributes_layout = QVBoxLayout(self.attributes_tab)
        
        # Attributes scroll area
        self.attributes_scroll = QScrollArea()
        self.attributes_scroll.setWidgetResizable(True)
        self.attributes_container = QWidget()
        self.attributes_layout = QVBoxLayout(self.attributes_container)
        self.attributes_layout.setAlignment(Qt.AlignTop)
        self.attributes_scroll.setWidget(self.attributes_container)
        attributes_layout.addWidget(self.attributes_scroll)
        
        # Add attribute button
        add_attr_button = QPushButton("Add Attribute")
        add_attr_button.clicked.connect(self.add_attribute)
        attributes_layout.addWidget(add_attr_button)
        
        self.tabs.addTab(self.attributes_tab, "Attributes")
        
        # Defects tab
        self.defects_tab = QWidget()
        defects_layout = QVBoxLayout(self.defects_tab)
        
        # Defects scroll area
        self.defects_scroll = QScrollArea()
        self.defects_scroll.setWidgetResizable(True)
        self.defects_container = QWidget()
        self.defects_layout = QVBoxLayout(self.defects_container)
        self.defects_layout.setAlignment(Qt.AlignTop)
        self.defects_scroll.setWidget(self.defects_container)
        defects_layout.addWidget(self.defects_scroll)
        
        # Add defect button
        add_defect_button = QPushButton("Add Defect")
        add_defect_button.clicked.connect(self.add_defect)
        defects_layout.addWidget(add_defect_button)
        
        self.tabs.addTab(self.defects_tab, "Defects")
        
        main_layout.addWidget(self.tabs)
        
        # Buttons
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
        main_layout.addLayout(btn_layout)
        
        # Populate existing attributes and defects
        self.populate_attributes()
        self.populate_defects()
    
    def populate_attributes(self):
        for attr in self.metamorphosis_data.get("attributes", []):
            self.add_attribute_card(attr)
    
    def populate_defects(self):
        for defect in self.metamorphosis_data.get("defects", []):
            self.add_defect_card(defect)
    
    def add_attribute(self):
        dialog = AttributeBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            attr_data = dialog.get_attribute_data()
            
            # Add a unique ID if not present
            if "id" not in attr_data:
                attr_data["id"] = str(uuid.uuid4())
            
            # Add to our metamorphosis data
            self.metamorphosis_data["attributes"].append(attr_data)
            
            # Add card to UI
            self.add_attribute_card(attr_data)
            
            # Update CP usage
            self.update_cp_display()
    
    def add_attribute_card(self, attr):
        # Create a function to remove this specific attribute
        def remove_this_attr():
            self.remove_attribute(attr["id"])
        
        # Create a function to edit this specific attribute
        def edit_this_attr():
            self.edit_attribute(attr["id"])
        
        # Format attribute display
        lines = []
        lines.append(f"Level: {attr.get('level', 1)}")
        lines.append(f"Cost: {attr.get('cost', 0)} CP")
        
        if attr.get("description"):
            lines.append(f"Description: {attr['description']}")
        
        # Create the card
        card = create_card_widget(
            title=attr["name"],
            lines=lines,
            on_remove=remove_this_attr,
            on_click=edit_this_attr,
            card_type="attribute"  # Use attribute type for styling
        )
        
        self.attributes_layout.insertWidget(0, card)
    
    def remove_attribute(self, attr_id):
        # Find the attribute with the given ID
        for i, attr in enumerate(self.metamorphosis_data["attributes"]):
            if attr.get("id") == attr_id:
                # Remove from data
                self.metamorphosis_data["attributes"].pop(i)
                break
        
        # Rebuild UI
        self.rebuild_attributes_ui()
        
        # Update CP usage
        self.update_cp_display()
    
    def edit_attribute(self, attr_id):
        # Find the attribute with the given ID
        attr_index = -1
        for i, attr in enumerate(self.metamorphosis_data["attributes"]):
            if attr.get("id") == attr_id:
                attr_index = i
                break
        
        if attr_index == -1:
            QMessageBox.warning(self, "Error", f"Attribute with ID {attr_id} not found.")
            return
        
        existing_attr = self.metamorphosis_data["attributes"][attr_index]
        
        dialog = AttributeBuilderDialog(self.parent)
        dialog.load_attribute_data(existing_attr)
        
        if dialog.exec_() == QDialog.Accepted:
            updated_attr = dialog.get_attribute_data()
            
            # Preserve the ID
            updated_attr["id"] = attr_id
            
            # Update in our data
            self.metamorphosis_data["attributes"][attr_index] = updated_attr
            
            # Rebuild UI
            self.rebuild_attributes_ui()
            
            # Update CP usage
            self.update_cp_display()
    
    def rebuild_attributes_ui(self):
        # Clear all widgets from the layout
        while self.attributes_layout.count():
            item = self.attributes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Re-add all attributes
        for attr in self.metamorphosis_data["attributes"]:
            self.add_attribute_card(attr)
    
    def add_defect(self):
        dialog = DefectBuilderDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            defect_data = dialog.get_defect_data()
            
            # Add a unique ID if not present
            if "id" not in defect_data:
                defect_data["id"] = str(uuid.uuid4())
            
            # Add to our metamorphosis data
            self.metamorphosis_data["defects"].append(defect_data)
            
            # Add card to UI
            self.add_defect_card(defect_data)
            
            # Update CP usage
            self.update_cp_display()
    
    def add_defect_card(self, defect):
        # Create a function to remove this specific defect
        def remove_this_defect():
            self.remove_defect(defect["id"])
        
        # Create a function to edit this specific defect
        def edit_this_defect():
            self.edit_defect(defect["id"])
        
        # Format defect display
        lines = []
        lines.append(f"Rank: {defect.get('rank', 1)}")
        lines.append(f"Value: {defect.get('value', 0)} CP")
        
        if defect.get("description"):
            lines.append(f"Description: {defect['description']}")
        
        # Create the card
        card = create_card_widget(
            title=defect["name"],
            lines=lines,
            on_remove=remove_this_defect,
            on_click=edit_this_defect,
            card_type="defect"  # Use defect type for styling
        )
        
        self.defects_layout.insertWidget(0, card)
    
    def remove_defect(self, defect_id):
        # Find the defect with the given ID
        for i, defect in enumerate(self.metamorphosis_data["defects"]):
            if defect.get("id") == defect_id:
                # Remove from data
                self.metamorphosis_data["defects"].pop(i)
                break
        
        # Rebuild UI
        self.rebuild_defects_ui()
        
        # Update CP usage
        self.update_cp_display()
    
    def edit_defect(self, defect_id):
        # Find the defect with the given ID
        defect_index = -1
        for i, defect in enumerate(self.metamorphosis_data["defects"]):
            if defect.get("id") == defect_id:
                defect_index = i
                break
        
        if defect_index == -1:
            QMessageBox.warning(self, "Error", f"Defect with ID {defect_id} not found.")
            return
        
        existing_defect = self.metamorphosis_data["defects"][defect_index]
        
        dialog = DefectBuilderDialog(self.parent)
        dialog.load_defect_data(existing_defect)
        
        if dialog.exec_() == QDialog.Accepted:
            updated_defect = dialog.get_defect_data()
            
            # Preserve the ID
            updated_defect["id"] = defect_id
            
            # Update in our data
            self.metamorphosis_data["defects"][defect_index] = updated_defect
            
            # Rebuild UI
            self.rebuild_defects_ui()
            
            # Update CP usage
            self.update_cp_display()
    
    def rebuild_defects_ui(self):
        # Clear all widgets from the layout
        while self.defects_layout.count():
            item = self.defects_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Re-add all defects
        for defect in self.metamorphosis_data["defects"]:
            self.add_defect_card(defect)
    
    def update_cp_display(self):
        # Calculate total CP used
        attr_cp = sum(attr.get("cost", 0) for attr in self.metamorphosis_data["attributes"])
        defect_cp = sum(defect.get("value", 0) for defect in self.metamorphosis_data["defects"])
        
        # Defects provide CP back (negative cost)
        self.total_cp_used = attr_cp - defect_cp
        
        # Update the display
        self.cp_used_display.setText(f"{self.total_cp_used} CP")
        
        # Check if we're over budget
        cp_budget = self.metamorphosis_data.get("cp", 5)
        if self.total_cp_used > cp_budget:
            self.cp_used_display.setStyleSheet("color: red;")
            self.save_btn.setEnabled(False)
        elif self.total_cp_used < -cp_budget:  # Check if we're under minimum budget
            self.cp_used_display.setStyleSheet("color: orange;")
            self.save_btn.setEnabled(False)
        else:
            self.cp_used_display.setStyleSheet("")
            self.save_btn.setEnabled(True)
    
    def get_metamorphosis_data(self):
        # Update the data with the current UI values
        self.metamorphosis_data["name"] = self.name_input.text()
        self.metamorphosis_data["description"] = self.desc_input.toPlainText()
        
        # Return the updated data
        return self.metamorphosis_data

    def save_to_library(self):
        QMessageBox.information(self, "Save to Library", "Feature not yet implemented.")

    def import_from_library(self):
        from dialogs.library_selector_dialog import LibrarySelectorDialog
        selector = LibrarySelectorDialog(self, "metamorphosis")
        if selector.exec_() == QDialog.Accepted:
            selected_obj = selector.get_selected_object()
            if selected_obj and selected_obj != "CREATE_NEW":
                self.populate_from_library(selected_obj)

    def populate_from_library(self, data):
        self.name_input.setText(data.get("name", ""))
        self.level_display.setText(str(data.get("level", 1)))
        self.metamorphosis_data.update(data)
        self.update_cp_display()
        self.populate_attributes()
        self.populate_defects()
