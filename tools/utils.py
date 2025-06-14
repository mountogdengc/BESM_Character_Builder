# utils.py
import json
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from tools.widgets import ClickableCard

def create_card_widget(title="", lines=None, on_click=None, on_remove=None, card_type="default", **kwargs):
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
    from PyQt5.QtCore import Qt

    # Outer ClickableCard (invisible wrapper)
    card = ClickableCard()
    card.setMinimumHeight(80)  # Minimum height for aesthetics
    
    # Set size policy to allow the card to grow vertically
    card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

    # Shadow effect
    apply_text_shadow(card)

    # Inner container — the actual visible card
    container = QWidget()
    container.setObjectName("alternateFormCard")  # ✅ Apply the style here
    container.setMinimumHeight(80)  # Also set minimum height on container
    container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

    layout = QVBoxLayout(container)
    layout.setContentsMargins(6, 6, 6, 10)
    layout.setSpacing(2)

    # Title
    title_label = QLabel(title)
    title_label.setObjectName("cardTitle")
    layout.addWidget(title_label)

    # Lines (summary)
    if lines:
        content_label = QLabel("\n".join(lines))
        content_label.setObjectName("cardLabel")
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection
        content_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)  # Allow vertical expansion
        # Don't set a minimum height, let it be determined by content
        # Adjust alignment to top to prevent extra space at bottom
        content_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(content_label)
    
    # Add buttons layout
    button_layout = QHBoxLayout()
    button_layout.setContentsMargins(0, 0, 0, 0)
    button_layout.addStretch()
    
    # Add edit button for alternate form cards
    if card_type == "alternate_form" or on_click:
        edit_button = QPushButton("Edit")
        edit_button.setObjectName("editButton")
        edit_button.setToolTip("Edit")
        edit_button.clicked.connect(on_click)
        button_layout.addWidget(edit_button)
    
    # Add remove button if requested (only for attribute and defect cards, not for special tabs)
    if on_remove and card_type in ["attribute", "defect"]:
        remove_button = QPushButton("×")
        remove_button.setObjectName("removeButton")
        remove_button.setFixedSize(20, 20)
        remove_button.setToolTip("Remove")
        remove_button.clicked.connect(on_remove)
        button_layout.addWidget(remove_button)
    
    # Only add the button layout if we have any buttons
    if not button_layout.isEmpty():
        layout.addLayout(button_layout)

    # Mount the styled container into the outer card
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(0, 0, 0, 0)
    card_layout.setSpacing(0)  # Remove spacing
    card_layout.addWidget(container)
    card_layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)  # Make layout only as big as needed

    # Make the entire card clickable
    if on_click:
        card.clicked.connect(on_click)
        # Also make the container clickable to ensure the entire card responds to clicks
        container.mousePressEvent = lambda event: card.clicked.emit()

    print("Card uses container with objectName:", container.objectName())

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