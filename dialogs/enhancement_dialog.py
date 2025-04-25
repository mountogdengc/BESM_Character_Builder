import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QCheckBox
)
from PyQt5.QtCore import Qt

class EnhancementDialog(QDialog):
    def __init__(self, parent=None, existing_enhancements=None, enhancement_counts=None):
        super().__init__(parent)
        self.setWindowTitle("Add Enhancements")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        # Initialize result tracking
        self.selected_enhancements = {}
        if enhancement_counts:
            self.selected_enhancements = enhancement_counts.copy()
        
        # Load enhancements data
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_path, "data", "enhancements.json"), "r", encoding="utf-8") as f:
            self.raw_enhancements = json.load(f)["enhancements"]
            
        # Define maximum number of times each enhancement can be selected
        self.max_enhancement_picks = {
            "Area": 6,
            "Duration": 6,
            "Potent": 6,
            "Range": 6,
            "Targets": 6
        }
        
        # Setup UI
        layout = QVBoxLayout(self)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search enhancements...")
        self.search_input.textChanged.connect(self.filter_enhancements)
        layout.addWidget(self.search_input)
        
        # Show all checkbox
        self.show_all = QCheckBox("Show All Options")
        self.show_all.setChecked(True)
        self.show_all.stateChanged.connect(self.filter_enhancements)
        layout.addWidget(self.show_all)
        
        # Enhancement list
        self.enhancement_list = QListWidget()
        self.enhancement_list.setSelectionMode(QListWidget.SingleSelection)
        self.enhancement_list.itemClicked.connect(self.on_enhancement_selection_changed)
        layout.addWidget(self.enhancement_list)
        
        # Count controls
        count_layout = QHBoxLayout()
        self.decrement_btn = QPushButton("-")
        self.decrement_btn.clicked.connect(self.decrement_count)
        count_layout.addWidget(self.decrement_btn)
        
        self.count_label = QLabel("0")
        count_layout.addWidget(self.count_label)
        
        self.increment_btn = QPushButton("+")
        self.increment_btn.clicked.connect(self.increment_count)
        count_layout.addWidget(self.increment_btn)
        
        layout.addLayout(count_layout)
        
        # Description area
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setFixedHeight(80)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Populate the list
        self.populate_enhancement_list()
        
        # Select existing enhancements if any
        if existing_enhancements:
            for enhancement in existing_enhancements:
                # Handle both string and dictionary enhancements
                enhancement_name = enhancement if isinstance(enhancement, str) else enhancement.get("name")
                count = self.selected_enhancements.get(enhancement_name, 1)
                self.selected_enhancements[enhancement_name] = count
        
        # Update the UI with selections
        self.update_enhancements_display()
    
    def populate_enhancement_list(self):
        """Populate the enhancement list"""
        self.enhancement_list.clear()
        
        for enhancement in self.raw_enhancements:
            item = QListWidgetItem(enhancement["name"])
            item.setData(Qt.UserRole, enhancement)
            
            # Mark as selected if in selected_enhancements
            if enhancement["name"] in self.selected_enhancements:
                count = self.selected_enhancements[enhancement["name"]]
                max_count = self.max_enhancement_picks.get(enhancement["name"], 1)
                item.setText(f"{enhancement['name']} ({count}/{max_count})")
                
            self.enhancement_list.addItem(item)
    
    def filter_enhancements(self):
        """Filter the enhancement list based on search text"""
        search_text = self.search_input.text().lower()
        show_all = self.show_all.isChecked()
        
        for i in range(self.enhancement_list.count()):
            item = self.enhancement_list.item(i)
            enhancement = item.data(Qt.UserRole)
            enhancement_name = enhancement["name"]
            
            # Get display name without count suffix
            display_name = enhancement_name.split(" (")[0]
            
            # Determine if item should be visible
            show_item = show_all or search_text in display_name.lower()
            
            # Always show selected items
            if enhancement_name in self.selected_enhancements:
                show_item = True
                
            # Set item visibility
            self.enhancement_list.setRowHidden(i, not show_item)
    
    def on_enhancement_selection_changed(self):
        """Update controls when an enhancement is selected"""
        selected_items = self.enhancement_list.selectedItems()
        if not selected_items:
            self.decrement_btn.setEnabled(False)
            self.increment_btn.setEnabled(False)
            self.description_label.setText("")
            return
        
        item = selected_items[0]
        enhancement = item.data(Qt.UserRole)
        enhancement_name = enhancement["name"]
        
        # Update description
        self.description_label.setText(enhancement.get("description", ""))
        
        # Update count controls
        count = self.selected_enhancements.get(enhancement_name, 0)
        max_count = self.max_enhancement_picks.get(enhancement_name, 1)
        
        self.count_label.setText(f"{count}/{max_count}")
        self.decrement_btn.setEnabled(count > 0)
        self.increment_btn.setEnabled(count < max_count)
    
    def increment_count(self):
        """Increment the count for the selected enhancement"""
        selected_items = self.enhancement_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        enhancement = item.data(Qt.UserRole)
        enhancement_name = enhancement["name"]
        
        current_count = self.selected_enhancements.get(enhancement_name, 0)
        max_count = self.max_enhancement_picks.get(enhancement_name, 1)
        
        if current_count < max_count:
            self.selected_enhancements[enhancement_name] = current_count + 1
            self.update_enhancements_display()
    
    def decrement_count(self):
        """Decrement the count for the selected enhancement"""
        selected_items = self.enhancement_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        enhancement = item.data(Qt.UserRole)
        enhancement_name = enhancement["name"]
        
        current_count = self.selected_enhancements.get(enhancement_name, 0)
        
        if current_count > 0:
            if current_count == 1:
                # Remove from selected if count reaches 0
                del self.selected_enhancements[enhancement_name]
            else:
                self.selected_enhancements[enhancement_name] = current_count - 1
            
            self.update_enhancements_display()
    
    def update_enhancements_display(self):
        """Update the enhancements display with current selections"""
        # Reselect current item to update controls
        selected_items = self.enhancement_list.selectedItems()
        current_selection = None
        if selected_items:
            current_selection = selected_items[0].data(Qt.UserRole)["name"]
        
        # Update list items
        for i in range(self.enhancement_list.count()):
            item = self.enhancement_list.item(i)
            enhancement = item.data(Qt.UserRole)
            enhancement_name = enhancement["name"]
            
            if enhancement_name in self.selected_enhancements:
                count = self.selected_enhancements[enhancement_name]
                max_count = self.max_enhancement_picks.get(enhancement_name, 1)
                item.setText(f"{enhancement_name} ({count}/{max_count})")
            else:
                item.setText(enhancement_name)
        
        # Restore selection if there was one
        if current_selection:
            for i in range(self.enhancement_list.count()):
                item = self.enhancement_list.item(i)
                enhancement = item.data(Qt.UserRole)
                if enhancement["name"] == current_selection:
                    self.enhancement_list.setCurrentItem(item)
                    break
        
        # Update count controls
        self.on_enhancement_selection_changed()
    
    def get_selected_enhancements(self):
        """Return the dictionary of selected enhancements and their counts"""
        return self.selected_enhancements 