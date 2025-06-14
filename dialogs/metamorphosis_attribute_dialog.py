import uuid
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSpinBox, QTextEdit, QTabWidget, QWidget,
    QScrollArea, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from tools.utils import create_card_widget

class MetamorphosisAttributeDialog(QDialog):
    def __init__(self, parent, attribute_data=None):
        super().__init__(parent)
        self.parent = parent
        
        # Initialize with default or provided data
        self.attribute_data = attribute_data or {
            "id": str(uuid.uuid4()),
            "name": "Metamorphosis",
            "base_name": "Metamorphosis",
            "level": 1,
            "cost": 2,  # Base cost per level
            "effective_level": 1,
            "enhancers": [],
            "limiters": [],
            "description": "This offensive Attribute is used to alter a touched person's species for short durations.",
            "user_description": "",
            "custom_fields": {
                "template_name": "",
                "template_cp_value": 0
            }
        }
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Metamorphosis Attribute")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        main_layout = QVBoxLayout(self)
        
        # Basic info section
        info_layout = QVBoxLayout()
        
        # Name field (read-only since this is a specific attribute)
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit("Metamorphosis")
        self.name_input.setReadOnly(True)  # Can't change the name
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        info_layout.addLayout(name_layout)
        
        # Level field
        level_layout = QHBoxLayout()
        level_label = QLabel("Level:")
        self.level_input = QSpinBox()
        self.level_input.setMinimum(1)
        self.level_input.setMaximum(20)  # Reasonable maximum
        self.level_input.setValue(self.attribute_data.get("level", 1))
        self.level_input.valueChanged.connect(self.update_cost_display)
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_input)
        info_layout.addLayout(level_layout)
        
        # Cost display
        cost_layout = QHBoxLayout()
        cost_label = QLabel("Cost:")
        self.cost_display = QLabel(f"{self.attribute_data.get('level', 1) * 2} CP")
        cost_layout.addWidget(cost_label)
        cost_layout.addWidget(self.cost_display)
        cost_layout.addStretch()
        info_layout.addLayout(cost_layout)
        
        # Template name field
        template_name_layout = QHBoxLayout()
        template_name_label = QLabel("Template Name:")
        self.template_name_input = QLineEdit(self.attribute_data.get("custom_fields", {}).get("template_name", ""))
        template_name_layout.addWidget(template_name_label)
        template_name_layout.addWidget(self.template_name_input)
        info_layout.addLayout(template_name_layout)
        
        # Template CP value field
        template_cp_layout = QHBoxLayout()
        template_cp_label = QLabel("Template CP Value:")
        self.template_cp_input = QSpinBox()
        self.template_cp_input.setMinimum(-100)
        self.template_cp_input.setMaximum(100)
        self.template_cp_input.setValue(self.attribute_data.get("custom_fields", {}).get("template_cp_value", 0))
        self.template_cp_input.valueChanged.connect(self.validate_template_cp)
        template_cp_layout.addWidget(template_cp_label)
        template_cp_layout.addWidget(self.template_cp_input)
        info_layout.addLayout(template_cp_layout)
        
        # Template CP validation message
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red;")
        info_layout.addWidget(self.validation_label)
        
        # Description field
        desc_layout = QVBoxLayout()
        desc_label = QLabel("User Description:")
        self.desc_input = QTextEdit(self.attribute_data.get("user_description", ""))
        self.desc_input.setMaximumHeight(100)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        info_layout.addLayout(desc_layout)
        
        main_layout.addLayout(info_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
        
        # Initial validation
        self.validate_template_cp()
        
    def update_cost_display(self):
        level = self.level_input.value()
        cost = level * 2  # 2 points per level
        self.cost_display.setText(f"{cost} CP")
        self.validate_template_cp()
        
    def validate_template_cp(self):
        level = self.level_input.value()
        template_cp = self.template_cp_input.value()
        max_cp = level * 5
        
        if abs(template_cp) > max_cp:
            self.validation_label.setText(f"Template CP must be between -{max_cp} and {max_cp} for level {level}")
            self.save_button.setEnabled(False)
        else:
            self.validation_label.setText("")
            self.save_button.setEnabled(True)
    
    def get_attribute_data(self):
        print("Dialog accepted, getting attribute data...")
        
        # Update the data with the current UI values
        self.attribute_data["name"] = "Metamorphosis"
        self.attribute_data["base_name"] = "Metamorphosis"
        self.attribute_data["level"] = self.level_input.value()
        self.attribute_data["cost"] = self.level_input.value() * 2  # 2 points per level
        self.attribute_data["effective_level"] = self.level_input.value()
        self.attribute_data["user_description"] = self.desc_input.toPlainText()
        
        # Update custom fields
        if "custom_fields" not in self.attribute_data:
            self.attribute_data["custom_fields"] = {}
            
        self.attribute_data["custom_fields"]["template_name"] = self.template_name_input.text()
        self.attribute_data["custom_fields"]["template_cp_value"] = self.template_cp_input.value()
        
        print(f"Attribute data: {self.attribute_data}")
        
        # Return the updated data
        return self.attribute_data
