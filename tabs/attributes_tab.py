import uuid
from uuid import uuid4
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea
)

from tools.utils import create_card_widget

def init_attributes_tab(app, layout):
    """
    Initializes the Attributes tab. Sets up a scrollable card layout
    and a button row with an Add button that calls the add_attribute method.
    """
    tab = QWidget()
    outer_layout = QVBoxLayout(tab)

    # Scroll area
    app.attributes_scroll_area = QScrollArea()
    app.attributes_scroll_area.setWidgetResizable(True)
    outer_layout.addWidget(app.attributes_scroll_area)

    # Card container and layout
    app.attr_card_container = QWidget()
    app.attributes_layout = QVBoxLayout(app.attr_card_container)
    app.attributes_layout.setContentsMargins(8, 8, 8, 8)
    app.attributes_layout.setSpacing(6)
    app.attributes_layout.setAlignment(Qt.AlignTop)

    app.attributes_scroll_area.setWidget(app.attr_card_container)

    # Add the button to the provided layout
    add_button = QPushButton("Add Attribute")
    add_button.clicked.connect(app.add_attribute)
    layout.addWidget(add_button)

    app.attributes_tab = tab
    app.tabs.addTab(tab, "Attributes")

def sync_attributes(self):
    """
    Calls populate_attributes_ui to rebuild the attribute cards from
    self.character_data['attributes'].
    """
    populate_attributes_ui(self)

def clear_attributes_ui(self):
    """Clear the attributes UI by removing all attribute cards"""
    if hasattr(self, 'attr_card_container') and self.attr_card_container is not None:
        try:
            # Check if layout exists and is valid
            if hasattr(self, 'attributes_layout') and self.attributes_layout is not None:
                # Store a reference to the layout before clearing
                layout = self.attributes_layout
                
                # Clear all widgets from the layout
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        w = item.widget()
                        w.setParent(None)
                        # Ensure the widget is deleted to avoid floating windows
                        w.deleteLater()
            
            # Remove the container from the scroll area if it exists and delete it
            if hasattr(self, 'attributes_scroll_area') and self.attributes_scroll_area is not None and self.attr_card_container is not None:
                self.attributes_scroll_area.takeWidget()
                # Safely delete container and its children to avoid orphan pop-ups
                self.attr_card_container.setParent(None)
                self.attr_card_container.deleteLater()
            
            # Clear references
            self.attr_card_container = None
            self.attributes_layout = None
        except RuntimeError:
            # If we get a runtime error, just clear the references
            self.attr_card_container = None
            self.attributes_layout = None

def populate_attributes_ui(self):
    """Populate the attributes UI with cards for each attribute"""
    # Clear existing UI first
    clear_attributes_ui(self)
    
    # Create new container if needed
    if not hasattr(self, 'attr_card_container') or self.attr_card_container is None:
        self.attr_card_container = QWidget()
        self.attributes_layout = QVBoxLayout(self.attr_card_container)
        self.attributes_layout.setContentsMargins(8, 8, 8, 8)
        self.attributes_layout.setSpacing(6)
        self.attributes_layout.setAlignment(Qt.AlignTop)
        self.attributes_scroll_area.setWidget(self.attr_card_container)
    
    # Add attribute cards
    for attr in self.character_data.get("attributes", []):
        # Create and add attribute card
        card = create_attribute_card(self, attr)
        # Explicitly parent the card to the container to avoid stray windows
        card.setParent(self.attr_card_container)
        self.attributes_layout.addWidget(card)

def create_attribute_card(self, attr):
    """Create a card widget for an attribute"""
    # Create a unique identifier for this attribute if it doesn't have one
    if "id" not in attr:
        attr["id"] = str(uuid4())
        
    # Create the remove function for this specific attribute
    def make_remove_handler(attr_id):
        def remove_handler():
            self.remove_attribute_by_id(attr_id)
        return remove_handler
    
    # Create the edit function for this specific attribute
    def make_edit_handler(attr_id):
        def edit_handler():
            base_name = attr.get("base_name", attr["name"])
            if base_name in ["Item", "Items"]:
                self.edit_item(attr_id)
            elif base_name in ["Companion", "Companions"]:
                self.edit_companion(attr_id)
            elif base_name == "Minions":
                self.edit_minion(attr_id)
            elif base_name == "Metamorphosis":
                self.edit_metamorphosis(attr_id)
            elif base_name == "Alternate Form":
                self.edit_alternate_form(attr_id)
            else:
                self.edit_attribute_by_id(attr_id)
        return edit_handler
    
    # Format the display lines based on attribute type
    base_name = attr.get("base_name", attr["name"])
    
    if base_name in ["Item", "Items"]:
        # For Items, show total cost and list of items
        items = [item for item in self.character_data.get("items", []) 
                if item.get("id") == attr.get("id")]
        item_names = [item.get("name", "Unnamed Item") for item in items]
        item_list = ", ".join(item_names) if item_names else "None"
        
        lines = [
            f"Level: {attr.get('level', 0)}",
            f"Cost: {attr.get('cost', 0)} CP",
            f"Items: {item_list}"
        ]
    elif base_name in ["Companion", "Companions"]:
        # For Companions, show companion details
        companions = [comp for comp in self.character_data.get("companions", []) 
                     if comp.get("id") == attr.get("id")]
        if companions:
            comp = companions[0]
            stats = comp.get("stats", {})
            lines = [
                f"Level: {attr.get('level', 0)}",
                f"Cost: {attr.get('cost', 0)} CP",
                f"Stats: Body {stats.get('Body', 0)}, Mind {stats.get('Mind', 0)}, Soul {stats.get('Soul', 0)}"
            ]
        else:
            lines = [
                f"Level: {attr.get('level', 0)}",
                f"Cost: {attr.get('cost', 0)} CP"
            ]
    elif base_name == "Minions":
        # For Minions, show minion details
        minions = [minion for minion in self.character_data.get("minions", []) 
                  if minion.get("id") == attr.get("id")]
        minion_names = [minion.get("name", "Unnamed Minion") for minion in minions]
        minion_list = ", ".join(minion_names) if minion_names else "None"
        
        lines = [
            f"Level: {attr.get('level', 0)}",
            f"Cost: {attr.get('cost', 0)} CP",
            f"Minions: {minion_list}"
        ]
    elif base_name == "Metamorphosis":
        # For Metamorphosis, show metamorphosis details
        meta_forms = [form for form in self.character_data.get("metamorphosis", []) 
                     if form.get("id") == attr.get("id")]
        form_names = [form.get("name", "Unnamed Form") for form in meta_forms]
        form_list = ", ".join(form_names) if form_names else "None"
        
        lines = [
            f"Level: {attr.get('level', 0)}",
            f"Cost: {attr.get('cost', 0)} CP",
            f"Forms: {form_list}"
        ]
    elif base_name == "Alternate Form":
        # For Alternate Forms, show form details
        forms = [form for form in self.character_data.get("alternate_forms", []) 
                if form.get("id") == attr.get("id")]
        if forms:
            form = forms[0]
            stats = form.get("stats", {})
            lines = [
                f"Level: {attr.get('level', 0)}",
                f"Cost: {attr.get('cost', 0)} CP",
                f"Stats: Body {stats.get('Body', 0)}, Mind {stats.get('Mind', 0)}, Soul {stats.get('Soul', 0)}"
            ]
        else:
            lines = [
                f"Level: {attr.get('level', 0)}",
                f"Cost: {attr.get('cost', 0)} CP"
            ]
    elif attr.get("key") == "unknown_power":
        # Special handling for Unknown Power attribute
        cp_spent = attr.get("cp_spent", 0)
        gm_points = attr.get("gm_points", 0)
        lines = [
            f"Level: {attr.get('level', 0)}",
            f"Cost: {cp_spent} CP",
            f"Description: Represents hidden or mysterious abilities not known to the character. The GM allocates Attributes equal to CP spent + 50% bonus, which manifest during play.",
            f"Notes: ({gm_points} Points)"
        ]
    else:
        # For all other attributes, show normal display
        lines = [
            f"Level: {attr.get('level', 0)}",
            f"Cost: {attr.get('cost', 0)} CP"
        ]
        
        # Add official description if available
        if "description" in attr and attr["description"]:
            lines.append(f"Description: {attr['description']}")
        
        # Get enhancement counts if available
        enhancement_counts = attr.get("enhancement_counts", {})
        
        # Format enhancements with (E) prefix and counts
        if attr.get('enhancements'):
            enhancement_list = []
            for enh in attr['enhancements']:
                enh_name = enh if isinstance(enh, str) else enh.get("name")
                enh_count = enhancement_counts.get(enh_name, 1)
                enhancement_list.append(f"(E) {enh_name} ({enh_count})")
            lines.append(f"Enhancements: {', '.join(enhancement_list)}")
        
        # Get limiter counts if available
        limiter_counts = attr.get("limiter_counts", {})
        
        # Format limiters with (L) prefix and counts
        if attr.get('limiters'):
            limiter_list = []
            for lim in attr['limiters']:
                lim_name = lim if isinstance(lim, str) else lim.get("name")
                lim_count = limiter_counts.get(lim_name, 1)
                limiter_list.append(f"(L) {lim_name} ({lim_count})")
            lines.append(f"Limiters: {', '.join(limiter_list)}")
            
        # Add tags if any
        if attr.get('custom_fields') and any(attr.get('custom_fields').values()):
            lines.append(f"Tags: {', '.join(attr.get('custom_fields', {}).values())}")
                
        # Add user description if available
        if "user_description" in attr and attr["user_description"]:
            lines.append(f"Notes: {attr['user_description']}")
    
    # Create and return the card widget
    return create_card_widget(
        title=attr.get("name", "Unnamed Attribute"),
        lines=lines,
        on_remove=make_remove_handler(attr["id"]),
        on_click=make_edit_handler(attr["id"]),
        card_type="attribute"
    )
