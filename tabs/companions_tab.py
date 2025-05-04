# companions_tab

import uuid
from uuid import uuid4
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QMessageBox
)
from tools.utils import create_card_widget
from dialogs.companion_builder_dialog import CompanionBuilderDialog

def init_companions_tab(self):
    tab = QWidget()
    outer_layout = QVBoxLayout(tab)

    # Scroll area
    self.companions_scroll_area = QScrollArea()
    self.companions_scroll_area.setWidgetResizable(True)
    outer_layout.addWidget(self.companions_scroll_area)

    # Card container and layout
    self.companions_card_container = QWidget()
    self.companions_layout = QVBoxLayout(self.companions_card_container)
    self.companions_layout.setContentsMargins(8, 8, 8, 8)
    self.companions_layout.setSpacing(6)
    self.companions_layout.setAlignment(Qt.AlignTop)

    self.companions_scroll_area.setWidget(self.companions_card_container)

    self.companions_tab = tab
    self.tabs.addTab(tab, "Companions")

def sync_companions_from_attributes(self):
    print("[DEBUG] Starting sync_companions_from_attributes")
    self.character_data["companions"].clear()
    clear_companions_ui(self)

    for attr in self.character_data["attributes"]:
        # Check for both singular and plural forms of the attribute name
        base_name = attr.get("base_name", attr["name"])
        print(f"[DEBUG] Checking attribute: {base_name}")
        
        if base_name in ["Companion", "Companions"]:
            print(f"[DEBUG] Found Companion attribute with level {attr['level']}")
            # Use the attribute's ID instead of generating a new one
            companion_data = {
                "id": attr["id"],  # Use the attribute's ID
                "name": f"Companion ({attr['level']} CP)",
                "level": attr["level"],
                "cp_budget": attr["level"] * 10,  # Companion gets 10 CP per level
                "stats": self.character_data["stats"].copy(),
                "derived": self.character_data["derived"].copy(),
                "attributes": [],
                "defects": []
            }
            self.character_data["companions"].append(companion_data)
            print(f"[DEBUG] Added companion with ID {companion_data['id']}")

    print(f"[DEBUG] Total companions: {len(self.character_data['companions'])}")
    populate_companions_ui(self)

def clear_companions_ui(self):
    # Delete old layout by replacing the card container entirely
    if hasattr(self, "companions_card_container"):
        self.companions_card_container.deleteLater()

    # Create a new container and layout
    from PyQt5.QtWidgets import QWidget, QVBoxLayout

    self.companions_card_container = QWidget()
    self.companions_layout = QVBoxLayout(self.companions_card_container)
    self.companions_layout.setContentsMargins(8, 8, 8, 8)
    self.companions_layout.setSpacing(6)
    self.companions_layout.setAlignment(Qt.AlignTop)

    self.companions_scroll_area.setWidget(self.companions_card_container)

def populate_companions_ui(self):
    print("[DEBUG] Starting populate_companions_ui")
    clear_companions_ui(self)
    print(f"[DEBUG] Number of companions to display: {len(self.character_data['companions'])}")
    
    for companion in self.character_data["companions"]:
        print(f"[DEBUG] Creating card for companion: {companion['name']}")
        stats = companion.get("stats", {})
        derived = companion.get("derived", {})

        lines = []

        # Basic stats
        lines.append(f"Body {stats.get('Body', 0)}, Mind {stats.get('Mind', 0)}, Soul {stats.get('Soul', 0)}")

        # Derived stats
        lines.append(
            f"Combat Value {derived.get('CV', 0)}, Attack Combat Value {derived.get('ACV', 0)}, Defense Combat Value {derived.get('DCV', 0)}, "
            f"Health Points {derived.get('HP', 0)}, EP {derived.get('EP', 0)}, Damage Multiplier {derived.get('DM', 0)}"
        )

        # Attributes/Defects summary
        attr_names = [a["name"] for a in companion.get("attributes", [])]
        defect_names = [d["name"] for d in companion.get("defects", [])]

        if attr_names:
            lines.append("Attributes: " + ", ".join(attr_names))
        if defect_names:
            lines.append("Defects: " + ", ".join(defect_names))

        print(f"[DEBUG] Card lines: {lines}")
        
        # Create a unique function for each companion to avoid lambda capture issues
        def make_click_handler(uid):
            def click_handler():
                self.edit_companion(uid)
            return click_handler
            
        card = create_card_widget(
            title=companion["name"],
            lines=lines,
            on_click=make_click_handler(companion["id"]),
            card_type="attribute"  # Make it styled and clickable like attribute cards
        )
        print(f"[DEBUG] Card created, adding to layout")
        self.companions_layout.insertWidget(0, card)
        
    print("[DEBUG] Finished populate_companions_ui")

def edit_companion(self, companion_id):
    # Find the companion data by ID
    companion_data = None
    for companion in self.character_data["companions"]:
        if companion["id"] == companion_id:
            companion_data = companion
            break
    
    if not companion_data:
        QMessageBox.warning(self, "Error", "Companion not found.")
        return
    
    # Open the companion builder dialog
    dialog = CompanionBuilderDialog(self, companion_data)
    if dialog.exec_():
        # Get updated companion data
        updated_data = dialog.get_companion_data()
        
        # Update the companion in character data
        for i, companion in enumerate(self.character_data["companions"]):
            if companion["id"] == companion_id:
                self.character_data["companions"][i] = updated_data
                break
        
        # Refresh the UI
        populate_companions_ui(self)

__all__ = [
    "init_companions_tab",
    "sync_companions_from_attributes",
    "clear_companions_ui",
    "populate_companions_ui",
    "edit_companion"
]