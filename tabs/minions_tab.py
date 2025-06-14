# minions_tab

import uuid
from uuid import uuid4
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy
)
from tools.utils import create_card_widget

def init_minions_tab(self):
    tab = QWidget()
    outer_layout = QVBoxLayout(tab)

    # Scroll area
    self.minions_scroll_area = QScrollArea()
    self.minions_scroll_area.setWidgetResizable(True)
    outer_layout.addWidget(self.minions_scroll_area)

    # Card container and layout
    self.minions_card_container = QWidget()
    self.minions_layout = QVBoxLayout(self.minions_card_container)
    self.minions_layout.setContentsMargins(8, 8, 8, 8)
    self.minions_layout.setSpacing(6)
    self.minions_layout.setAlignment(Qt.AlignTop)

    self.minions_scroll_area.setWidget(self.minions_card_container)

    # Add button
    add_button = QPushButton("Add Minions")
    add_button.clicked.connect(self.add_minions)
    add_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    outer_layout.addWidget(add_button)

    self.minions_tab = tab
    self.tabs.addTab(tab, "Minions")

def sync_minions_from_attributes(self):
    self.character_data["minions"].clear()
    clear_minions_ui(self)

    for attr in self.character_data["attributes"]:
        if attr.get("base_name", attr["name"]) == "Minions":
            minion_id = str(uuid4())
            # Calculate the number of minions based on level
            num_minions = 5  # Default for level 1
            level = attr.get("level", 1)
            
            if level == 2:
                num_minions = 10
            elif level == 3:
                num_minions = 25
            elif level == 4:
                num_minions = 50
            elif level == 5:
                num_minions = 100
            elif level == 6:
                num_minions = 200
                
            minion_data = {
                "id": minion_id,
                "name": attr.get("custom_fields", {}).get("minion_type", "Unnamed Minions"),
                "level": attr["level"],
                "description": f"Group of {num_minions} minions",
                "count": num_minions,
                "cp": int(self.character_data["totalPoints"] * 0.2),  # 1/5 of character's total points
                "attributes": [],
                "defects": []
            }
            self.character_data["minions"].append(minion_data)

    populate_minions_ui(self)

def clear_minions_ui(self):
    # Delete old layout by replacing the card container entirely
    if hasattr(self, "minions_card_container"):
        self.minions_card_container.deleteLater()

    # Create a new container and layout
    from PyQt5.QtWidgets import QWidget, QVBoxLayout

    self.minions_card_container = QWidget()
    self.minions_layout = QVBoxLayout(self.minions_card_container)
    self.minions_layout.setContentsMargins(8, 8, 8, 8)
    self.minions_layout.setSpacing(6)
    self.minions_layout.setAlignment(Qt.AlignTop)

    self.minions_scroll_area.setWidget(self.minions_card_container)

def populate_minions_ui(self):
    clear_minions_ui(self)
    for minion in self.character_data["minions"]:
        lines = []

        # Basic info
        lines.append(f"Level: {minion.get('level', 0)}")
        lines.append(f"Count: {minion.get('count', 0)} minions")
        lines.append(f"CP Budget per minion: {minion.get('cp', 0)} CP")
        
        if minion.get("description"):
            lines.append(f"Description: {minion['description']}")

        # Attributes/Defects summary
        attr_names = [a["name"] for a in minion.get("attributes", [])]
        defect_names = [d["name"] for d in minion.get("defects", [])]

        if attr_names:
            lines.append("Attributes: " + ", ".join(attr_names))
        if defect_names:
            lines.append("Defects: " + ", ".join(defect_names))

        card = create_card_widget(
            title=minion["name"],
            lines=lines,
            on_click=lambda uid=minion["id"]: self.edit_minion(uid)
        )
        self.minions_layout.insertWidget(0, card)

__all__ = [
    "init_minions_tab",
    "sync_minions_from_attributes",
    "clear_minions_ui",
    "populate_minions_ui"
]