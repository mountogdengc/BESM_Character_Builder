import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QCheckBox
)
from PyQt5.QtCore import Qt

class LimiterDialog(QDialog):
    def __init__(self, parent=None, existing_limiters=None, limiter_counts=None):
        super().__init__(parent)
        self.setWindowTitle("Add Limiters")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        # Initialize result tracking
        self.selected_limiters = {}
        if limiter_counts:
            self.selected_limiters = limiter_counts.copy()
        
        # Load limiters data
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_path, "data", "limiters.json"), "r", encoding="utf-8") as f:
            self.raw_limiters = json.load(f)["limiters"]
            
        # Define maximum number of times each limiter can be selected
        self.max_limiter_picks = {
            "Maximum (Lvl 3-4 Max)": 1,
            "Maximum (Lvl 5+ Max)": 1,
            "Maximum (Lvl 2 Max)": 1
        }
        
        # Setup UI
        layout = QVBoxLayout(self)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search limiters...")
        self.search_input.textChanged.connect(self.filter_limiters)
        layout.addWidget(self.search_input)
        
        # Show all checkbox
        self.show_all = QCheckBox("Show All Options")
        self.show_all.setChecked(True)
        self.show_all.stateChanged.connect(self.filter_limiters)
        layout.addWidget(self.show_all)
        
        # Limiters list
        self.limiter_list = QListWidget()
        self.limiter_list.setSelectionMode(QListWidget.SingleSelection)
        self.limiter_list.itemClicked.connect(self.on_limiter_selection_changed)
        layout.addWidget(self.limiter_list)
        
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
        self.populate_limiter_list()
        
        # Select existing limiters if any
        if existing_limiters:
            for limiter in existing_limiters:
                # Handle both string and dictionary limiters
                limiter_name = limiter if isinstance(limiter, str) else limiter.get("name")
                count = self.selected_limiters.get(limiter_name, 1)
                self.selected_limiters[limiter_name] = count
        
        # Update the UI with selections
        self.update_limiters_display()
    
    def populate_limiter_list(self):
        """Populate the limiter list"""
        self.limiter_list.clear()
        
        for limiter in self.raw_limiters:
            item = QListWidgetItem(limiter["name"])
            item.setData(Qt.UserRole, limiter)
            
            # Mark as selected if in selected_limiters
            if limiter["name"] in self.selected_limiters:
                count = self.selected_limiters[limiter["name"]]
                max_count = self.max_limiter_picks.get(limiter["name"], 1)
                item.setText(f"{limiter['name']} ({count}/{max_count})")
                
            self.limiter_list.addItem(item)
    
    def filter_limiters(self):
        """Filter the limiter list based on search text"""
        search_text = self.search_input.text().lower()
        show_all = self.show_all.isChecked()
        
        for i in range(self.limiter_list.count()):
            item = self.limiter_list.item(i)
            limiter = item.data(Qt.UserRole)
            limiter_name = limiter["name"]
            
            # Get display name without count suffix
            display_name = limiter_name.split(" (")[0]
            
            # Determine if item should be visible
            show_item = show_all or search_text in display_name.lower()
            
            # Always show selected items
            if limiter_name in self.selected_limiters:
                show_item = True
                
            # Set item visibility
            self.limiter_list.setRowHidden(i, not show_item)
    
    def on_limiter_selection_changed(self):
        """Update controls when a limiter is selected"""
        selected_items = self.limiter_list.selectedItems()
        if not selected_items:
            self.decrement_btn.setEnabled(False)
            self.increment_btn.setEnabled(False)
            self.description_label.setText("")
            return
        
        item = selected_items[0]
        limiter = item.data(Qt.UserRole)
        limiter_name = limiter["name"]
        
        # Update description
        self.description_label.setText(limiter.get("description", ""))
        
        # Update count controls
        count = self.selected_limiters.get(limiter_name, 0)
        max_count = self.max_limiter_picks.get(limiter_name, 1)
        
        self.count_label.setText(f"{count}/{max_count}")
        self.decrement_btn.setEnabled(count > 0)
        self.increment_btn.setEnabled(count < max_count)
    
    def increment_count(self):
        """Increment the count for the selected limiter"""
        selected_items = self.limiter_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        limiter = item.data(Qt.UserRole)
        limiter_name = limiter["name"]
        
        current_count = self.selected_limiters.get(limiter_name, 0)
        max_count = self.max_limiter_picks.get(limiter_name, 1)
        
        if current_count < max_count:
            self.selected_limiters[limiter_name] = current_count + 1
            self.update_limiters_display()
    
    def decrement_count(self):
        """Decrement the count for the selected limiter"""
        selected_items = self.limiter_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        limiter = item.data(Qt.UserRole)
        limiter_name = limiter["name"]
        
        current_count = self.selected_limiters.get(limiter_name, 0)
        
        if current_count > 0:
            if current_count == 1:
                # Remove from selected if count reaches 0
                del self.selected_limiters[limiter_name]
            else:
                self.selected_limiters[limiter_name] = current_count - 1
            
            self.update_limiters_display()
    
    def update_limiters_display(self):
        """Update the limiters display with current selections"""
        # Reselect current item to update controls
        selected_items = self.limiter_list.selectedItems()
        current_selection = None
        if selected_items:
            current_selection = selected_items[0].data(Qt.UserRole)["name"]
        
        # Update list items
        for i in range(self.limiter_list.count()):
            item = self.limiter_list.item(i)
            limiter = item.data(Qt.UserRole)
            limiter_name = limiter["name"]
            
            if limiter_name in self.selected_limiters:
                count = self.selected_limiters[limiter_name]
                max_count = self.max_limiter_picks.get(limiter_name, 1)
                item.setText(f"{limiter_name} ({count}/{max_count})")
            else:
                item.setText(limiter_name)
        
        # Restore selection if there was one
        if current_selection:
            for i in range(self.limiter_list.count()):
                item = self.limiter_list.item(i)
                limiter = item.data(Qt.UserRole)
                if limiter["name"] == current_selection:
                    self.limiter_list.setCurrentItem(item)
                    break
        
        # Update count controls
        self.on_limiter_selection_changed()
    
    def get_selected_limiters(self):
        """Return the dictionary of selected limiters and their counts"""
        return self.selected_limiters 