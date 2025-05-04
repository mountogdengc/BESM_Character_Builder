import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QFormLayout, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt

class LibrarySelectorDialog(QDialog):
    """Dialog for selecting objects from the BESM library"""
    
    def __init__(self, parent=None, library_type="items"):
        super().__init__(parent)
        self.parent = parent
        self.library_type = library_type
        self.selected_object = None
        
        # Set title based on type
        type_titles = {
            "items": "Items",
            "companions": "Companions",
            "minions": "Minions",
            "metamorphosis": "Metamorphosis",
            "alternate_forms": "Alternate Forms"
        }
        
        self.setWindowTitle(f"Select from {type_titles.get(library_type, 'Library')}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # Load libraries data
        self.libraries_data = self.load_libraries_data()
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Add title and description
        title = QLabel(f"Select from Library")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        description = QLabel("Choose a pre-made object from the library to use in your character.")
        description.setWordWrap(True)
        
        main_layout.addWidget(title)
        main_layout.addWidget(description)
        
        # Add search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to search...")
        self.search_box.textChanged.connect(self.filter_list)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        
        main_layout.addLayout(search_layout)
        
        # Split view for list and preview
        content_layout = QHBoxLayout()
        
        # Left side - list of objects
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.show_preview)
        
        # Populate the list
        self.populate_list()
        
        # Right side - preview panel
        preview_panel = QVBoxLayout()
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold;")
        
        self.preview_area = QScrollArea()
        self.preview_area.setWidgetResizable(True)
        
        self.preview_widget = QLabel("Select an item to see details")
        self.preview_widget.setWordWrap(True)
        self.preview_widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.preview_area.setWidget(self.preview_widget)
        
        preview_panel.addWidget(preview_label)
        preview_panel.addWidget(self.preview_area)
        
        # Add to content layout
        content_layout.addWidget(self.list_widget, 1)
        content_layout.addLayout(preview_panel, 2)
        
        main_layout.addLayout(content_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("Select")
        self.select_btn.clicked.connect(self.accept_selection)
        self.select_btn.setEnabled(False)  # Disabled until selection is made
        
        self.new_btn = QPushButton("Create New")
        self.new_btn.clicked.connect(self.create_new)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.new_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.select_btn)
        
        main_layout.addLayout(button_layout)
        
    def load_libraries_data(self):
        """Load libraries data from file"""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_path, "data", "libraries.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Return empty structure if file doesn't exist
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
    
    def populate_list(self):
        """Populate the list with library objects"""
        self.list_widget.clear()
        
        if self.library_type not in self.libraries_data["libraries"]:
            return
            
        for obj in self.libraries_data["libraries"][self.library_type]:
            item = QListWidgetItem(obj.get("name", "Unnamed"))
            item.setData(Qt.UserRole, obj)
            self.list_widget.addItem(item)
    
    def filter_list(self, text):
        """Filter the list based on search text"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            obj = item.data(Qt.UserRole)
            
            name = obj.get("name", "").lower()
            desc = obj.get("description", "").lower()
            
            if text.lower() in name or text.lower() in desc:
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def show_preview(self, current, previous):
        """Show preview of the selected object"""
        if not current:
            self.preview_widget.setText("Select an item to see details")
            self.select_btn.setEnabled(False)
            return
            
        # Get the object data
        obj = current.data(Qt.UserRole)
        self.selected_object = obj
        
        # Enable the select button
        self.select_btn.setEnabled(True)
        
        # Create a formatted preview
        preview_widget = QWidget()
        preview_layout = QFormLayout(preview_widget)
        
        # Name
        name_label = QLabel(f"<b>{obj.get('name', 'Unnamed')}</b>")
        name_label.setStyleSheet("font-size: 14px;")
        preview_layout.addRow(name_label)
        
        # Description
        if "description" in obj and obj["description"]:
            desc_label = QLabel(obj.get("description", ""))
            desc_label.setWordWrap(True)
            preview_layout.addRow(desc_label)
        
        # Cost/Level
        if "cost" in obj:
            preview_layout.addRow(QLabel(f"<b>Cost:</b> {obj.get('cost', 0)} CP"))
        if "level" in obj:
            preview_layout.addRow(QLabel(f"<b>Level:</b> {obj.get('level', 1)}"))
            
        # Type-specific fields
        if self.library_type == "items":
            if "type" in obj:
                preview_layout.addRow(QLabel(f"<b>Type:</b> {obj.get('type', '')}"))
                
        elif self.library_type in ["companions", "minions"]:
            if "stats" in obj:
                stats = obj.get("stats", {})
                stats_str = f"Body: {stats.get('Body', 4)}, Mind: {stats.get('Mind', 4)}, Soul: {stats.get('Soul', 4)}"
                preview_layout.addRow(QLabel(f"<b>Stats:</b> {stats_str}"))
                
        # Replace the current preview
        self.preview_area.setWidget(preview_widget)
    
    def accept_selection(self):
        """Accept the selected object"""
        if self.selected_object:
            self.accept()
    
    def create_new(self):
        """Signal that user wants to create a new object instead"""
        self.selected_object = "CREATE_NEW"
        self.accept()
    
    def get_selected_object(self):
        """Return the selected object data"""
        return self.selected_object 