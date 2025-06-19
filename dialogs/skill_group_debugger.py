import traceback
import functools
import os
import sys
from PyQt5.QtWidgets import QComboBox

# Create a log file in the same directory
log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skill_group_debug.log")

def log_message(message):
    """Write a message to the log file and print it to console"""
    print(f"[DEBUG] {message}")
    with open(log_file_path, "a") as f:
        f.write(f"{message}\n")

def clear_log_file():
    """Clear the log file at the start of a debugging session"""
    with open(log_file_path, "w") as f:
        f.write("Skill Group Debugging Log\n")
        f.write("------------------------\n")

def inspect_combobox(name, combo_box):
    """Inspect a QComboBox and log its state"""
    if combo_box is None:
        log_message(f"{name} is None")
        return
    
    try:
        items = [combo_box.itemText(i) for i in range(combo_box.count())]
        current_text = combo_box.currentText()
        log_message(f"{name} contains {len(items)} items: {items}")
        log_message(f"{name} current text: '{current_text}'")
    except Exception as e:
        log_message(f"Error inspecting {name}: {str(e)}")

def debug_update_skill_group_name(original_method):
    """Decorator to add debugging to _update_skill_group_name"""
    @functools.wraps(original_method)
    def wrapper(self, *args, **kwargs):
        try:
            log_message("\n--- Starting _update_skill_group_name method ---")
            
            # Log custom_name_edited status
            if hasattr(self, '_custom_name_edited'):
                log_message(f"_custom_name_edited = {self._custom_name_edited}")
            else:
                log_message("_custom_name_edited attribute not found")
                
            # Log custom_input_widgets
            log_message(f"custom_input_widgets keys: {list(self.custom_input_widgets.keys())}")
            
            # Inspect category and skill_group_name widgets
            cat_widget = self.custom_input_widgets.get("category")
            name_widget = self.custom_input_widgets.get("skill_group_name")
            
            inspect_combobox("Category widget", cat_widget)
            inspect_combobox("Skill_group_name widget", name_widget)
            
            # Call the original method and time it
            result = original_method(self, *args, **kwargs)
            
            log_message("--- _update_skill_group_name completed successfully ---")
            return result
        except Exception as e:
            log_message(f"*** EXCEPTION in _update_skill_group_name: {str(e)} ***")
            log_message(f"Traceback: {traceback.format_exc()}")
            # Don't re-raise the exception - this will prevent crashes
            return None
    return wrapper

def patch_attribute_builder():
    """Patch the AttributeBuilderDialog class to add debugging"""
    try:
        # Clear the log file at the start
        clear_log_file()
        log_message("Patching AttributeBuilderDialog for debugging")
        
        # Import the dialog module dynamically to avoid circular imports
        # Use the correct filename with hyphen instead of underscore
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "attribute_builder_dialog_CoreGPT", 
            os.path.join(os.path.dirname(__file__), "attribute_builder_dialog-CoreGPT.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        AttributeBuilderDialog = module.AttributeBuilderDialog
        
        # Add update_attribute_info method if it doesn't exist
        if not hasattr(AttributeBuilderDialog, 'update_attribute_info'):
            log_message("Adding missing update_attribute_info method")
            
            # Define the method that will be added
            def update_attribute_info(self):
                """Update attribute information based on current selection."""
                attr_name = self.attr_dropdown.currentText()
                attribute_data = self.attributes.get(attr_name, {})
                log_message(f"Updating attribute info for {attr_name}")
                return None
            
            # Add the method to the class
            AttributeBuilderDialog.update_attribute_info = update_attribute_info
        
        # Make a backup of the original method
        original_method = AttributeBuilderDialog._update_skill_group_name
        
        # Add a safe version of create_custom_field
        original_create_field = AttributeBuilderDialog.create_custom_field
        
        @functools.wraps(original_create_field)
        def safe_create_custom_field(self, field):
            try:
                key = field.get("key", "")
                log_message(f"Creating custom field: {key} ({field.get('field_type', 'unknown')})")
                result = original_create_field(self, field)
                
                # After creating skill group related fields, log their state
                if key == "category" or key == "skill_group_name":
                    widget = self.custom_input_widgets.get(key)
                    inspect_combobox(f"Newly created {key}", widget)
                    
                return result
            except Exception as e:
                log_message(f"*** EXCEPTION in create_custom_field for {field.get('key', 'unknown')}: {str(e)} ***")
                log_message(f"Field details: {field}")
                log_message(f"Traceback: {traceback.format_exc()}")
                # Create a safer fallback widget to prevent crashes
                from PyQt5.QtWidgets import QComboBox
                widget = QComboBox()
                widget.addItem(f"Error creating {field.get('key', 'unknown')} - see log")
                self.custom_input_widgets[field.get("key", "fallback")] = widget
                return widget
        
        # Replace the methods with our debug versions
        AttributeBuilderDialog._update_skill_group_name = debug_update_skill_group_name(original_method)
        AttributeBuilderDialog.create_custom_field = safe_create_custom_field
        
        # Add a fix for Skill Group fields
        def fix_skill_group_fields(self):
            """Ensure the skill_group fields are properly created"""
            log_message("Checking for skill group fields...")
            
            # Check if we have required skill group fields
            if self.attr_dropdown.currentText() == "Skill Group":
                if "category" not in self.custom_input_widgets:
                    log_message("Creating missing 'category' field")
                    widget = QComboBox()
                    widget.addItems([
                        "BACKGROUND - Academic (1 CP/level)",
                        "BACKGROUND - Artistic (1 CP/level)",
                        "BACKGROUND - Domestic (1 CP/level)",
                        "BACKGROUND - Occupation (1 CP/level)",
                        "FIELD - Business (2 CP/level)",
                        "FIELD - Social (2 CP/level)",
                        "FIELD - Street (2 CP/level)",
                        "FIELD - Technical (2 CP/level)",
                        "ACTION - Adventuring (3 CP/level)",
                        "ACTION - Detective (3 CP/level)",
                        "ACTION - Military (3 CP/level)",
                        "ACTION - Scientific (3 CP/level)"
                    ])
                    self.custom_input_widgets["category"] = widget
                
                if "skill_group_name" not in self.custom_input_widgets:
                    log_message("Creating missing 'skill_group_name' field")
                    widget = QComboBox()
                    widget.addItems(["Science", "History", "Engineering", "Medical", "Piloting", 
                                    "Combat", "Stealth", "Performance", "Economics", "Technology"])
                    self.custom_input_widgets["skill_group_name"] = widget
        
        # Check if we can patch the update_attribute_info method
        if hasattr(AttributeBuilderDialog, 'update_attribute_info'):
            # Patch the update_attribute_info method to call our fix
            original_update_info = AttributeBuilderDialog.update_attribute_info
            
            @functools.wraps(original_update_info)
            def safe_update_attribute_info(self):
                try:
                    log_message(f"\n--- Starting update_attribute_info for {self.attr_dropdown.currentText()} ---")
                    result = original_update_info(self)
                    
                    # After updating, check and fix skill group fields if needed
                    if self.attr_dropdown.currentText() == "Skill Group":
                        fix_skill_group_fields(self)
                        
                    log_message("--- update_attribute_info completed successfully ---")
                    return result
                except Exception as e:
                    log_message(f"*** EXCEPTION in update_attribute_info: {str(e)} ***")
                    log_message(f"Traceback: {traceback.format_exc()}")
                    # Don't re-raise the exception
                    return None
                    
            # Replace the update_attribute_info method
            AttributeBuilderDialog.update_attribute_info = safe_update_attribute_info
            
        # Alternative - patch the _set_dynamic_custom_name method which is called when attribute is changed
        if hasattr(AttributeBuilderDialog, '_set_dynamic_custom_name'):
            original_set_dynamic = AttributeBuilderDialog._set_dynamic_custom_name
            
            @functools.wraps(original_set_dynamic)
            def safe_set_dynamic_custom_name(self, attr_name):
                try:
                    log_message(f"\n--- Setting dynamic name for {attr_name} ---")
                    result = original_set_dynamic(self, attr_name)
                    
                    # Check and fix skill group fields if needed
                    if attr_name == "Skill Group":
                        fix_skill_group_fields(self)
                        
                    log_message("--- _set_dynamic_custom_name completed successfully ---")
                    return result
                except Exception as e:
                    log_message(f"*** EXCEPTION in _set_dynamic_custom_name: {str(e)} ***")
                    log_message(f"Traceback: {traceback.format_exc()}")
                    # Don't re-raise the exception
                    return None
            
            # Replace the method
            AttributeBuilderDialog._set_dynamic_custom_name = safe_set_dynamic_custom_name
        
        log_message("AttributeBuilderDialog successfully patched")
        return True
    except Exception as e:
        log_message(f"Failed to patch AttributeBuilderDialog: {str(e)}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return False

# This will be imported by besm_app.py
patch_successful = patch_attribute_builder()
