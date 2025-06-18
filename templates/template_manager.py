import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton,
    QTabWidget, QWidget, QMessageBox, QListWidgetItem
)
from PyQt5.QtCore import Qt

class TemplateDialog(QDialog):
    def __init__(self, parent=None, template_type="race"):
        super().__init__(parent)
        self.parent = parent
        self.template_type = template_type
        self.selected_template = None
        
        # Set window properties
        self.setWindowTitle(f"Select {template_type.title()} Template")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tabs for different template categories
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Load templates
        self.templates = self.load_templates()
        
        # Create a tab for each template category
        self.create_template_tabs()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply Template")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_template)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def load_templates(self):
        """Load templates from JSON files"""
        templates = {"templates": []}
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_path, "data", "templates")

        # Create templates directory if it doesn't exist
        os.makedirs(template_path, exist_ok=True)
    
        # Check for the new directory structure first
        # Main index file contains lists of template names for each category
        main_index_path = os.path.join(template_path, "index.json")
        
        # Handle the singular/plural mismatch
        # The template_type passed to the dialog is singular ("class", "race", "size")
        # But the directory names and index.json keys are plural ("classes", "races", "sizes")
        # Special case for "class" which already ends with 's'
        if self.template_type == "class":
            template_type_plural = "classes"  # Use "classes" instead of "classs"
        else:
            template_type_plural = f"{self.template_type}s"  # Convert to plural
        template_dir = os.path.join(template_path, template_type_plural)
        
        print(f"[DEBUG] Checking for new structure: main_index_path={main_index_path} exists={os.path.exists(main_index_path)}")
        print(f"[DEBUG] Checking for new structure: template_dir={template_dir} exists={os.path.exists(template_dir)}")
        
        # Try to load from the new directory structure with individual files
        if os.path.exists(template_dir) and os.path.exists(main_index_path):
            try:
                # Load the main index file
                print(f"[DEBUG] Loading templates from new structure: {template_dir}")
                with open(main_index_path, 'r') as f:
                    index_data = json.load(f)
                
                # Get the list of template names for the current type
                # We're using the template_type_plural variable defined above
                template_names = index_data.get(template_type_plural, [])
                print(f"[DEBUG] Template type: {self.template_type}, plural: {template_type_plural}, found {len(template_names)} templates in index")
                
                # Process each template file
                loaded_templates = []
                for template_name in template_names:
                    template_file_path = os.path.join(template_dir, f"{template_name}.json")
                    print(f"[DEBUG] Checking template file: {template_file_path}")
                    if os.path.exists(template_file_path):
                        print(f"[DEBUG] Loading template file: {template_file_path}")
                        with open(template_file_path, 'r') as f:
                            template_data = json.load(f)
                            
                            # For size templates, ensure we're getting the proper name
                            # The name field should be properly capitalized
                            if self.template_type == "size":
                                # If there's a specific name field, use it; otherwise use capitalized key
                                name = template_data.get("name")
                                if not name:
                                    # Fallback to capitalizing the filename/key
                                    name = template_name.capitalize()
                                category = "Sizes"
                            elif self.template_type == "race":
                                name = template_data.get("race_name", template_data.get("name", "Unknown Race"))
                                category = "Races"
                            elif self.template_type == "class":
                                name = template_data.get("class_name", template_data.get("name", "Unknown Class"))
                                category = "Classes"
                            else:
                                name = template_data.get("name", "Unknown Template")
                                category = "Templates"
                            
                            # Debug print to check names
                            print(f"[DEBUG] Added template: {name} (from file {template_name}.json)")
                            
                            loaded_templates.append({
                                "name": name,
                                "category": category,
                                "data": template_data
                            })
                
                if loaded_templates:
                    templates["templates"] = loaded_templates
                    print(f"[DEBUG] Returning {len(loaded_templates)} templates from new structure")
                    return templates
                else:
                    print(f"[DEBUG] No templates loaded from new structure")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load templates from directory structure: {e}")
        
        # Only fall back to the old method if the new structure doesn't exist at all
        if not os.path.exists(template_dir) or not os.path.exists(main_index_path):
            print(f"[DEBUG] New structure not found, falling back to old method")
            file_path = os.path.join(template_path, f"{self.template_type}_templates.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                        # Extract templates based on the file structure
                        if self.template_type == "size":
                            # Size templates structure: {"sizeTemplates": {"sizes": [...]}}
                            size_templates = data.get("sizeTemplates", {}).get("sizes", [])
                            templates["templates"] = [{
                                "name": size.get("name", "Unknown Size"),
                                "category": "Sizes",
                                "data": size
                            } for size in size_templates]
                        elif self.template_type == "race":
                            # Race templates structure: direct array of race objects
                            # Support both old format {"raceTemplates": {"races": [...]}} and new format [race1, race2, ...]
                            if isinstance(data, list):
                                race_templates = data  # New format: direct array
                            else:
                                race_templates = data.get("raceTemplates", {}).get("races", [])  # Old format
                            
                            templates["templates"] = [{
                                "name": race.get("race_name", race.get("name", "Unknown Race")),
                                "category": "Races",
                                "data": race
                            } for race in race_templates]
                        elif self.template_type == "class":
                            # Class templates structure: {"classTemplates": {"classes": [...]}}
                            class_templates = data.get("classTemplates", {}).get("classes", [])
                            templates["templates"] = [{
                                "name": cls.get("class_name", cls.get("name", "Unknown Class")),
                                "category": "Classes",
                                "data": cls
                            } for cls in class_templates]
                        else:
                            # Default case - try to load templates directly
                            templates = data
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to load templates: {e}")
            # Don't create empty template files anymore since we're using the new structure
        else:
            # If we get here, it means the new structure exists but no templates were loaded
            # This could happen if the index.json file doesn't have the right keys or if the template files don't exist
            print(f"[DEBUG] New structure exists but no templates were loaded. Check index.json and template files.")
            
        return templates
    
    def create_template_tabs(self):
        """Create tabs for different template categories"""
        # Clear existing tabs
        self.tabs.clear()
        
        # Get templates for the current type
        type_templates = self.templates.get("templates", [])
        
        # Group templates by category
        categories = {}
        for template in type_templates:
            category = template.get("category", "General")
            if category not in categories:
                categories[category] = []
            categories[category].append(template)
        
        # Create a tab for each category
        for category, templates in categories.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            # Create list widget for templates
            list_widget = QListWidget()
            list_widget.setSelectionMode(QListWidget.SingleSelection)
            list_widget.itemClicked.connect(self.on_template_selected)
            
            # Add templates to list
            for template in templates:
                # Get the name, ensuring it's properly displayed
                template_name = template.get("name", "Unnamed Template")
                if self.template_type == "size" and not template_name:
                    # If the name is empty, try to get it from the data
                    template_data = template.get("data", {})
                    template_name = template_data.get("name", "Unknown Size")
                
                # Make sure the name is visible in the dialog
                print(f"[DEBUG] Adding template to list: {template_name}")
                
                item = QListWidgetItem(template_name)
                item.setData(Qt.UserRole, template)
                list_widget.addItem(item)
            
            tab_layout.addWidget(list_widget)
            self.tabs.addTab(tab, category)
        
        # Add "All" tab if there are multiple categories
        if len(categories) > 1:
            all_tab = QWidget()
            all_layout = QVBoxLayout(all_tab)
            
            all_list = QListWidget()
            all_list.setSelectionMode(QListWidget.SingleSelection)
            all_list.itemClicked.connect(self.on_template_selected)
            
            for template in type_templates:
                # Get the name, ensuring it's properly displayed
                template_name = template.get("name", "Unnamed Template")
                if self.template_type == "size" and not template_name:
                    # If the name is empty, try to get it from the data
                    template_data = template.get("data", {})
                    template_name = template_data.get("name", "Unknown Size")
                
                item = QListWidgetItem(template_name)
                item.setData(Qt.UserRole, template)
                all_list.addItem(item)
            
            all_layout.addWidget(all_list)
            self.tabs.insertTab(0, all_tab, "All")
            self.tabs.setCurrentIndex(0)
        
        # If no templates, show message
        if not type_templates:
            no_templates_tab = QWidget()
            no_templates_layout = QVBoxLayout(no_templates_tab)
            no_templates_label = QLabel(f"No {self.template_type} templates found.")
            no_templates_label.setAlignment(Qt.AlignCenter)
            no_templates_layout.addWidget(no_templates_label)
            self.tabs.addTab(no_templates_tab, "No Templates")
    
    def on_template_selected(self, item):
        """Handle template selection"""
        self.selected_template = item.data(Qt.UserRole)
        self.apply_button.setEnabled(True)
    
    def apply_template(self):
        """Apply the selected template to the character"""
        if not self.selected_template:
            return
        
        # Print debug info for the selected template
        template_data = self.selected_template.get("data", {})
        if self.template_type == "size":
            print(f"[DEBUG] Applying size template: {self.selected_template.get('name', 'Unknown Size')}")
            # Make sure the size name is correctly stored in the template data
            if "name" not in template_data and "name" in self.selected_template:
                template_data["name"] = self.selected_template["name"]
        
        # Accept the dialog, returning the selected template
        self.accept()
    
    def get_selected_template(self):
        """Return the selected template"""
        return self.selected_template


def apply_template_to_character(app, template_data, template_type):
    """Apply a template to the character data"""
    if not template_data:
        return False
    
    # Create a unique ID for this template application
    import uuid
    template_id = str(uuid.uuid4())
    
    # Store the template application in the character data
    if "applied_templates" not in app.character_data:
        app.character_data["applied_templates"] = []
    
    # Get the actual template data from the 'data' field
    actual_template = template_data.get("data", template_data)
    
    # Record what this template application changed
    template_changes = {
        "id": template_id,
        "type": template_type,
        "name": actual_template.get("name", "Unnamed Template"),
        "changes": []
    }
    
    # Apply template changes based on type
    if template_type == "size":
        apply_size_template(app, actual_template, template_changes)
    elif template_type == "race":
        apply_race_template(app, actual_template, template_changes)
    elif template_type == "class":
        apply_class_template(app, actual_template, template_changes)
    
    # Add the template changes to the character data
    app.character_data["applied_templates"].append(template_changes)
    
    # Update the UI (but preserve race and class fields)
    current_race = app.race_input.text()
    current_class = app.class_input.text()
    
    # Update points first
    app.update_point_total()
    
    # Update attributes UI only once
    from tabs.attributes_tab import sync_attributes
    sync_attributes(app)
    
    # Update dynamic tabs visibility
    app.update_dynamic_tabs_visibility()
    
    # Restore race and class fields if they were set
    if current_race and current_race.strip():
        app.race_input.setText(current_race)
        app.character_data["race"] = current_race
        
    if current_class and current_class.strip():
        app.class_input.setText(current_class)
        app.character_data["class"] = current_class
    
    return True


def apply_size_template(app, template_data, template_changes):
    """Apply a size template to the character"""
    # Debug print to check template data
    print(f"[DEBUG] Applying size template: {template_data.get('name', 'NO NAME FOUND')}")
    print(f"[DEBUG] Template data keys: {list(template_data.keys())}")
    
    # Update size field - try different ways to get the name
    size_name = template_data.get("name")
    if not size_name and "key" in template_data:
        # Try to get the name from the key by capitalizing it
        size_name = template_data["key"].capitalize()
    
    if size_name:
        old_size = app.size_input.text()
        app.size_input.setText(size_name)
        app.character_data["size"] = size_name
        print(f"[DEBUG] Updated size field to: {size_name}")
        template_changes["changes"].append({
            "field": "size",
            "old_value": old_size,
            "new_value": size_name
        })
    else:
        print(f"[ERROR] Could not find size name in template data")
    
    # Apply stat changes by adding to existing stats
    if "stats" in template_data:
        # Handle new stats structure (object with body_adj, mind_adj, soul_adj)
        if isinstance(template_data["stats"], dict):
            # New format
            stats_dict = template_data["stats"]
            
            # Map the new field names to the old ones
            stat_mapping = {
                "body_adj": "Body",
                "mind_adj": "Mind",
                "soul_adj": "Soul"
            }
            
            for new_field, old_field in stat_mapping.items():
                value = stats_dict.get(new_field, 0)
                if value and old_field in app.stat_spinners:
                    old_value = app.stat_spinners[old_field].value()
                    new_value = old_value + value
                    app.stat_spinners[old_field].setValue(new_value)
                    template_changes["changes"].append({
                        "field": f"stat_{old_field}",
                        "old_value": old_value,
                        "new_value": new_value,
                        "modifier": f"+{value}"  # Record that this was an addition
                    })
        else:
            # Old format - list of stat entries
            for stat_entry in template_data["stats"]:
                stat = stat_entry.get("stat")
                value = stat_entry.get("value")
                if stat in app.stat_spinners:
                    old_value = app.stat_spinners[stat].value()
                    new_value = old_value + value  # Add instead of replace
                    app.stat_spinners[stat].setValue(new_value)
                    template_changes["changes"].append({
                        "field": f"stat_{stat}",
                        "old_value": old_value,
                        "new_value": new_value,
                        "modifier": f"+{value}"  # Record that this was an addition
                    })
    
    # Apply attribute changes
    apply_attributes(app, template_data, template_changes)
    
    # Apply defect changes
    apply_defects(app, template_data, template_changes)


def apply_race_template(app, template_data, template_changes):
    """Apply a race template to the character"""
    # Get the template race name - either from race_name, race field, or the template name
    template_race = template_data.get("race_name", template_data.get("race", template_data.get("name", "")))
    
    if template_race:
        old_race = app.race_input.text()
        
        # If there's already a race, append the new one
        if old_race and old_race.strip():
            new_race = f"{old_race} / {template_race}"
        else:
            new_race = template_race
            
        # Update both the UI and the character data
        app.race_input.setText(new_race)
        app.character_data["race"] = new_race
        
        template_changes["changes"].append({
            "field": "race",
            "old_value": old_race,
            "new_value": new_race
        })
    
    # Check if this race has a specific size template to apply
    if "baseSize" in template_data:
        apply_size_from_template(app, template_data["baseSize"], template_changes)
    
    # Apply stat changes by adding to existing stats
    if "stats" in template_data:
        # Handle new stats structure (object with body_adj, mind_adj, soul_adj)
        if isinstance(template_data["stats"], dict):
            # New format
            stats_dict = template_data["stats"]
            
            # Map the new field names to the old ones
            stat_mapping = {
                "body_adj": "Body",
                "mind_adj": "Mind",
                "soul_adj": "Soul"
            }
            
            for new_field, old_field in stat_mapping.items():
                value = stats_dict.get(new_field, 0)
                if value and old_field in app.stat_spinners:
                    old_value = app.stat_spinners[old_field].value()
                    new_value = old_value + value
                    app.stat_spinners[old_field].setValue(new_value)
                    template_changes["changes"].append({
                        "field": f"stat_{old_field}",
                        "old_value": old_value,
                        "new_value": new_value,
                        "modifier": f"+{value}"  # Record that this was an addition
                    })
        else:
            # Old format - list of stat entries
            for stat_entry in template_data["stats"]:
                stat = stat_entry.get("stat")
                value = stat_entry.get("value")
                if stat in app.stat_spinners:
                    old_value = app.stat_spinners[stat].value()
                    new_value = old_value + value  # Add instead of replace
                    app.stat_spinners[stat].setValue(new_value)
                    template_changes["changes"].append({
                        "field": f"stat_{stat}",
                        "old_value": old_value,
                        "new_value": new_value,
                        "modifier": f"+{value}"  # Record that this was an addition
                    })
    
    # Apply attribute changes
    apply_attributes(app, template_data, template_changes)
    
    # Apply defect changes
    apply_defects(app, template_data, template_changes)


def apply_class_template(app, template_data, template_changes):
    """Apply a class template to the character"""
    # Get the template class name - support both old and new structures
    template_class = template_data.get("class_name", template_data.get("class", template_data.get("name", "")))
    
    if template_class:
        old_class = app.class_input.text()
        
        # If there's already a class, append the new one
        if old_class and old_class.strip():
            new_class = f"{old_class} / {template_class}"
        else:
            new_class = template_class
            
        # Update both the UI and the character data
        app.class_input.setText(new_class)
        app.character_data["class"] = new_class
        
        template_changes["changes"].append({
            "field": "class",
            "old_value": old_class,
            "new_value": new_class
        })
    
    # Check if this class has a specific size template to apply
    if "baseSize" in template_data:
        apply_size_from_template(app, template_data["baseSize"], template_changes)
    
    # Apply attribute changes
    apply_attributes(app, template_data, template_changes)
    
    # Apply defect changes
    apply_defects(app, template_data, template_changes)


def apply_attributes(app, template_data, template_changes):
    """Apply attribute changes from a template with deduplication and provenance tracking"""
    if "attributes" in template_data:
        import copy
        import uuid
        template_id = template_changes.get("id") or template_changes.get("template_id") or template_changes.get("name")
        
        # Track which special attribute tabs need updating
        needs_update = {
            "attributes": False,
            "alternate_forms": False,
            "companions": False,
            "items": False,
            "metamorphosis": False,
            "minions": False
        }
        
        for attr in template_data["attributes"]:
            # Use the attribute name and level from the template
            # Support both old format (name) and new format (custom_name + key)
            attr_name = attr.get("custom_name", attr.get("name", ""))
            attr_key = attr.get("key", "")
            attr_level = attr.get("level", 1)

            # Fetch full attribute details from attributes.json using key if available
            full_attr = None
            if attr_key and attr_key in app.attributes_by_key:
                full_attr = app.attributes_by_key.get(attr_key, {})
            else:
                full_attr = app.attributes.get(attr_name, {})
                
            new_attr = copy.deepcopy(full_attr)
            new_attr["id"] = str(uuid.uuid4())
            new_attr["name"] = attr_name
            new_attr["key"] = attr_key or full_attr.get("key", "")
            new_attr["level"] = attr_level
            
            # Copy additional fields from the template attribute
            if "user_description" in attr and attr["user_description"]:
                new_attr["user_description"] = attr["user_description"]
            if "enhancements" in attr and attr["enhancements"]:
                new_attr["enhancements"] = attr["enhancements"]
            if "limiters" in attr and attr["limiters"]:
                new_attr["limiters"] = attr["limiters"]
            if "options" in attr and attr["options"]:
                new_attr["options"] = attr["options"]
            if "user_input" in attr and attr["user_input"]:
                new_attr["user_input"] = attr["user_input"]
            if "options_source" in attr:
                new_attr["options_source"] = attr["options_source"]

            # Calculate cost if not present
            cost_per_level = new_attr.get("cost_per_level")
            if cost_per_level is None:
                cost_per_level = 0  # Provide a default value if None
            
            # Special handling for Skill Group attribute
            if attr_key == "skill_group" or attr_name == "Skill Group":
                # Get the dynamic cost map (support both legacy and new key names)
                dynamic_cost_map = new_attr.get("dynamic_cost", {}) or new_attr.get("dynamic_cost_map", {})
                # Get the skill group type from user_description or custom fields
                skill_group_type = None
                
                # First check if custom_fields is already set
                if "custom_fields" in attr:
                    cf = attr["custom_fields"]
                    if "skill_group_type" in cf:
                        skill_group_type = cf["skill_group_type"]
                    elif "category" in cf:
                        skill_group_type = cf["category"]
                    # Copy custom fields over
                    new_attr["custom_fields"] = cf
                # If still not found, try to extract from user_description
                elif "user_description" in attr and attr["user_description"]:
                    # Extract the skill group type from the description
                    desc = attr["user_description"]
                    for group_type in dynamic_cost_map.keys():
                        if group_type in desc:
                            skill_group_type = group_type
                            break
                    
                    # If we found a skill group type, store it in custom_fields
                    if skill_group_type:
                        if "custom_fields" not in new_attr:
                            new_attr["custom_fields"] = {}
                        new_attr["custom_fields"]["skill_group_type"] = skill_group_type
                
                # If we found a skill group type, use its cost per level
                if skill_group_type and skill_group_type in dynamic_cost_map:
                    cost_per_level = dynamic_cost_map[skill_group_type]
                    # ensure custom_fields has unified key for later use
                    if "custom_fields" not in new_attr:
                        new_attr["custom_fields"] = {}
                    new_attr["custom_fields"]["skill_group_type"] = skill_group_type
                    # Store the cost_per_level in the attribute for reference
                    new_attr["cost_per_level"] = cost_per_level
                    print(f"DEBUG: Setting Skill Group cost_per_level to {cost_per_level} for type {skill_group_type}")
            
            # Calculate the cost – if we never resolved cost_per_level, fall back to existing cost field or 0
            if cost_per_level == 0 and "cost" in attr and attr["cost"]:
                new_attr["cost"] = attr["cost"]
            else:
                new_attr["cost"] = cost_per_level * attr_level
            
            # Special handling for Unknown Power attribute
            if attr_key == "unknown_power" or attr_name == "Unknown Power":
                import math
                # Set cp_spent equal to the level
                new_attr["cp_spent"] = attr_level
                # Calculate GM points (50% bonus rounded up)
                new_attr["gm_points"] = math.ceil(attr_level * 1.5)
                # Update description
                new_attr["description"] = f"Represents hidden or mysterious abilities not known to the character. The GM allocates Attributes equal to CP spent + 50% bonus, which manifest during play."

            # Deduplication key: name+details
            dedup_key = (new_attr.get("name", "").strip().lower(), str(new_attr.get("details", "")).strip().lower())
            found = False
            for attr_existing in app.character_data.get("attributes", []):
                key_existing = (attr_existing.get("name", "").strip().lower(), str(attr_existing.get("details", "")).strip().lower())
                if dedup_key == key_existing:
                    if "sources" not in attr_existing:
                        attr_existing["sources"] = []
                    if template_id not in attr_existing["sources"]:
                        attr_existing["sources"].append(template_id)
                    found = True
                    break
            if not found:
                new_attr["sources"] = [template_id]
                app.character_data["attributes"].append(new_attr)
                template_changes["changes"].append({
                    "field": "attribute_add",
                    "attribute_id": new_attr["id"],
                    "attribute_data": new_attr
                })
                
                # Mark which special tabs need updating based on attribute type
                needs_update["attributes"] = True
                base_name = new_attr.get("base_name", new_attr["name"])
                needs_update["alternate_forms"] = True  # Always update alternate forms
                
                if base_name in ["Companion", "Companions"]:
                    needs_update["companions"] = True
                elif base_name in ["Item", "Items"]:
                    needs_update["items"] = True
                elif base_name == "Metamorphosis":
                    needs_update["metamorphosis"] = True
                elif base_name == "Minions":
                    needs_update["minions"] = True
        
        # Update all necessary tabs once, after the loop
        if needs_update["attributes"]:
            from tabs.attributes_tab import sync_attributes
            sync_attributes(app)
            
        if needs_update["alternate_forms"]:
            from tabs.alternate_forms_tab import sync_alternate_forms_from_attributes
            sync_alternate_forms_from_attributes(app)
            
        if needs_update["companions"]:
            from tabs.companions_tab import sync_companions_from_attributes
            sync_companions_from_attributes(app)
            
        if needs_update["items"]:
            from tabs.items_tab import sync_items_from_attributes
            sync_items_from_attributes(app)
            
        if needs_update["metamorphosis"]:
            from tabs.metamorphosis_tab import sync_metamorphosis_from_attributes
            sync_metamorphosis_from_attributes(app)
            
        if needs_update["minions"]:
            from tabs.minions_tab import sync_minions_from_attributes
            sync_minions_from_attributes(app)


def apply_defects(app, template_data, template_changes):
    """Apply defect changes from a template with deduplication and provenance tracking, with detailed debugging output."""
    if "defects" in template_data:
        import copy
        import uuid
        template_id = template_changes.get("id") or template_changes.get("template_id") or template_changes.get("name")
        print(f"[DEBUG] Applying defects from template: {template_id}")
        
        # Track if any defects were added
        defects_added = False
        
        for defect in template_data["defects"]:
            # Support both old format (name) and new format (custom_name + key)
            defect_name = defect.get("custom_name", defect.get("name", ""))
            defect_key = defect.get("key", "")
            defect_rank = defect.get("rank", defect.get("level", 1))  # Use rank for defects as per BESM 4e terminology
            
            print(f"[DEBUG] Processing defect: {defect_name} key: {defect_key} rank: {defect_rank}")
            
            # Fetch full defect details from defects.json using key if available
            full_defect = None
            if defect_key and hasattr(app, 'defects_by_key') and defect_key in app.defects_by_key:
                full_defect = app.defects_by_key.get(defect_key, {})
                print(f"[DEBUG] Found full defect by key: {defect_key}")
            elif defect_name and hasattr(app, 'defects') and defect_name in app.defects:
                full_defect = app.defects.get(defect_name, {})
                print(f"[DEBUG] Found full defect by name: {defect_name}")
            else:
                print(f"[DEBUG] Could not find full defect definition for {defect_name} (key: {defect_key})")
                full_defect = {}
            
            # Debug the cp_refund values
            template_cp_refund = defect.get("cp_refund")
            full_defect_cp_refund = full_defect.get("cp_refund") if full_defect else None
            print(f"[DEBUG] CP refund values - Template: {template_cp_refund}, Full defect: {full_defect_cp_refund}")
            
            new_defect = copy.deepcopy(full_defect) if full_defect else copy.deepcopy(defect)
            new_defect["id"] = str(uuid.uuid4())
            new_defect["name"] = defect_name
            new_defect["key"] = defect_key or full_defect.get("key", "")
            new_defect["rank"] = defect_rank  # Use rank for defects as per BESM 4e terminology
            
            # Copy additional fields from the template defect
            if "user_description" in defect and defect["user_description"]:
                new_defect["user_description"] = defect["user_description"]
            if "enhancements" in defect and defect["enhancements"]:
                new_defect["enhancements"] = defect["enhancements"]
            if "limiters" in defect and defect["limiters"]:
                new_defect["limiters"] = defect["limiters"]
            if "options" in defect and defect["options"]:
                new_defect["options"] = defect["options"]
            if "user_input" in defect and defect["user_input"]:
                new_defect["user_input"] = defect["user_input"]
            if "options_source" in defect:
                new_defect["options_source"] = defect["options_source"]
                
            # Preserve cp_refund from full_defect if available (from defects.json)
            # This ensures we use the authoritative CP value from defects.json
            if full_defect and "cp_refund" in full_defect:
                new_defect["cp_refund"] = full_defect["cp_refund"]
                print(f"[DEBUG] Using cp_refund from defects.json: {new_defect['cp_refund']} for defect {new_defect.get('name', 'Unknown')}")
            # Always recalculate the cost based on the current defect data
            # This ensures we use the correct cp_refund value (especially from defects.json)
            if "cp_refund" in new_defect and new_defect["cp_refund"] is not None:
                # cp_refund is positive magnitude, subtract it
                new_defect["cost"] = -abs(new_defect["cp_refund"] * new_defect.get("rank", 1))
                print(f"[DEBUG] Calculated cost from cp_refund: {new_defect['cost']} for defect {new_defect.get('name', 'Unknown')}")
            elif "points" in new_defect and new_defect["points"] is not None:
                # legacy 'points' field treated as cp_refund
                new_defect["cost"] = -abs(new_defect["points"] * new_defect.get("rank", 1))
                print(f"[DEBUG] Calculated cost from points: {new_defect['cost']} for defect {new_defect.get('name', 'Unknown')}")
            elif "rank" in new_defect and "cost_per_rank" in new_defect:
                new_defect["cost"] = -abs(new_defect["rank"] * new_defect["cost_per_rank"])
                print(f"[DEBUG] Calculated cost from cost_per_rank: {new_defect['cost']} for defect {new_defect.get('name', 'Unknown')}")
            # Defects use rank in BESM 4e, not level
            else:
                # default refund per rank
                rank = new_defect.get("rank", 1)
                new_defect["cost"] = -abs(rank)
                print(f"[DEBUG] Warning: No cost info for defect {new_defect.get('name', 'Unknown')}. Using default refund of {new_defect['cost']}.")
            if new_defect.get("name", "").lower() == "unique defect":
                if "details" in new_defect and new_defect["details"]:
                    details_text = new_defect["details"].strip("()").strip()
                    if ":" in details_text:
                        new_defect["name"] = details_text.split(":")[0].strip()
                    elif "÷" in details_text or "-" in details_text:
                        parts = details_text.split(" ")
                        if len(parts) >= 2:
                            new_defect["name"] = " ".join(parts[:-1]).strip()
                    else:
                        new_defect["name"] = details_text
                    if not new_defect.get("details_original"):
                        new_defect["details_original"] = new_defect["details"]
            # Deduplication key: key+name+user_description
            # First try to match by key if available
            dedup_key = new_defect.get("key", "").strip().lower()
            dedup_name = new_defect.get("name", "").strip().lower()
            dedup_desc = str(new_defect.get("user_description", new_defect.get("details", ""))).strip().lower()
            
            print(f"[DEBUG] Defect deduplication key: {dedup_key}, name: {dedup_name}, desc: {dedup_desc}")
            found = False
            if dedup_key:
                for defect_existing in app.character_data.get("defects", []):
                    if dedup_key == defect_existing.get("key", "").strip().lower():
                        print(f"[DEBUG] Found existing defect with matching key: {dedup_key}")
                        if "sources" not in defect_existing:
                            defect_existing["sources"] = []
                        if template_id not in defect_existing["sources"]:
                            defect_existing["sources"].append(template_id)
                        found = True
                        break
            
            # If no match by key, try name+desc
            if not found:
                dedup_key = (dedup_name, dedup_desc)
                for defect_existing in app.character_data.get("defects", []):
                    key_existing = (
                        defect_existing.get("name", "").strip().lower(),
                        str(defect_existing.get("user_description", defect_existing.get("details", ""))).strip().lower()
                    )
                    print(f"[DEBUG] Comparing against existing: {key_existing}")
                    if dedup_key == key_existing:
                        print(f"[DEBUG] Found existing defect, updating sources for: {key_existing}")
                        if "sources" not in defect_existing:
                            defect_existing["sources"] = []
                        if template_id not in defect_existing["sources"]:
                            defect_existing["sources"].append(template_id)
                        found = True
                        break
            
            if not found:
                print(f"[DEBUG] Adding new defect: {dedup_key} with sources [{template_id}]")
                new_defect["sources"] = [template_id]
                app.character_data["defects"].append(new_defect)
                template_changes["changes"].append({
                    "field": "defect_add",
                    "defect_id": new_defect["id"],
                    "defect_data": new_defect
                })
                defects_added = True
                
        # Print debug info about defects
        print(f"[DEBUG] Defects in character after processing:")
        for i, d in enumerate(app.character_data["defects"], 1):
            print(f"[DEBUG] Defect {i}: {d.get('name', '')} (Rank: {d.get('rank', d.get('level', '?'))}), details: {d.get('details', '')}, sources: {d.get('sources', [])}")
        
        # Only sync defects once after all are processed
        if defects_added:
            from tabs.defects_tab import sync_defects
            sync_defects(app)


def apply_size_from_template(app, size_info, template_changes):
    """Apply a size template based on size information from a race or class template"""
    # Get the size name and key
    size_name = size_info.get("name", "")
    size_key = size_info.get("key", "")
    size_rank = size_info.get("size_rank", size_info.get("rank", 0))
    
    print(f"[DEBUG] Applying size from template: name={size_name}, key={size_key}, rank={size_rank}")
    
    if not (size_name or size_key):
        print(f"[DEBUG] No size name or key found in size_info")
        return
    
    # Load the size templates
    import os
    import json
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Try to load from the new directory structure first
    sizes_dir = os.path.join(base_path, "data", "templates", "sizes")
    index_path = os.path.join(base_path, "data", "templates", "index.json")
    
    print(f"[DEBUG] Checking for sizes directory: {sizes_dir}, exists={os.path.exists(sizes_dir)}")
    print(f"[DEBUG] Checking for index file: {index_path}, exists={os.path.exists(index_path)}")
    
    matching_template = None
    
    # Try to find the size template in the new directory structure
    if os.path.exists(sizes_dir) and os.path.exists(index_path):
        try:
            # Load the index file to get the list of size templates
            with open(index_path, 'r') as f:
                index_data = json.load(f)
                size_template_names = index_data.get("sizes", [])
            
            print(f"[DEBUG] Found {len(size_template_names)} size templates in index")
            
            # Try to find a matching size template by key or name
            for size_template_name in size_template_names:
                size_template_path = os.path.join(sizes_dir, f"{size_template_name}.json")
                
                if os.path.exists(size_template_path):
                    with open(size_template_path, 'r') as f:
                        template = json.load(f)
                        
                        # Match by key if available
                        if size_key and template.get("key") == size_key:
                            matching_template = template
                            print(f"[DEBUG] Found matching size template by key: {size_key}")
                            break
                        # Match by name if key not available
                        elif size_name and template.get("name") == size_name:
                            matching_template = template
                            print(f"[DEBUG] Found matching size template by name: {size_name}")
                            break
                        # Match by rank as a last resort
                        elif size_rank is not None and template.get("rank") == size_rank:
                            matching_template = template
                            print(f"[DEBUG] Found matching size template by rank: {size_rank}")
                            break
        except Exception as e:
            print(f"[DEBUG] Error loading size template from new structure: {e}")
    
    # Fall back to the old method if no matching template found
    if matching_template is None:
        print(f"[DEBUG] No matching template found in new structure, trying old structure")
        template_path = os.path.join(base_path, "data", "templates", "size_templates.json")
        
        if not os.path.exists(template_path):
            print(f"[DEBUG] Old size_templates.json not found")
            return
        
        try:
            with open(template_path, 'r') as f:
                data = json.load(f)
                size_templates = data.get("sizeTemplates", {}).get("sizes", [])
                
                # Find the matching size template
                for template in size_templates:
                    # Match by key if available
                    if size_key and template.get("key") == size_key:
                        matching_template = template
                        print(f"[DEBUG] Found matching size template by key in old structure: {size_key}")
                        break
                    # Match by name if key not available
                    elif size_name and template.get("name") == size_name:
                        matching_template = template
                        print(f"[DEBUG] Found matching size template by name in old structure: {size_name}")
                        break
                    # Match by rank as a last resort
                    elif size_rank is not None and template.get("rank") == size_rank:
                        matching_template = template
                        print(f"[DEBUG] Found matching size template by rank in old structure: {size_rank}")
                        break
        except Exception as e:
            print(f"[DEBUG] Error loading size template from old structure: {e}")
    
    # Apply the matching size template if found
    if matching_template:
        # Create a sub-changes list to track size template changes
        size_template_changes = {
            "id": template_changes["id"],
            "type": "size",
            "name": matching_template.get("name", "Unknown Size"),
            "changes": []
        }
        
        # Apply the size template
        apply_size_template(app, matching_template, size_template_changes)
        
        # Add a note about the size template being applied
        template_changes["changes"].append({
            "field": "size_template_applied",
            "size_name": matching_template.get("name", "Unknown Size"),
            "applied_by": template_changes.get("name", "Unknown Template")
        })


def remove_template_from_character(app, template_id):
    """Remove a template from the character"""
    if "applied_templates" not in app.character_data:
        return False
    
    # Find the template application
    template_application = None
    for i, template in enumerate(app.character_data["applied_templates"]):
        if template.get("id") == template_id:
            template_application = template
            app.character_data["applied_templates"].pop(i)
            break
    
    if not template_application:
        return False
    
    # Reverse the changes
    changes = template_application.get("changes", [])
    changes.reverse()  # Process in reverse order
    
    for change in changes:
        field = change.get("field", "")
        
        if field == "size":
            app.size_input.setText(change.get("old_value", ""))
        elif field == "race":
            app.race_input.setText(change.get("old_value", ""))
        elif field == "class":
            app.class_input.setText(change.get("old_value", ""))
        elif field.startswith("stat_"):
            stat = field[5:]  # Remove "stat_" prefix
            if stat in app.stat_spinners:
                app.stat_spinners[stat].setValue(change.get("old_value", 4))
        elif field == "attribute_add":
            # Remove the attribute only if no other template sources remain
            attribute_id = change.get("attribute_id")
            if attribute_id:
                for i, attr in enumerate(app.character_data["attributes"]):
                    if attr.get("id") == attribute_id:
                        # Remove this template from sources
                        sources = attr.get("sources", [])
                        template_id = template_application.get("id") or template_application.get("name")
                        if template_id in sources:
                            sources.remove(template_id)
                        # Remove attribute if no sources left
                        if not sources:
                            app.character_data["attributes"].pop(i)
                        else:
                            attr["sources"] = sources
                        break
        elif field == "defect_add":
            # Remove the defect only if no other template sources remain
            defect_id = change.get("defect_id")
            if defect_id:
                for i, defect in enumerate(app.character_data["defects"]):
                    if defect.get("id") == defect_id:
                        sources = defect.get("sources", [])
                        template_id = template_application.get("id") or template_application.get("name")
                        if template_id in sources:
                            sources.remove(template_id)
                        if not sources:
                            app.character_data["defects"].pop(i)
                        else:
                            defect["sources"] = sources
                        break
    
    # Process any pending events to ensure proper widget cleanup
    from PyQt5.QtWidgets import QApplication
    QApplication.processEvents()
    
    # Update the UI
    app.update_point_total()
    app.load_character_into_ui()
    
    # Sync all tabs
    from tabs.attributes_tab import sync_attributes
    sync_attributes(app)
    
    from tabs.defects_tab import sync_defects
    sync_defects(app)
    
    from tabs.alternate_forms_tab import sync_alternate_forms_from_attributes
    sync_alternate_forms_from_attributes(app)
    
    from tabs.companions_tab import sync_companions_from_attributes
    sync_companions_from_attributes(app)
    
    from tabs.items_tab import sync_items_from_attributes
    sync_items_from_attributes(app)
    
    from tabs.metamorphosis_tab import sync_metamorphosis_from_attributes
    sync_metamorphosis_from_attributes(app)
    
    from tabs.minions_tab import sync_minions_from_attributes
    sync_minions_from_attributes(app)
    
    return True


def show_applied_templates_dialog(app):
    """Show a dialog with all applied templates"""
    dialog = QDialog(app)
    dialog.setWindowTitle("Applied Templates")
    dialog.setMinimumWidth(400)
    dialog.setMinimumHeight(300)
    
    layout = QVBoxLayout(dialog)
    
    # Create list widget for templates
    list_widget = QListWidget()
    list_widget.setSelectionMode(QListWidget.SingleSelection)
    
    # Add templates to list
    if "applied_templates" in app.character_data:
        for template in app.character_data["applied_templates"]:
            item = QListWidgetItem(f"{template.get('name', 'Unnamed')} ({template.get('type', 'unknown').title()})")
            item.setData(Qt.UserRole, template.get("id"))
            list_widget.addItem(item)
    
    layout.addWidget(list_widget)
    
    # Buttons
    button_layout = QHBoxLayout()
    
    remove_button = QPushButton("Remove Template")
    remove_button.setEnabled(False)
    remove_button.clicked.connect(lambda: remove_template(app, list_widget))
    
    close_button = QPushButton("Close")
    close_button.clicked.connect(dialog.accept)
    
    button_layout.addWidget(remove_button)
    button_layout.addWidget(close_button)
    layout.addLayout(button_layout)
    
    # Enable remove button when an item is selected
    list_widget.itemSelectionChanged.connect(
        lambda: remove_button.setEnabled(list_widget.currentItem() is not None)
    )
    
    dialog.exec_()


def remove_template(app, list_widget):
    """Remove the selected template"""
    if not list_widget.currentItem():
        return
    
    template_id = list_widget.currentItem().data(Qt.UserRole)
    if not template_id:
        return
    
    # Confirm removal
    reply = QMessageBox.question(
        app, 
        "Remove Template", 
        "Are you sure you want to remove this template? This will undo all changes made by the template.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        success = remove_template_from_character(app, template_id)
        if success:
            # Remove from list
            list_widget.takeItem(list_widget.currentRow())
            QMessageBox.information(app, "Template Removed", "Template has been removed successfully.")
        else:
            QMessageBox.warning(app, "Error", "Failed to remove template.")
