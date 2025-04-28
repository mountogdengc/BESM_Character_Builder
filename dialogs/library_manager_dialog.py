import os
import json
import uuid
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTabWidget, QWidget, QListWidget, QListWidgetItem,
    QComboBox, QMessageBox, QSplitter, QFormLayout, QScrollArea,
    QInputDialog, QFileDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from dialogs.item_builder_dialog import ItemBuilderDialog
from dialogs.companion_builder_dialog import CompanionBuilderDialog
from dialogs.minion_builder_dialog import MinionBuilderDialog
from dialogs.alternate_form_editor_dialog import AlternateFormEditorDialog
from dialogs.metamorphosis_editor_dialog import MetamorphosisEditorDialog


class LibraryManagerDialog(QDialog):
    """Dialog for managing libraries of pre-made BESM objects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Library Manager")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        
        # Load libraries data
        self.libraries_data = self.load_libraries_data()
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Add title and description
        title = QLabel("BESM Library Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        description = QLabel("Create and manage pre-made objects that can be reused when creating characters.")
        description.setWordWrap(True)
        
        main_layout.addWidget(title)
        main_layout.addWidget(description)
        
        # Add tab widget for different libraries
        self.tabs = QTabWidget()
        self.init_tabs()
        main_layout.addWidget(self.tabs)
        
        # Add bottom buttons
        button_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import Library")
        self.export_btn = QPushButton("Export Library")
        self.close_btn = QPushButton("Close")
        
        self.import_btn.clicked.connect(self.import_library)
        self.export_btn.clicked.connect(self.export_library)
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
    def init_tabs(self):
        """Initialize tabs for each library type"""
        # Create tabs for each library type
        self.init_items_tab()
        self.init_companions_tab()
        self.init_minions_tab()
        self.init_metamorphosis_tab()
        self.init_alternate_forms_tab()
        
    def init_items_tab(self):
        """Initialize the items tab"""
        self.items_tab = self.create_library_tab("items", "Items", ItemBuilderDialog)
        self.tabs.addTab(self.items_tab, "Items")
        
    def init_companions_tab(self):
        """Initialize the companions tab"""
        self.companions_tab = self.create_library_tab("companions", "Companions", CompanionBuilderDialog)
        self.tabs.addTab(self.companions_tab, "Companions")
        
    def init_minions_tab(self):
        """Initialize the minions tab"""
        self.minions_tab = self.create_library_tab("minions", "Minions", MinionBuilderDialog)
        self.tabs.addTab(self.minions_tab, "Minions")
        
    def init_metamorphosis_tab(self):
        """Initialize the metamorphosis tab"""
        self.metamorphosis_tab = self.create_library_tab("metamorphosis", "Metamorphosis", MetamorphosisEditorDialog)
        self.tabs.addTab(self.metamorphosis_tab, "Metamorphosis")
        
    def init_alternate_forms_tab(self):
        """Initialize the alternate forms tab"""
        self.alternate_forms_tab = self.create_library_tab("alternate_forms", "Alternate Forms", AlternateFormEditorDialog)
        self.tabs.addTab(self.alternate_forms_tab, "Alternate Forms") 

    def create_library_tab(self, library_type, title, dialog_class):
        """Create a standard tab for a library type"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Add header and controls
        header_layout = QHBoxLayout()
        tab_title = QLabel(f"{title} Library")
        tab_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        search_box = QLineEdit()
        search_box.setPlaceholderText(f"Search {title.lower()}...")
        search_box.textChanged.connect(lambda text: self.filter_library(library_type, text))
        
        header_layout.addWidget(tab_title)
        header_layout.addStretch()
        header_layout.addWidget(search_box)
        
        layout.addLayout(header_layout)
        
        # Create list and preview sections
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - list of library items
        list_widget = QListWidget()
        list_widget.setObjectName(f"{library_type}_list")
        list_widget.currentItemChanged.connect(
            lambda current, previous: self.show_object_preview(library_type, current)
        )
        
        # Fill the list with library objects
        self.populate_library_list(library_type, list_widget)
        
        # Right side - preview and edit controls
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # Preview content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(400)
        
        preview_content = QWidget()
        preview_content.setObjectName(f"{library_type}_preview_content")
        preview_content_layout = QVBoxLayout(preview_content)
        
        # Initial content - empty state
        empty_label = QLabel(f"Select a {title.lower().rstrip('s')} to view details")
        empty_label.setAlignment(Qt.AlignCenter)
        preview_content_layout.addWidget(empty_label)
        
        scroll.setWidget(preview_content)
        preview_layout.addWidget(scroll)
        
        # Button controls
        button_layout = QHBoxLayout()
        add_btn = QPushButton(f"Add New {title.rstrip('s')}")
        add_btn.clicked.connect(lambda: self.add_library_object(library_type, list_widget, dialog_class))
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_library_object(library_type, list_widget, dialog_class))
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_library_object(library_type, list_widget))
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        
        preview_layout.addLayout(button_layout)
        
        # Add to splitter
        splitter.addWidget(list_widget)
        splitter.addWidget(preview_widget)
        splitter.setSizes([200, 400])  # Initial sizes
        
        layout.addWidget(splitter)
        
        # Store references for later use
        setattr(self, f"{library_type}_list", list_widget)
        setattr(self, f"{library_type}_preview", preview_content)
        
        return tab
    
    def load_libraries_data(self):
        """Load libraries data from file"""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_path, "data", "libraries.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default structure if file doesn't exist
                default_data = {
                    "version": "1.0",
                    "libraries": {
                        "items": [],
                        "companions": [],
                        "minions": [],
                        "metamorphosis": [],
                        "alternate_forms": []
                    }
                }
                # Save the default structure
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, indent=2)
                return default_data
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load libraries data: {str(e)}")
            return {
                "version": "1.0",
                "libraries": {
                    "items": [],
                    "companions": [],
                    "minions": [],
                    "metamorphosis": [],
                    "alternate_forms": []
                }
            }
            
    def save_libraries_data(self):
        """Save libraries data to file"""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_path, "data", "libraries.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.libraries_data, f, indent=2)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save libraries data: {str(e)}")
            
    def populate_library_list(self, library_type, list_widget):
        """Populate list widget with library objects"""
        list_widget.clear()
        
        for obj in self.libraries_data["libraries"][library_type]:
            item = QListWidgetItem(obj.get("name", "Unnamed"))
            item.setData(Qt.UserRole, obj)  # Store the full object data
            list_widget.addItem(item) 

    def filter_library(self, library_type, text):
        """Filter the library list based on search text"""
        list_widget = getattr(self, f"{library_type}_list")
        
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            obj = item.data(Qt.UserRole)
            
            # Show item if search text is in name or description
            name = obj.get("name", "").lower()
            desc = obj.get("description", "").lower()
            
            if text.lower() in name or text.lower() in desc:
                item.setHidden(False)
            else:
                item.setHidden(True)
                
    def show_object_preview(self, library_type, current_item):
        """Show preview of the selected object"""
        if not current_item:
            return
            
        # Get the object data
        obj = current_item.data(Qt.UserRole)
        
        # Get the preview widget
        preview_widget = getattr(self, f"{library_type}_preview")
        
        # Clear existing content
        while preview_widget.layout().count():
            child = preview_widget.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Add preview content based on object type
        layout = QFormLayout()
        
        # Name
        layout.addRow(QLabel(f"<b>Name:</b> {obj.get('name', 'Unnamed')}"))
        
        # Cost (for all types)
        if "cost" in obj:
            layout.addRow(QLabel(f"<b>Cost:</b> {obj.get('cost', 0)} CP"))
        
        # Level (for attributes)
        if "level" in obj:
            layout.addRow(QLabel(f"<b>Level:</b> {obj.get('level', 1)}"))
            
        # Description
        if "description" in obj and obj["description"]:
            desc_label = QLabel(f"<b>Description:</b> {obj.get('description', '')}")
            desc_label.setWordWrap(True)
            layout.addRow(desc_label)
            
        # Type-specific fields
        if library_type == "items":
            # Item specific fields
            if "type" in obj:
                layout.addRow(QLabel(f"<b>Type:</b> {obj.get('type', '')}"))
            if "properties" in obj:
                props_label = QLabel(f"<b>Properties:</b> {', '.join(obj.get('properties', []))}")
                props_label.setWordWrap(True)
                layout.addRow(props_label)
                
        elif library_type == "companions" or library_type == "minions":
            # Character types specific fields
            if "stats" in obj:
                stats = obj.get("stats", {})
                stats_str = f"Body: {stats.get('Body', 4)}, Mind: {stats.get('Mind', 4)}, Soul: {stats.get('Soul', 4)}"
                layout.addRow(QLabel(f"<b>Stats:</b> {stats_str}"))
                
        elif library_type == "alternate_forms":
            # Alternate form specific
            if "cp_budget" in obj:
                layout.addRow(QLabel(f"<b>CP Budget:</b> {obj.get('cp_budget', 0)}"))
                
        preview_content = QWidget()
        preview_content.setLayout(layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(preview_content)
        
        preview_widget.layout().addWidget(scroll)
        
    def add_library_object(self, library_type, list_widget, dialog_class):
        """Add a new object to the library"""
        try:
            # Create a new object of the appropriate type
            dialog = None
            
            if library_type == "items":
                dialog = dialog_class(self.parent)
            elif library_type == "companions":
                dialog = dialog_class(self.parent)
            elif library_type == "minions":
                dialog = dialog_class(self.parent)
            elif library_type == "metamorphosis":
                dialog = dialog_class(self.parent)
            elif library_type == "alternate_forms":
                dialog = dialog_class(self.parent)
                
            if dialog and dialog.exec_():
                # Get the created object data
                if library_type == "items":
                    obj_data = dialog.get_item_data()
                elif library_type == "companions":
                    obj_data = dialog.get_companion_data()
                elif library_type == "minions":
                    obj_data = dialog.get_minion_data()
                elif library_type == "metamorphosis":
                    obj_data = dialog.get_metamorphosis_data()
                elif library_type == "alternate_forms":
                    obj_data = dialog.get_form_data()
                
                # Ensure the object has a unique ID
                if "id" not in obj_data:
                    obj_data["id"] = str(uuid.uuid4())
                    
                # Add to the library
                self.libraries_data["libraries"][library_type].append(obj_data)
                
                # Add to the list widget
                item = QListWidgetItem(obj_data.get("name", "Unnamed"))
                item.setData(Qt.UserRole, obj_data)
                list_widget.addItem(item)
                list_widget.setCurrentItem(item)
                
                # Save the updated library
                self.save_libraries_data()
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add object: {str(e)}")
            
    def edit_library_object(self, library_type, list_widget, dialog_class):
        """Edit an existing object in the library"""
        current_item = list_widget.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", f"Please select a {library_type.rstrip('s')} to edit.")
            return
            
        # Get the object data
        obj_data = current_item.data(Qt.UserRole)
        
        try:
            # Create an editor dialog with the object data
            dialog = None
            
            if library_type == "items":
                dialog = dialog_class(self.parent, obj_data)
            elif library_type == "companions":
                dialog = dialog_class(self.parent, obj_data)
            elif library_type == "minions":
                dialog = dialog_class(self.parent, obj_data)
            elif library_type == "metamorphosis":
                dialog = dialog_class(self.parent, obj_data)
            elif library_type == "alternate_forms":
                dialog = dialog_class(self.parent, form_data=obj_data)
                
            if dialog and dialog.exec_():
                # Get the updated object data
                if library_type == "items":
                    updated_data = dialog.get_item_data()
                elif library_type == "companions":
                    updated_data = dialog.get_companion_data()
                elif library_type == "minions":
                    updated_data = dialog.get_minion_data()
                elif library_type == "metamorphosis":
                    updated_data = dialog.get_metamorphosis_data()
                elif library_type == "alternate_forms":
                    updated_data = dialog.get_form_data()
                    
                # Ensure ID is preserved
                updated_data["id"] = obj_data["id"]
                
                # Update the library
                for i, obj in enumerate(self.libraries_data["libraries"][library_type]):
                    if obj.get("id") == obj_data["id"]:
                        self.libraries_data["libraries"][library_type][i] = updated_data
                        break
                        
                # Update the list item
                current_item.setText(updated_data.get("name", "Unnamed"))
                current_item.setData(Qt.UserRole, updated_data)
                
                # Update the preview
                self.show_object_preview(library_type, current_item)
                
                # Save the updated library
                self.save_libraries_data()
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit object: {str(e)}")
            
    def delete_library_object(self, library_type, list_widget):
        """Delete an object from the library"""
        current_item = list_widget.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", f"Please select a {library_type.rstrip('s')} to delete.")
            return
            
        # Get the object data
        obj_data = current_item.data(Qt.UserRole)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete '{obj_data.get('name', 'Unnamed')}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from the library
            self.libraries_data["libraries"][library_type] = [
                obj for obj in self.libraries_data["libraries"][library_type]
                if obj.get("id") != obj_data.get("id")
            ]
            
            # Remove from the list widget
            row = list_widget.row(current_item)
            list_widget.takeItem(row)
            
            # Clear the preview if needed
            if list_widget.count() == 0:
                preview_widget = getattr(self, f"{library_type}_preview")
                
                # Clear existing content
                while preview_widget.layout().count():
                    child = preview_widget.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                        
                # Show empty state
                empty_label = QLabel(f"Select a {library_type.rstrip('s')} to view details")
                empty_label.setAlignment(Qt.AlignCenter)
                preview_widget.layout().addWidget(empty_label)
                
            # Save the updated library
            self.save_libraries_data()
            
    def import_library(self):
        """Import a library from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Library",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
                
            # Validate the imported data
            if "libraries" not in imported_data:
                QMessageBox.warning(self, "Invalid File", "The selected file does not contain valid library data.")
                return
                
            # Determine what to import
            library_types = ["items", "companions", "minions", "metamorphosis", "alternate_forms"]
            
            # Count items in each library
            counts = {}
            for lib_type in library_types:
                if lib_type in imported_data["libraries"]:
                    counts[lib_type] = len(imported_data["libraries"][lib_type])
                    
            # If nothing to import, show message
            if not counts:
                QMessageBox.information(self, "Nothing to Import", "The selected file does not contain any library data to import.")
                return
                
            # Show confirmation with counts
            message = "The following items will be imported:\n\n"
            for lib_type, count in counts.items():
                if count > 0:
                    message += f"- {lib_type.capitalize()}: {count} items\n"
                    
            message += "\nDo you want to continue with the import?"
            
            reply = QMessageBox.question(
                self,
                "Confirm Import",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Merge with existing libraries
                for lib_type in library_types:
                    if lib_type in imported_data["libraries"]:
                        existing_ids = [obj.get("id") for obj in self.libraries_data["libraries"][lib_type]]
                        
                        for obj in imported_data["libraries"][lib_type]:
                            # Ensure the object has an ID
                            if "id" not in obj:
                                obj["id"] = str(uuid.uuid4())
                                
                            # If ID already exists, generate a new one
                            if obj["id"] in existing_ids:
                                obj["id"] = str(uuid.uuid4())
                                
                            # Add to library
                            self.libraries_data["libraries"][lib_type].append(obj)
                            
                # Save and refresh
                self.save_libraries_data()
                
                # Refresh all library lists
                for lib_type in library_types:
                    list_widget = getattr(self, f"{lib_type}_list", None)
                    if list_widget:
                        self.populate_library_list(lib_type, list_widget)
                        
                QMessageBox.information(self, "Import Complete", "Library import completed successfully.")
                
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Failed to import library: {str(e)}")
            
    def export_library(self):
        """Export the library to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Library",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
            
        # Ensure the file has a .json extension
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.libraries_data, f, indent=2)
                
            QMessageBox.information(self, "Export Complete", "Library exported successfully.")
            
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export library: {str(e)}")
            
    def get_library_object(self, library_type, obj_id):
        """Get a library object by ID"""
        for obj in self.libraries_data["libraries"][library_type]:
            if obj.get("id") == obj_id:
                return obj
        return None 