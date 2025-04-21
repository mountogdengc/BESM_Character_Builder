# metamorphosis_tab

import uuid
from uuid import uuid4
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy
)
from tools.utils import create_card_widget

def init_metamorphosis_tab(self):
    tab = QWidget()
    outer_layout = QVBoxLayout(tab)

    # Scroll area
    self.metamorphosis_scroll_area = QScrollArea()
    self.metamorphosis_scroll_area.setWidgetResizable(True)
    outer_layout.addWidget(self.metamorphosis_scroll_area)

    # Card container and layout
    self.metamorphosis_card_container = QWidget()
    self.metamorphosis_layout = QVBoxLayout(self.metamorphosis_card_container)
    self.metamorphosis_layout.setContentsMargins(8, 8, 8, 8)
    self.metamorphosis_layout.setSpacing(6)
    self.metamorphosis_layout.setAlignment(Qt.AlignTop)

    self.metamorphosis_scroll_area.setWidget(self.metamorphosis_card_container)

    # No Add button - Metamorphosis forms are created when the Metamorphosis attribute is added
    # This follows the pattern for special attribute tabs

    self.metamorphosis_tab = tab
    self.tabs.addTab(tab, "Metamorphosis")

def sync_metamorphosis_from_attributes(self):
    self.character_data["metamorphosis"].clear()
    clear_metamorphosis_ui(self)

    for attr in self.character_data["attributes"]:
        if attr.get("base_name", attr["name"]) == "Metamorphosis":
            meta_id = str(uuid4())
            meta_data = {
                "id": meta_id,
                "name": attr.get("custom_fields", {}).get("template_name", "Unnamed Form"),
                "level": attr["level"],
                "description": f"Transforms into a new form with {attr['level'] * 5} CP of changes",
                "cp": attr["level"] * 5,  # Metamorphosis CP budget scales with level
                "attributes": [],
                "defects": []
            }
            self.character_data["metamorphosis"].append(meta_data)

    populate_metamorphosis_ui(self)

def clear_metamorphosis_ui(self):
    # Delete old layout by replacing the card container entirely
    if hasattr(self, "metamorphosis_card_container"):
        self.metamorphosis_card_container.deleteLater()

    # Create a new container and layout
    from PyQt5.QtWidgets import QWidget, QVBoxLayout

    self.metamorphosis_card_container = QWidget()
    self.metamorphosis_layout = QVBoxLayout(self.metamorphosis_card_container)
    self.metamorphosis_layout.setContentsMargins(8, 8, 8, 8)
    self.metamorphosis_layout.setSpacing(6)
    self.metamorphosis_layout.setAlignment(Qt.AlignTop)

    self.metamorphosis_scroll_area.setWidget(self.metamorphosis_card_container)

def populate_metamorphosis_ui(self):
    clear_metamorphosis_ui(self)
    for meta in self.character_data["metamorphosis"]:
        lines = []

        # Basic info
        lines.append(f"Level: {meta.get('level', 0)}")
        lines.append(f"CP Budget: {meta.get('cp', 0)} CP")
        
        if meta.get("description"):
            lines.append(f"Description: {meta['description']}")

        # Attributes/Defects summary
        attr_names = [a["name"] for a in meta.get("attributes", [])]
        defect_names = [d["name"] for d in meta.get("defects", [])]

        if attr_names:
            lines.append("Attributes: " + ", ".join(attr_names))
        if defect_names:
            lines.append("Defects: " + ", ".join(defect_names))

        # Use a lambda function to capture the current meta ID
        card = create_card_widget(
            title=meta["name"],
            lines=lines,
            on_click=lambda meta_id=meta["id"]: edit_metamorphosis(self, meta_id)
        )
        self.metamorphosis_layout.insertWidget(0, card)

def edit_metamorphosis(self, uid):
    """Edit a metamorphosis form"""
    # Import the dialog
    from dialogs.metamorphosis_editor_dialog import MetamorphosisEditorDialog
    from PyQt5 import QtWidgets
    
    # Find the metamorphosis form with the given ID
    form = None
    for meta in self.character_data.get("metamorphosis", []):
        if meta.get("id") == uid:
            form = meta
            break
            
    if not form:
        QtWidgets.QMessageBox.warning(self, "Error", f"Metamorphosis form with ID {uid} not found.")
        return
        
    dialog = MetamorphosisEditorDialog(self, metamorphosis_data=form)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        updated_form = dialog.get_metamorphosis_data()
        
        # Replace the old form (keeping the ID intact)
        for i, existing in enumerate(self.character_data["metamorphosis"]):
            if existing.get("id") == uid:
                self.character_data["metamorphosis"][i] = updated_form
                break
                
        # Update the UI
        populate_metamorphosis_ui(self)
        
        # Update point total
        self.update_point_total()

__all__ = [
    "init_metamorphosis_tab",
    "sync_metamorphosis_from_attributes",
    "clear_metamorphosis_ui",
    "populate_metamorphosis_ui",
    "edit_metamorphosis"
]