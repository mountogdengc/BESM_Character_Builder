# utils.py
import json
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from tools.widgets import ClickableCard

def create_card_widget(title="", lines=None, on_click=None, on_remove=None, card_type="default", parent=None, **kwargs):
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
    from PyQt5.QtCore import Qt

    # Create all widgets before adding them to layouts
    card = ClickableCard()
    container = QWidget(parent)  # Add parent parameter here
    title_label = QLabel(title)
    button_layout = QHBoxLayout()
    card_layout = QVBoxLayout(card)
    layout = QVBoxLayout(container)
    
    # Configure the card
    card.setMinimumHeight(80)
    card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
    apply_text_shadow(card)

    # Configure the container
    if card_type == "alternate_form":
        container.setObjectName("alternateFormCard")
    elif card_type == "attribute":
        container.setObjectName("attributeCard")
    elif card_type == "defect":
        container.setObjectName("defectCard")
    else:
        container.setObjectName("defaultCard")
    
    # Set cursor for clickable cards
    if on_click or on_remove:
        container.setCursor(QCursor(Qt.PointingHandCursor))
    
    container.setMinimumHeight(80)
    container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

    # Configure layouts
    layout.setContentsMargins(6, 6, 6, 10)
    layout.setSpacing(2)
    button_layout.setContentsMargins(0, 0, 0, 0)
    button_layout.addStretch()
    card_layout.setContentsMargins(0, 0, 0, 0)
    card_layout.setSpacing(0)

    # Create top row with title and remove button
    title_row = QHBoxLayout()
    title_row.setContentsMargins(0, 0, 0, 0)
    title_row.setSpacing(4)
    
    # Add title to the left of the title row
    title_label.setObjectName("cardTitle")
    title_row.addWidget(title_label, 1)  # Give it stretch
    
    # Add remove button to the right of the title row if needed
    if on_remove and card_type in ["attribute", "defect"]:
        remove_button = QPushButton("×")
        remove_button.setObjectName("removeButton")
        remove_button.setFixedSize(24, 24)
        remove_button.setToolTip("Remove")
        remove_button.clicked.connect(on_remove)
        remove_button.setCursor(QCursor(Qt.PointingHandCursor))
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 0;
                margin: 0;
                min-width: 24px;
                min-height: 24px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        title_row.addWidget(remove_button)
    
    # Add the title row to the main layout
    layout.addLayout(title_row)

    # Add content if provided
    if lines:
        content_label = QLabel("\n".join(lines))
        content_label.setObjectName("cardLabel")
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        content_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        content_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(content_label)
    
    # Add edit button if needed in the button layout
    if card_type == "alternate_form" or (card_type == "attribute" and on_click):
        edit_button = QPushButton("Edit")
        edit_button.setObjectName("editButton")
        edit_button.setToolTip("Edit")
        edit_button.clicked.connect(on_click)
        edit_button.setCursor(QCursor(Qt.PointingHandCursor))
        button_layout.addWidget(edit_button)
    
    # Add button layout if it's not empty
    if not button_layout.isEmpty():
        layout.addLayout(button_layout)

    # Assemble the final widget
    card_layout.addWidget(container)
    card_layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

    # Make card clickable if needed
    if on_click and card_type in ["defect", "attribute", "alternate_form"]:
        card.clicked.connect(on_click)
        container.mousePressEvent = lambda event: card.clicked.emit()

    return card


def generate_auto_name(base_name: str, fields: dict) -> str:
    """
    Returns a human-friendly name that incorporates relevant custom fields.
    `fields` is something like {"enemy_type": "Dragons", "category_type": "Psychic", ...}.
    """
    if base_name == "Enemy Attack":
        enemy = fields.get("enemy_type", "").strip()
        if enemy:
            return f"Enemy Attack vs. {enemy}"
        return base_name

    elif base_name == "Dynamic Powers":
        cat_type = fields.get("category_type", "").strip()
        controlled = fields.get("controlled_category", "").strip()
        if cat_type and controlled:
            return f"Dynamic Powers: {controlled} ({cat_type})"
        elif cat_type or controlled:
            return f"Dynamic Powers: {cat_type or controlled}"
        return base_name

    elif base_name == "Enemy Defense":
        enemy = fields.get("enemy_type", "").strip()
        if enemy:
            return f"Enemy Defense vs. {enemy}"
        return base_name

    # Fallback
    return base_name


def apply_text_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(2)
    shadow.setOffset(1, 1)
    shadow.setColor(QColor("black"))
    widget.setGraphicsEffect(shadow)


def cell(text, align_center=False):
    item = QTableWidgetItem(str(text))
    if align_center:
        item.setTextAlignment(Qt.AlignCenter)
    return item


def load_json_file(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return {}
    
def format_attribute_display(self, attr):
    name = attr["name"]
    level = attr["level"]
    cost = attr["cost"]

    custom_text = ""
    if "custom_fields" in attr and attr["custom_fields"]:
        tags = list(attr["custom_fields"].values())
        if tags:
            custom_text = f" [{' / '.join(tags)}]"

    return f"{name}{custom_text} (level {level}) - {cost} CP"

def sync_alternate_forms_from_attributes(self):
    # Clear and rebuild form blocks
    self.character_data["alternate_forms"].clear()
    self.clear_alternate_form_ui()

    for attr in self.character_data["attributes"]:
        if attr.get("base_name", attr["name"]) == "Alternate Form":
            form_data = {
                "name": f"Alternate Form ({attr['level']} CP)",
                "level": attr["level"],
                "cp_budget": attr["level"] * 5,
                "stats": self.character_data["stats"].copy(),
                "derived": self.character_data["derived"].copy(),
                "attributes": [],
                "defects": []
            }
            self.character_data["alternate_forms"].append(form_data)

    self.populate_alternate_form_ui()