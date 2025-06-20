import sys
import os
import json
import math
import uuid

# --- Resource path helper for PyInstaller ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

from tools.utils import (
    ClickableCard, create_card_widget, generate_auto_name,
    apply_text_shadow, cell, load_json_file
)
from tools.pdf_export import export_character_to_pdf
from tools.widgets import ClickableCard, AttributeListWidget, LabeledRowWithHelp
import common_ui as ui
from dialogs.attribute_builder_dialog import AttributeBuilderDialog
from dialogs.defect_builder_dialog import DefectBuilderDialog

from tabs.alternate_forms_tab import (
    init_alternate_forms_tab,
    sync_alternate_forms_from_attributes,
    clear_alternate_form_ui,
    populate_alternate_form_ui
)

from tabs.attributes_tab import init_attributes_tab

from tabs import (
    init_stats_tab,
    init_items_tab,
    init_alternate_forms_tab,
    init_metamorphosis_tab,
    init_companions_tab,
    init_minions_tab,
)

from tabs.items_tab import init_items_tab

from PyQt5.QtWidgets import (
    QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QPushButton, QToolButton, QTabWidget, QWidget, QGridLayout,
    QMainWindow, QMessageBox, QFileDialog, QStatusBar, QDialog
)
from PyQt5.QtCore import QSettings, Qt

from tools.data_migrations import DataMigrator
from tools.backup_manager import BackupManager
from dialogs.backup_dialog import BackupDialog
from tabs.data_management_tab import init_data_management_tab

class BESMCharacterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BESM Character Generator")
        
        # Initialize settings
        self.settings = QSettings("LegendMasters", "BESM Character Generator")
        
        # Initialize backup manager
        self.backup_manager = BackupManager(self)
        
        # Load attributes from JSON
        base_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_path, "data", "attributes.json")) as f:
            self.attributes_data = json.load(f)
        
        # Load defects from JSON
        with open(os.path.join(base_path, "data", "defects.json")) as f:
            defects_list = json.load(f)["defects"]
            self.defects = {defect["name"]: defect for defect in defects_list}
            # Create a dictionary indexed by key for faster lookups
            self.defects_by_key = {defect["key"]: defect for defect in defects_list if "key" in defect}
        
        # Initialize character data
        self.character_data = {
            "name": "",
            "stats": {},
            "attributes": [],
            "defects": [],
            "items": [],
            "skills": [],
            "derived_values": {},
            "notes": ""
        }
        
        # Initialize attributes dictionaries for template management
        self.attributes = {}
        self.attributes_by_key = {}
        with open(os.path.join(base_path, "data", "attributes.json")) as f:
            attributes_data = json.load(f)
            for attr in attributes_data.get("attributes", []):
                self.attributes[attr["name"]] = attr
                if "key" in attr:
                    self.attributes_by_key[attr["key"]] = attr
        
        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Initialize all tabs
        # Create a layout for the attributes tab
        attributes_tab_layout = QVBoxLayout()
        init_attributes_tab(self, attributes_tab_layout)

        # Create a QWidget for the attributes tab and set its layout
        attributes_tab_widget = QWidget()
        attributes_tab_widget.setLayout(attributes_tab_layout)

        # Add the attributes tab to the QTabWidget
        self.tabs.addTab(attributes_tab_widget, "Attributes")
        self.init_defects_tab()
        init_items_tab(self)
        # Replace non-existent init_skills_tab() and init_notes_tab() with placeholders
        # self.init_skills_tab()  # Not implemented yet
        # self.init_notes_tab()   # Not implemented yet
        init_data_management_tab(self)  # Initialize the new data management tab
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Create menu bar
        self.init_menu_bar()
        
        # Set window properties
        self.setGeometry(100, 100, 800, 1200)
        
        # Initialize data migrator
        self.data_migrator = DataMigrator()
        
        # Load last folder or default to ./characters
        self.last_directory = self.settings.value("last_directory", os.path.join(base_path, "characters"))
        os.makedirs(self.last_directory, exist_ok=True)
        self.menuBar().setVisible(False)
        self.setMinimumSize(1200, 600)
        main_layout = ui.QHBoxLayout()
        container = ui.QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Sidebar
        sidebar = ui.QVBoxLayout()

        # Add logo (optional)
        logo = ui.QLabel()
        logo.setPixmap(ui.QPixmap(resource_path("project-logo.jpg")).scaledToWidth(150, ui.Qt.SmoothTransformation))
        logo.setAlignment(ui.Qt.AlignCenter)
        sidebar.addWidget(logo)

        # Add file operations buttons
        btn_new = ui.QPushButton("New Character")
        btn_load = ui.QPushButton("Load Character")
        btn_save = ui.QPushButton("Save Character")
        btn_export = ui.QPushButton("Export to PDF")
        btn_options = ui.QToolButton()
        btn_options.setText("Options")
        btn_options.setPopupMode(ui.QToolButton.InstantPopup)

        for btn in [btn_new, btn_load, btn_save, btn_export, btn_options]:
            btn.setSizePolicy(ui.QSizePolicy.Expanding, ui.QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton, QToolButton {
                    background-color: transparent;
                    color: #ff5aa9;
                    font-family: "Comic Sans MS";
                    font-size: 18px;
                    font-weight: bold;
                    border: none;
                    padding: 8px;
                }
                QPushButton:hover, QToolButton::menu-indicator {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)

        # Style and add
        for btn in [btn_new, btn_load, btn_save, btn_export, btn_options]:
            btn.setSizePolicy(ui.QSizePolicy.Expanding, ui.QSizePolicy.Fixed)
            sidebar.addWidget(btn)
            
        # Add template section header
        template_header = ui.QLabel("Templates")
        template_header.setAlignment(ui.Qt.AlignCenter)
        template_header.setStyleSheet("""
            QLabel {
                color: #ff5aa9;
                font-family: "Comic Sans MS";
                font-size: 16px;
                font-weight: bold;
                margin-top: 15px;
                margin-bottom: 5px;
            }
        """)
        sidebar.addWidget(template_header)
        
        # Add template buttons
        btn_size_template = ui.QPushButton("Size Templates")
        btn_race_template = ui.QPushButton("Race Templates")
        btn_class_template = ui.QPushButton("Class Templates")
        btn_manage_templates = ui.QPushButton("Manage Templates")
        btn_library_manager = ui.QPushButton("Library Manager")
        
        # Connect template buttons
        btn_size_template.clicked.connect(lambda: self.open_template_dialog("size"))
        btn_race_template.clicked.connect(lambda: self.open_template_dialog("race"))
        btn_class_template.clicked.connect(lambda: self.open_template_dialog("class"))
        btn_manage_templates.clicked.connect(self.manage_templates)
        btn_library_manager.clicked.connect(self.open_library_manager)
        
        # Style template buttons
        for btn in [btn_size_template, btn_race_template, btn_class_template, btn_manage_templates, btn_library_manager]:
            btn.setSizePolicy(ui.QSizePolicy.Expanding, ui.QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #5acdff;
                    font-family: "Comic Sans MS";
                    font-size: 14px;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
            sidebar.addWidget(btn)

        sidebar.addStretch()  # Push content to top

        # Wrap in a widget
        sidebar_widget = ui.QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(180)
        main_layout.addWidget(sidebar_widget)

        # Define this BEFORE using it
        self.extra_stats_enabled = {
            "Shock Value": True,
            "Sanity Points": True,
            "Social Combat Value": True,
            "Society Points": True,
        }

        options_menu = ui.QMenu(self)
        btn_options.setMenu(options_menu)

        self.extra_stat_actions = {}
        for stat_name in self.extra_stats_enabled:
            action = options_menu.addAction(stat_name)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(lambda checked, name=stat_name: self.toggle_extra_stat(name, checked))
            self.extra_stat_actions[stat_name] = action

        self.central_widget = ui.QWidget()
        main_content_layout = ui.QVBoxLayout()
        self.central_widget.setLayout(main_content_layout)
        main_layout.addWidget(self.central_widget)  # Add main content to right side

        # Create a layout for attribute cards
        self.attr_table_layout = ui.QVBoxLayout()
        self.attr_table_container = ui.QWidget()
        self.attr_table_container.setLayout(self.attr_table_layout)

        # Add the attribute card container to the main content layout
        main_content_layout.addWidget(self.attr_table_container)

        # Create a layout for defect cards
        self.defect_list_layout = ui.QVBoxLayout()
        self.defect_list_container = ui.QWidget()
        self.defect_list_container.setLayout(self.defect_list_layout)

        # Add the defect card container to the main content layout
        main_content_layout.addWidget(self.defect_list_container)

        # Connect buttons
        btn_new.clicked.connect(self.create_new_character)
        btn_load.clicked.connect(self.load_character)
        btn_save.clicked.connect(self.save_character)
        btn_export.clicked.connect(self.export_to_pdf)
        # Options menu is not yet implemented
        options_menu = ui.QMenu()
        options_menu.addAction("Settings", lambda: ui.QMessageBox.information(self, "Settings", "Settings dialog not yet implemented."))
        options_menu.addAction("About", lambda: ui.QMessageBox.information(self, "About", "BESM 4e Character Generator\nVersion 0.1\n\nCreated for Legendmasters"))
        btn_options.setMenu(options_menu)

        # --- Apply to all ui.QLabel widgets ---
        for label in self.findChildren(ui.QLabel):
            apply_text_shadow(label)

        # --- Apply to sidebar buttons ---
        for btn in [btn_new, btn_load, btn_save, btn_export, btn_options]:
            apply_text_shadow(btn)

        self.character_data = {
            "version": self.data_migrator.current_version,
            "name": "",
            "player": "",
            "gm": "",
            "race": "",
            "class": "",
            "homeworld": "",
            "size": "",
            "background": {
                "origin": "",
                "faction": "",
                "goals": "",
                "personality": "",
                "history": ""
            },
            "stats": {
                "Body": 0,
                "Mind": 0,
                "Soul": 0
            },
            "derived": {
                "CV": 0,
                "ACV": 0,
                "DCV": 0,
                "HP": 0,
                "EP": 0,
                "DM": 0,
                "SV": 0,
                "SP": 0,
                "SCV": 0,
                "SOP": 0
            },
            "drama_points": {
                "current": 3,
                "max": 5
            },
            "attributes": [],
            "defects": [],
            "skills": [],
            "weapons": [],
            "armor": [],
            "items": [],
            "techniques": [],
            "templates": [],
            "alternate_forms": [
                # Each entry will be something like:
                # {
                #   "name": "Wolf Form",
                #   "level": 3,
                #   "cp_budget": 15,
                #   "stats": { "Body": 4, "Mind": 3, "Soul": 4 },
                #   "derived": {...},
                #   "attributes": [...],
                #   "defects": [...]
                # }
            ],
            "metamorphosis": [],
            "companions": [],
            "minions": [],
            "relationships": [],
            "notes": "",
            "custom_fields": {},
            "custom_rules": [],
            "saved_loadouts": [],
            "benchmark": None,
            "totalPoints": 0
        }

        self.benchmarks = self.load_benchmarks(os.path.join("data", "benchmarks.json"))
        if not self.benchmarks:
            print("[WARNING] No benchmarks loaded! Check data/benchmarks.json.")
        self.selected_benchmark = None
        self.user_selected_benchmark = None # Start as None to mean "not initialized"

        # Character Points Summary
        points_layout = ui.QGridLayout()

        self.starting_cp_input = ui.QSpinBox()
        self.starting_cp_input.setRange(0, 9999)
        self.starting_cp_input.setValue(0)
        self.starting_cp_input.valueChanged.connect(self.update_point_total)

        self.earned_cp_input = ui.QSpinBox()
        self.earned_cp_input.setRange(0, 9999)
        self.earned_cp_input.setValue(0)
        self.earned_cp_input.valueChanged.connect(self.update_point_total)

        self.spent_cp_display = ui.QLabel("0")
        self.spent_cp_display.setObjectName("spentCpDisplay")
        self.spent_cp_display.setAlignment(ui.Qt.AlignCenter)

        self.unspent_cp_display = ui.QLabel("0")
        self.unspent_cp_display.setObjectName("unspentCpDisplay")
        self.unspent_cp_display.setAlignment(ui.Qt.AlignCenter)

        points_layout.addWidget(ui.QLabel("Starting CP:"), 0, 0)
        points_layout.addWidget(self.starting_cp_input, 0, 1)
        points_layout.addWidget(ui.QLabel("Earned CP:"), 0, 2)
        points_layout.addWidget(self.earned_cp_input, 0, 3)
        points_layout.addWidget(ui.QLabel("Spent CP:"), 1, 0)
        points_layout.addWidget(self.spent_cp_display, 1, 1)
        points_layout.addWidget(ui.QLabel("Unspent CP:"), 1, 2)
        points_layout.addWidget(self.unspent_cp_display, 1, 3)

        main_content_layout.addLayout(points_layout)

        self.benchmark_dropdown = ui.QComboBox()
        self.benchmark_dropdown.addItem("No Benchmark", userData="No Benchmark")
        for b in self.benchmarks:
            range_min, range_max = b["point_range"]
            if range_max is None:
                range_str = f"{range_min}+ CP"
            else:
                range_str = f"{range_min}–{range_max} CP"
            label = f"{b['name']} ({range_str})"
            self.benchmark_dropdown.addItem(label, userData=b["name"])
        
        self.benchmark_dropdown.currentTextChanged.connect(self.set_benchmark)
        main_content_layout.addWidget(self.benchmark_dropdown)

        # Suggestion label that appears below the benchmark dropdown
        self.suggestion_label = ui.QLabel("DEBUG: Suggested Benchmark Label")
        self.suggestion_label.setAlignment(ui.Qt.AlignCenter)
        self.suggestion_label.setObjectName("suggestionLabel")  # Style is defined in style.qss
        
        # Force very obvious styling for debugging
        self.suggestion_label.setStyleSheet("""
            background-color: transparent;
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        
        # Make it clickable
        self.suggestion_label.setCursor(ui.Qt.PointingHandCursor)
        self.suggestion_label.mousePressEvent = self.on_suggestion_clicked
        
        # Add directly to the main layout
        main_content_layout.addWidget(self.suggestion_label)

        self.tabs = ui.QTabWidget()
        # Set tab properties to ensure longer tab names aren't cut off
        self.tabs.setTabsClosable(False)
        self.tabs.setMovable(False)
        self.tabs.setElideMode(ui.Qt.ElideNone)  # Prevent text elision (cutting off)
        self.tabs.setUsesScrollButtons(True)    # Enable scroll buttons for many tabs
        self.tabs.setDocumentMode(True)         # More compact look
        
        # Set explicit tab size policy to prevent text truncation
        self.tabs.tabBar().setExpanding(False)  # Don't expand tabs to fill width
        self.tabs.tabBar().setMinimumWidth(200) # Ensure minimum width for tab bar
        main_content_layout.addWidget(self.tabs)

        init_stats_tab(self)
        init_items_tab(self)
        init_alternate_forms_tab(self)
        init_metamorphosis_tab(self)
        init_companions_tab(self)
        init_minions_tab(self)

        # Calculate initial derived values
        self.update_derived_values()

        # Initialize the attributes tab layout
        self.attributes_tab_layout = ui.QVBoxLayout()
        self.attributes_tab_layout.setContentsMargins(8, 8, 8, 8)
        self.attributes_tab_layout.setSpacing(10)

        # Create a scrollable area for the cards
        self.attributes_scroll_area = QScrollArea()
        self.attributes_scroll_area.setWidgetResizable(True)
        self.attributes_scroll_container = ui.QWidget()
        self.attributes_scroll_layout = ui.QVBoxLayout()
        self.attributes_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.attributes_scroll_layout.setSpacing(10)
        self.attributes_scroll_layout.setAlignment(ui.Qt.AlignTop)  # Ensure cards align to the top
        self.attributes_scroll_container.setLayout(self.attributes_scroll_layout)
        self.attributes_scroll_area.setWidget(self.attributes_scroll_container)

        # Add the scrollable area to the attributes tab layout
        self.attributes_tab_layout.addWidget(self.attributes_scroll_area)

        # Add the "Add Attribute" button fixed at the bottom
        self.add_attribute_button = ui.QPushButton("Add Attribute")
        self.add_attribute_button.clicked.connect(self.add_attribute)
        self.add_attribute_button.setSizePolicy(ui.QSizePolicy.Expanding, ui.QSizePolicy.Fixed)
        self.attributes_tab_layout.addWidget(self.add_attribute_button)

        # Create the attributes tab container and set its layout
        self.attributes_tab_container = ui.QWidget()
        self.attributes_tab_container.setLayout(self.attributes_tab_layout)

        # Add the attributes tab directly after the stats tab
        self.tabs.insertTab(1, self.attributes_tab_container, "Attributes")

        # Initialize the defects tab directly
        self.init_defects_tab()

        self.dynamic_tabs = {
            "Alternate Form": {
                "tab": self.alternate_forms_tab,
                "index": -1
            },
            "Items": {
                "tab": self.items_tab,
                "index": -1
            },
            "Metamorphosis": {
                "tab": self.metamorphosis_tab,
                "index": -1
            },
            "Companions": {
                "tab": self.companions_tab,
                "index": -1
            },
            "Minions": {
                "tab": self.minions_tab,
                "index": -1
            }
        }

        self.update_dynamic_tabs_visibility()

        self.suggested_benchmark_name = None
        self.user_selected_benchmark = False
        self.update_point_total()

        # Character Info Layout
        info_grid = ui.QGridLayout()

        # Text fields for character metadata
        self.char_name_input = ui.QLineEdit()
        self.player_name_input = ui.QLineEdit()
        self.gm_name_input = ui.QLineEdit()
        self.race_input = ui.QLineEdit()
        self.class_input = ui.QLineEdit()
        self.homeworld_input = ui.QLineEdit()
        self.size_input = ui.QLineEdit()

        # Hide them all at start
        for info in self.dynamic_tabs.values():
            self.tabs.removeTab(info["index"])

        # Row 0
        info_grid.addWidget(ui.QLabel("Character Name:"), 0, 0)
        info_grid.addWidget(self.char_name_input, 0, 1)
        info_grid.addWidget(ui.QLabel("Player Name:"), 0, 2)
        info_grid.addWidget(self.player_name_input, 0, 3)

        # Row 1
        info_grid.addWidget(ui.QLabel("Game Master Name:"), 1, 0)
        info_grid.addWidget(self.gm_name_input, 1, 1)
        info_grid.addWidget(ui.QLabel("Race / Species:"), 1, 2)
        info_grid.addWidget(self.race_input, 1, 3)

        # Row 2
        info_grid.addWidget(ui.QLabel("Class / Occupation:"), 2, 0)
        info_grid.addWidget(self.class_input, 2, 1)
        info_grid.addWidget(ui.QLabel("Home World / Habitat:"), 2, 2)
        info_grid.addWidget(self.homeworld_input, 2, 3)

        # Row 3
        info_grid.addWidget(ui.QLabel("Size / Height / Weight / Gender:"), 3, 0)
        info_grid.addWidget(self.size_input, 3, 1, 1, 3)

        main_content_layout.addLayout(info_grid)

        self.last_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "characters")
        os.makedirs(self.last_directory, exist_ok=True)

    def add_labeled_row_with_help(self, layout, label_text, widget, help_text):
        row_layout = ui.QHBoxLayout()
        row_label = ui.QLabel(label_text)
        row_label.setFixedWidth(150)

        help_icon = ui.QLabel("❓")
        help_icon.setToolTip(help_text)
        help_icon.setStyleSheet("color: gray; font-weight: bold;")
        help_icon.setFixedWidth(20)
        help_icon.setAlignment(ui.Qt.AlignCenter)

        row_layout.addWidget(row_label)
        row_layout.addWidget(help_icon)
        row_layout.addWidget(widget)
        
        # Add the row layout to the form layout
        layout.addRow(row_layout)

        # Store the row layout in a dict so we can hide it later
        return data["benchmarks"]
    
    def add_attribute(self):
        """Open the attribute builder dialog to add a new attribute"""
        dialog = AttributeBuilderDialog(self)
        if dialog.exec_() == ui.QDialog.Accepted:
            print("Dialog accepted, getting attribute data...")
            attr = dialog.get_attribute_data()
            print(f"Attribute data: {attr}")
            
            # Check if this is a special type that should use the library
            base_name = attr.get("base_name", attr.get("name", ""))
            
            # For special types, show selector dialog first
            library_type = None
            if base_name == "Item":
                library_type = "items"
            elif base_name in ["Companion", "Companions"]:
                library_type = "companions"
            elif base_name == "Minions":
                library_type = "minions"
            elif base_name == "Metamorphosis":
                library_type = "metamorphosis"
            elif base_name == "Alternate Form":
                library_type = "alternate_forms"
            elif base_name == "Unknown Power":
                library_type = "unknown_power"
                
            # If this is a special attribute type, show the library selector
            if library_type:
                self.handle_special_attribute(attr, library_type)
            else:
                # Regular attribute - add directly
                self._add_attribute_to_character(attr)
    
    def handle_special_attribute(self, attr, library_type):
        """Handle special attribute types that can use the library"""
        if library_type == "unknown_power":
            # Unknown Power uses its own manager dialog for the GM
            self._add_attribute_to_character(attr)  # Add first so it appears in data/UI
            self.open_unknown_power_manager(attr)
        else:
            # Other special attributes use their respective editors
            self._add_attribute_to_character(attr)
            self._open_special_editor_for_new_attribute(attr, library_type)
    
    def open_unknown_power_manager(self, attr):
        """Open the Unknown Power manager dialog for the GM"""
        from dialogs.unknown_power_dialog import UnknownPowerDialog
        dialog = UnknownPowerDialog(self, attr)
        if dialog.exec_():
            # Update the character sheet to reflect any changes
            from tabs.attributes_tab import sync_attributes
            sync_attributes(self)  # Refresh the attributes tab UI
            self.update_derived_values()
            self.update_point_total()

    def _add_attribute_to_character(self, attr):
        """Add an attribute to the character data"""
        # Ensure attributes list exists
        if "attributes" not in self.character_data:
            self.character_data["attributes"] = []
            
        # Add a unique ID to the attribute if it doesn't have one
        if "id" not in attr:
            attr["id"] = str(uuid.uuid4())

        # Special handling for Unknown Power attribute: calculate GM bonus points
        if attr.get("key") == "unknown_power" or attr.get("name") == "Unknown Power":
            import math
            cp_spent = attr.get("cp_spent", attr.get("level", 0))
            attr["cp_spent"] = cp_spent
            attr["cost"] = cp_spent  # Cost equals points spent by the player
            gm_points = math.ceil(cp_spent * 1.5)  # GM receives 50% bonus, rounded up
            attr["gm_points"] = gm_points
            attr["description"] = (
                f"GM has {gm_points} points to assign to hidden attributes revealed during play."
            )
            # Ensure a hidden_attributes list exists on the character
            self.character_data.setdefault("hidden_attributes", [])
            
        # Add the attribute to character data
        self.character_data["attributes"].append(attr)
        print(f"Attributes in character data: {len(self.character_data['attributes'])}")
        
        # Update the attributes tab UI
        from tabs.attributes_tab import sync_attributes
        sync_attributes(self)
        
        # Sync all special attribute tabs based on the attribute type
        base_name = attr.get("base_name", attr["name"])
        
        # Always sync alternate forms
        sync_alternate_forms_from_attributes(self)
        
        # Sync specific tabs based on attribute type
        if base_name in ["Companion", "Companions"]:
            from tabs.companions_tab import sync_companions_from_attributes
            sync_companions_from_attributes(self)
        elif base_name in ["Item", "Items"]:
            from tabs.items_tab import sync_items_from_attributes
            sync_items_from_attributes(self)
        elif base_name == "Metamorphosis":
            from tabs.metamorphosis_tab import sync_metamorphosis_from_attributes
            sync_metamorphosis_from_attributes(self)
        elif base_name == "Minions":
            from tabs.minions_tab import sync_minions_from_attributes
            sync_minions_from_attributes(self)
            
        # Update dynamic tabs visibility
        self.update_dynamic_tabs_visibility()
    
    def _open_special_editor_for_new_attribute(self, attr, library_type):
        """Open the appropriate editor for the newly created special attribute"""
        attr_id = attr.get("id")
        if not attr_id:
            return
            
        if library_type == "items":
            self.edit_item(attr_id)
        elif library_type == "companions":
            self.edit_companion(attr_id)
        elif library_type == "minions":
            self.edit_minion(attr_id)
        elif library_type == "metamorphosis":
            self.edit_metamorphosis(attr_id)
        elif library_type == "alternate_forms":
            self.edit_alternate_form(attr_id)
    
    def _associate_library_object_with_attribute(self, attr, library_obj, library_type):
        """Associate a library object with a newly created attribute"""
        # Find the attribute in character data
        attr_id = attr.get("id")
        if not attr_id:
            return
            
        for i, a in enumerate(self.character_data["attributes"]):
            if a.get("id") == attr_id:
                # Update attribute properties based on library object
                a["name"] = library_obj.get("name", a["name"])
                if "level" in library_obj:
                    a["level"] = library_obj["level"]
                if "cost" in library_obj:
                    a["cost"] = library_obj["cost"]
                if "description" in library_obj:
                    a["description"] = library_obj["description"]
                    
                # Save reference to library object
                a["library_ref"] = {
                    "type": library_type,
                    "id": library_obj.get("id")
                }
                
                # Update UI and associated special data
                if library_type == "items":
                    # Add item to character's items
                    if "id" not in library_obj:
                        library_obj["id"] = attr_id
                    self.character_data["items"].append(library_obj)
                    from tabs.items_tab import sync_items_from_attributes
                    sync_items_from_attributes(self)
                    
                elif library_type == "companions":
                    # Add companion to character's companions
                    if "id" not in library_obj:
                        library_obj["id"] = attr_id
                    self.character_data["companions"].append(library_obj)
                    from tabs.companions_tab import sync_companions_from_attributes
                    sync_companions_from_attributes(self)
                    
                elif library_type == "minions":
                    # Add minion to character's minions
                    if "id" not in library_obj:
                        library_obj["id"] = attr_id
                    self.character_data["minions"].append(library_obj)
                    from tabs.minions_tab import sync_minions_from_attributes
                    sync_minions_from_attributes(self)
                    
                elif library_type == "metamorphosis":
                    # Add metamorphosis to character's metamorphosis
                    if "id" not in library_obj:
                        library_obj["id"] = attr_id
                    self.character_data["metamorphosis"].append(library_obj)
                    from tabs.metamorphosis_tab import sync_metamorphosis_from_attributes
                    sync_metamorphosis_from_attributes(self)
                    
                elif library_type == "alternate_forms":
                    # Add alternate form to character's alternate forms
                    if "id" not in library_obj:
                        library_obj["id"] = attr_id
                    self.character_data["alternate_forms"].append(library_obj)
                    sync_alternate_forms_from_attributes(self)
                
                # Update UI
                from tabs.attributes_tab import sync_attributes
                sync_attributes(self)
                
                # Update dynamic tabs visibility
                self.update_dynamic_tabs_visibility()
                
                # Update point totals
                self.update_point_total()
                
                break
    
    def load_benchmarks(self, file_path):
        """
        Load benchmark data from a JSON file
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Extract the benchmarks array from the JSON structure
                    return data.get("benchmarks", [])
            else:
                print(f"Benchmark file not found: {file_path}")
                return []
        except Exception as e:
            ui.QMessageBox.warning(self, "Error", f"Failed to load benchmark data: {e}")
            return []
            
    def init_defects_tab(self):
        # Create a container for the defects tab
        self.defects_tab_container = ui.QWidget()
        self.defects_tab_layout = ui.QVBoxLayout(self.defects_tab_container)
        self.defects_tab_layout.setContentsMargins(8, 8, 8, 8)
        self.defects_tab_layout.setSpacing(10)
        
        # Initialize the defects tab using the function from tabs/defects_tab.py
        from tabs.defects_tab import init_defects_tab
        init_defects_tab(self, self.defects_tab_layout)
        
        # Add the "Add Defect" button
        add_button = ui.QPushButton("Add Defect")
        add_button.clicked.connect(self.add_defect)
        add_button.setSizePolicy(ui.QSizePolicy.Expanding, ui.QSizePolicy.Fixed)
        self.defects_tab_layout.addWidget(add_button)
        
        # Add the tab to the main tabs
        self.tabs.addTab(self.defects_tab_container, "Defects")

    def add_weapon(self):
        self.character_data["weapons"].append({"name": "New Weapon", "damage": "10", "cost": 1})
        self.weapon_list.addItem("New Weapon - 10 dmg - 1 CP")
        self.update_point_total()

    def add_item(self):
        # You can expand this later to open a dialog or load from JSON
        item = {"name": "New Item", "description": "Describe the item here.", "cost": 0}
        self.character_data["items"].append(item)
        self.items_list.addItem(f"{item['name']} - {item['description']} - {item['cost']} CP")
        self.update_point_total()

    def add_metamorphosis(self):
        # Basic placeholder until a dialog is added
        entry = {"name": "New Metamorphosis", "description": "Transformative state", "cp": 0}
        self.character_data["metamorphosis"].append(entry)
        self.metamorphosis_list.addItem(f"{entry['name']} - {entry['description']} - {entry['cp']} CP")
        self.update_point_total()

    def add_alternate_form(self):
        # Simple placeholder for alternate form
        form = {
            "id": str(uuid.uuid4()),
            "name": "New Alternate Form",
            "description": "Alternate appearance",
            "cp": 0
        }
        self.character_data["alternate_forms"].append(form)
        self.alternate_forms_list.addItem(f"{form['name']} - {form['description']} - {form['cp']} CP")
        self.update_point_total()

    def add_companion(self):
        # First, add the Companion attribute to the character
        from dialogs.attribute_builder_dialog import AttributeBuilderDialog
        
        # Get the attribute data for Companion
        attributes_data = self.load_attributes_data()
        companion_attr = next((a for a in attributes_data if a["name"] == "Companion"), None)
        
        if companion_attr:
            # Create a new attribute based on the Companion template
            attr = companion_attr.copy()
            attr["id"] = str(uuid.uuid4())
            attr["level"] = 1  # Default level
            attr["cost"] = attr["level"] * attr["cost_per_level"]
            
            # Add the attribute to character data
            self.character_data["attributes"].append(attr)
            
            # Add the attribute row to the UI
            self.add_attribute_row(attr)
            
            # Sync companions tab
            from tabs.companions_tab import sync_companions_from_attributes
            sync_companions_from_attributes(self)
            
            # Update tabs visibility and point total
            self.update_dynamic_tabs_visibility()
            self.update_point_total()
        else:
            ui.QMessageBox.warning(self, "Error", "Companion attribute not found in attributes data.")

    def add_minions(self):
        minion = {"name": "New Minion", "description": "Lesser follower", "cp": 0}
        self.character_data["minions"].append(minion)
        self.minions_list.addItem(f"{minion['name']} - {minion['description']} - {minion['cp']} CP")
        self.update_point_total()

    def update_point_total(self):
        total = 0
        warnings = []

        # --- Calculate total CP from stats, attributes, defects, and weapons ---
        for stat in self.stat_spinners:
            value = self.stat_spinners[stat].value()
            self.character_data["stats"][stat] = value
            total += value * 2  # Stats cost 2 CP per level in BESM 4e

            # Validate stat max
            if self.selected_benchmark:
                try:
                    max_stat = int(self.selected_benchmark["max_stat"])
                    if value > max_stat:
                        warnings.append(f"{stat} exceeds benchmark max ({value} > {max_stat})")
                except ValueError:
                    pass

        for attr in self.character_data["attributes"]:
            total += attr["cost"]
            if self.selected_benchmark:
                try:
                    max_attr = int(self.selected_benchmark["max_attribute_level"])
                    if attr["level"] > max_attr:  # Changed back to 'level'
                        warnings.append(f"{attr['name']} level exceeds benchmark max")
                except ValueError:
                    pass
                    
        # Process defects - use 'cost' instead of 'points'
        for defect in self.character_data["defects"]:
            # Note: defect costs are already negative values
            total += defect["cost"]
        
        # Process weapons
        for weapon in self.character_data["weapons"]:
            total += weapon["cost"]

        self.character_data["totalPoints"] = total
        self.spent_cp_display.setText(str(total))

        # Update the suggested benchmark label
        self.update_suggestion_label(total)

        # --- Unspent CP Calculation ---
        starting = self.starting_cp_input.value()
        earned = self.earned_cp_input.value()
        unspent = (starting + earned) - total

        self.unspent_cp_display.setText(str(unspent))

        # Highlight if negative
        self.unspent_cp_display.setProperty("negative", unspent < 0)
        self.unspent_cp_display.style().unpolish(self.unspent_cp_display)
        self.unspent_cp_display.style().polish(self.unspent_cp_display)

        if unspent < 0:
            self.unspent_cp_display.setToolTip("You have spent more points than allowed.")
        else:
            self.unspent_cp_display.setToolTip("Points remaining for upgrades.")

    def update_stat(self, stat_name, value):
        """Update a base stat value and recalculate derived values"""
        self.character_data["stats"][stat_name] = value
        self.update_derived_values()
        self.update_point_total()

    def calculate_derived_values(self, character_data):
        """Calculate derived values based on stats and modifiers from attributes/defects
        
        Args:
            character_data (dict): The character data to calculate derived values for
            
        Returns:
            dict: The updated derived values
        """
        import math
        
        # 1. Start with base stats
        base_body = character_data["stats"]["Body"]
        base_mind = character_data["stats"]["Mind"]
        base_soul = character_data["stats"]["Soul"]
        
        # 2. Apply modifiers from attributes and defects
        body_mods = 0
        mind_mods = 0
        soul_mods = 0
        
        # Track direct modifiers to derived values
        derived_mods = {
            "CV": 0, "ACV": 0, "DCV": 0, "HP": 0, "EP": 0, 
            "DM": 0, "SV": 0, "SP": 0, "SCV": 0, "SOP": 0
        }
        
        # Track multipliers for derived values
        multipliers = {
            "CV": 1, "ACV": 1, "DCV": 1, "HP": 1, "EP": 1, 
            "DM": 1, "SV": 1, "SP": 1, "SCV": 1, "SOP": 1
        }
        
        # Process attributes
        for attr in character_data.get("attributes", []):
            if "stat_mods" in attr:
                level = attr.get("level", 1)
                
                # Handle dynamic modifiers (like Augmented where the stat is chosen by the user)
                if attr["stat_mods"].get("dynamic", False):
                    # For Augmented, we need to look at the user-selected stat
                    if attr.get("key") == "augmented" and "user_input" in attr:
                        target_stat = attr["user_input"].get("stat_target")
                        if target_stat:
                            if target_stat == "Body":
                                body_mods += level
                            elif target_stat == "Mind":
                                mind_mods += level
                            elif target_stat == "Soul":
                                soul_mods += level
                
                # Apply base stat modifiers
                if "base" in attr["stat_mods"]:
                    for stat, value in attr["stat_mods"]["base"].items():
                        if stat == "Body":
                            body_mods += value * level
                        elif stat == "Mind":
                            mind_mods += value * level
                        elif stat == "Soul":
                            soul_mods += value * level
                
                # Apply direct derived value modifiers
                if "derived" in attr["stat_mods"]:
                    for key, value in attr["stat_mods"]["derived"].items():
                        if key in derived_mods:
                            derived_mods[key] += value * level
                
                # Apply multipliers
                if "multipliers" in attr["stat_mods"]:
                    for key, value in attr["stat_mods"]["multipliers"].items():
                        if key in multipliers:
                            multipliers[key] *= value
                
                # Apply level-based modifiers if present
                if "level_based" in attr["stat_mods"] and str(level) in attr["stat_mods"]["level_based"]:
                    level_mods = attr["stat_mods"]["level_based"][str(level)]
                    
                    # Apply level-specific base stat modifiers
                    if "base" in level_mods:
                        body_mods += level_mods["base"].get("Body", 0)
                        mind_mods += level_mods["base"].get("Mind", 0)
                        soul_mods += level_mods["base"].get("Soul", 0)
                    
                    # Apply level-specific derived value modifiers
                    if "derived" in level_mods:
                        for key, value in level_mods["derived"].items():
                            if key in derived_mods:
                                derived_mods[key] += value
                    
                    # Apply level-specific multipliers
                    if "multipliers" in level_mods:
                        for key, value in level_mods["multipliers"].items():
                            if key in multipliers:
                                multipliers[key] *= value
        
        # Process defects
        for defect in character_data.get("defects", []):
            if "stat_mods" in defect:
                rank = defect.get("rank", 1)
                
                # Apply base stat modifiers
                if "base" in defect["stat_mods"]:
                    for stat, value in defect["stat_mods"]["base"].items():
                        if stat == "Body":
                            body_mods += value * rank
                        elif stat == "Mind":
                            mind_mods += value * rank
                        elif stat == "Soul":
                            soul_mods += value * rank
                
                # Apply direct derived value modifiers
                if "derived" in defect["stat_mods"]:
                    for key, value in defect["stat_mods"]["derived"].items():
                        if key in derived_mods:
                            derived_mods[key] += value * rank
                
                # Apply multipliers
                if "multipliers" in defect["stat_mods"]:
                    for key, value in defect["stat_mods"]["multipliers"].items():
                        if key in multipliers:
                            multipliers[key] *= value
                
                # Apply rank-based modifiers if present
                if "rank_based" in defect["stat_mods"] and str(rank) in defect["stat_mods"]["rank_based"]:
                    rank_mods = defect["stat_mods"]["rank_based"][str(rank)]
                    
                    # Apply rank-specific base stat modifiers
                    if "base" in rank_mods:
                        body_mods += rank_mods["base"].get("Body", 0)
                        mind_mods += rank_mods["base"].get("Mind", 0)
                        soul_mods += rank_mods["base"].get("Soul", 0)
                    
                    # Apply rank-specific derived value modifiers
                    if "derived" in rank_mods:
                        for key, value in rank_mods["derived"].items():
                            if key in derived_mods:
                                derived_mods[key] += value
                    
                    # Apply rank-specific multipliers
                    if "multipliers" in rank_mods:
                        for key, value in rank_mods["multipliers"].items():
                            if key in multipliers:
                                multipliers[key] *= value
        
        # 3. Calculate final stats
        body = max(1, base_body + body_mods)  # Ensure minimum of 1
        mind = max(1, base_mind + mind_mods)
        soul = max(1, base_soul + soul_mods)
        
        # 4. Calculate derived values
        cv = math.floor((body + mind + soul) / 3)
        acv = cv
        dcv = cv
        hp = body * 10
        ep = mind * 10
        sv = body * 2
        dm = math.floor((body + soul) / 2)
        sp = soul * 10
        sop = mind * 10
        scv = math.floor((mind + soul) / 2)
        
        # 5. Apply direct modifiers to derived values
        cv += derived_mods["CV"]
        acv += derived_mods["ACV"] + derived_mods["CV"]  # CV mods affect both ACV and DCV
        dcv += derived_mods["DCV"] + derived_mods["CV"]
        hp += derived_mods["HP"]
        ep += derived_mods["EP"]
        sv += derived_mods["SV"]
        dm += derived_mods["DM"]
        sp += derived_mods["SP"]
        sop += derived_mods["SOP"]
        scv += derived_mods["SCV"]
        
        # 6. Apply multipliers
        cv = math.floor(cv * multipliers["CV"])
        acv = math.floor(acv * multipliers["ACV"])
        dcv = math.floor(dcv * multipliers["DCV"])
        hp = math.floor(hp * multipliers["HP"])
        ep = math.floor(ep * multipliers["EP"])
        sv = math.floor(sv * multipliers["SV"])
        dm = math.floor(dm * multipliers["DM"])
        sp = math.floor(sp * multipliers["SP"])
        sop = math.floor(sop * multipliers["SOP"])
        scv = math.floor(scv * multipliers["SCV"])
        
        # 7. Return the derived values
        return {
            "CV": cv,
            "ACV": acv,
            "DCV": dcv,
            "HP": hp,
            "EP": ep,
            "SV": sv,
            "DM": dm,
            "SP": sp,
            "SOP": sop,
            "SCV": scv
        }
    
    def update_derived_values(self):
        """Calculate derived values for the main character and update the UI"""
        # Calculate the derived values
        derived_values = self.calculate_derived_values(self.character_data)
        
        # Update character data
        self.character_data["derived"] = self.character_data.get("derived", {})
        for key, value in derived_values.items():
            self.character_data["derived"][key] = value
        
        # Update UI if labels exist
        if hasattr(self, 'cv_label'):
            self.cv_label.setText(str(derived_values["CV"]))
        if hasattr(self, 'acv_label'):
            self.acv_label.setText(str(derived_values["ACV"]))
        if hasattr(self, 'dcv_label'):
            self.dcv_label.setText(str(derived_values["DCV"]))
        if hasattr(self, 'hp_label'):
            self.hp_label.setText(str(derived_values["HP"]))
        if hasattr(self, 'ep_label'):
            self.ep_label.setText(str(derived_values["EP"]))
        if hasattr(self, 'dm_label'):
            self.dm_label.setText(str(derived_values["DM"]))
        if hasattr(self, 'sv_label'):
            self.sv_label.setText(str(derived_values["SV"]))
        if hasattr(self, 'sp_label'):
            self.sp_label.setText(str(derived_values["SP"]))
        if hasattr(self, 'scv_label'):
            self.scv_label.setText(str(derived_values["SCV"]))
        if hasattr(self, 'sop_label'):
            self.sop_label.setText(str(derived_values["SOP"]))

        # Initialize warnings list
        warnings = []
        
        # Get total CP for benchmark warnings
        total = self.character_data.get("totalPoints", 0)

        # --- Warn if CP is outside the benchmark's recommended range ---
        if self.selected_benchmark:
            pr_min, pr_max = self.selected_benchmark["point_range"]
            if pr_max is None:
                if total < pr_min:
                    warnings.append(f"CP below minimum for {self.selected_benchmark['name']} ({total} < {pr_min})")
            else:
                if total < pr_min or total > pr_max:
                    warnings.append(
                        f"CP outside recommended range for {self.selected_benchmark['name']} ({pr_min}-{pr_max})"
                    )

        # --- Display CP total and warnings visually ---
        if warnings:
            self.spent_cp_display.setStyleSheet("color: red; font-weight: bold;")
            self.spent_cp_display.setToolTip("\n".join(warnings))
        else:
            self.spent_cp_display.setStyleSheet("font-weight: bold;")
            self.spent_cp_display.setToolTip("")

        self.spent_cp_display.setText(str(total))

        # --- Derived Stats ---
        body = self.character_data["stats"]["Body"]
        mind = self.character_data["stats"]["Mind"]
        soul = self.character_data["stats"]["Soul"]

        # Base Combat Value
        cv = math.floor((body + mind + soul) / 3)

        # Attribute Lookup (defaults to 0)
        def get_attribute_level(name):
            return sum(attr["level"] for attr in self.character_data["attributes"] if attr["name"] == name)

        attack_mastery = get_attribute_level("Attack Mastery")
        defense_mastery = get_attribute_level("Defense Mastery")
        massive_damage = get_attribute_level("Massive Damage")
        hardboiled_level = get_attribute_level("Hardboiled")
        unassailable = get_attribute_level("Unassailable")
        unsettled = get_attribute_level("Unsettled")

        acv = math.floor(cv + attack_mastery)
        dcv = math.floor(cv + defense_mastery)
        hp = math.floor((body + soul) * 5)
        ep = math.floor((mind + soul) * 5)
        damage_multiplier = math.floor(5 + massive_damage)
        sv = math.floor((hp / 5) + hardboiled_level)
        sp = math.floor((mind + soul) + unassailable - unsettled)
        scv = math.floor((mind + soul) / 2)
        sop = scv

        # --- Helper function to set value + warning ---
        def set_derived(label: ui.QLabel, value, range_min=None, range_max=None, name=""):
            label.setText(f"{value}")
            label.setToolTip("")
            label.setStyleSheet("")

            if range_min is not None and range_max is not None:
                if value < range_min or value > range_max:
                    label.setStyleSheet("color: red;")
                    label.setToolTip(f"{name} is outside recommended range: {range_min}–{range_max}")
                else:
                    label.setToolTip(f"{name} is within recommended range: {range_min}–{range_max}")

        # Pull ranges from selected benchmark
        if self.selected_benchmark:
            benchmark = self.selected_benchmark
            cv_range = benchmark.get("combat_value_range", [None, None])
            hp_range = benchmark.get("hp_ep_range", [None, None])
            ep_range = benchmark.get("hp_ep_range", [None, None])  # same range for both
            dm_range = benchmark.get("damage_multiplier_range", [None, None])
            sv_range = benchmark.get("shock_value_range", [None, None])
            sp_range = benchmark.get("sanity_points_range", [None, None])
            scv_range = benchmark.get("combat_value_range", [None, None])
            sop_range = benchmark.get("society_points_range", [None, None])

        else:
            cv_range = hp_range = ep_range = dm_range = sv_range = sp_range = scv_range = sop_range = [None, None]

        # Set derived fields with optional warnings
        set_derived(self.cv_label, cv, *cv_range, name="Combat Value")
        set_derived(self.acv_label, acv, *cv_range, name="Attack CV")
        set_derived(self.dcv_label, dcv, *cv_range, name="Defense CV")
        set_derived(self.hp_label, hp, *hp_range, name="Health")
        set_derived(self.ep_label, ep, *ep_range, name="Energy")
        set_derived(self.dm_label, damage_multiplier, *dm_range, name="Damage Multiplier")
        
        def toggle_row(stat_name, value, label, range_, layout_name):
            layout = self.stat_rows.get(layout_name)
            if self.extra_stats_enabled.get(stat_name, False):
                set_derived(label, value, *range_, name=stat_name)
                if layout:
                    layout.show()
            else:
                if layout:
                    layout.hide()

        toggle_row("Shock Value", sv, self.sv_label, sv_range, "Shock Value")
        toggle_row("Sanity Points", sp, self.sp_label, sp_range, "Sanity Points")
        toggle_row("Social Combat Value", scv, self.scv_label, scv_range, "Social Combat Value")
        toggle_row("Society Points", sop, self.sop_label, sop_range, "Society Points")

    def save_character(self):
        """Save the current character to the last used file path"""
        if not hasattr(self, 'current_file_path') or not self.current_file_path:
            self.save_character_as()
            return
            
        try:
            self.save_character_to_file(self.current_file_path)
            self.statusBar().showMessage(f"Character saved to {self.current_file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save character: {str(e)}")
            
    def save_character_as(self):
        """Save the current character to a new file"""
        last_dir = self.settings.value("last_directory", "./characters")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Character",
            last_dir,
            "BESM Character Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Update the last used directory
                self.settings.setValue("last_directory", os.path.dirname(file_path))
                self.current_file_path = file_path
                self.save_character_to_file(file_path)
                self.statusBar().showMessage(f"Character saved to {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save character: {str(e)}")
                
    def save_character_to_file(self, file_path):
        """Save the character data to the specified file"""
        # Collect all character data from tabs
        character_data = self.character_data.copy()
        
        # Create a backup before saving
        self.backup_manager.create_backup(self.character_data, manual=False)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=4)
            
    def load_character(self):
        """Load a character from a file"""
        last_dir = self.settings.value("last_directory", "./characters")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Character",
            last_dir,
            "BESM Character Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Create a backup before loading
                self.backup_manager.create_backup(self.character_data, manual=False)
                
                # Update the last used directory
                self.settings.setValue("last_directory", os.path.dirname(file_path))
                
                # Load the character data
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # Validate the loaded data
                if not self.validate_loaded_data(loaded_data):
                    raise ValueError("Invalid character data format")
                
                # Update the current file path
                self.current_file_path = file_path
                
                # Update the character data
                self.character_data.update(loaded_data)
                
                # Refresh all tabs with the new data
                self.refresh_all_tabs()
                
                self.statusBar().showMessage(f"Character loaded from {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load character: {str(e)}")
                
    def validate_loaded_data(self, data):
        """Validate that the loaded data has the required structure"""
        required_keys = [
            "attributes", "derived_stats", "defects", "skills",
            "items", "powers", "character_info", "notes"
        ]
        return all(key in data for key in required_keys)
        
    def refresh_all_tabs(self):
        """Refresh all tabs with the current character data"""
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, 'refresh'):
                tab.refresh()
                
    def new_character(self):
        """Create a new character"""
        if hasattr(self, 'current_file_path') and self.current_file_path:
            reply = QMessageBox.question(
                self,
                "New Character",
                "Do you want to save the current character before creating a new one?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.save_character()
            elif reply == QMessageBox.Cancel:
                return
                
        # Create a backup before creating new character
        self.backup_manager.create_backup(self.character_data, manual=False)
        
        # Reset character data to default values
        self.character_data = {
            "version": self.data_migrator.current_version,
            "name": "",
            "player": "",
            "gm": "",
            "race": "",
            "class": "",
            "homeworld": "",
            "size": "",
            "background": {
                "origin": "",
                "faction": "",
                "goals": "",
                "personality": "",
                "history": ""
            },
            "stats": {
                "Body": 0,
                "Mind": 0,
                "Soul": 0
            },
            "derived": {
                "CV": 0,
                "ACV": 0,
                "DCV": 0,
                "HP": 0,
                "EP": 0,
                "DM": 0,
                "SV": 0,
                "SP": 0,
                "SCV": 0,
                "SOP": 0
            },
            "drama_points": {
                "current": 3,
                "max": 5
            },
            "attributes": [],
            "defects": [],
            "skills": [],
            "weapons": [],
            "armor": [],
            "items": [],
            "techniques": [],
            "templates": [],
            "alternate_forms": [],
            "metamorphosis": [],
            "companions": [],
            "minions": [],
            "relationships": [],
            "notes": "",
            "custom_fields": {},
            "custom_rules": [],
            "saved_loadouts": [],
            "benchmark": None,
            "totalPoints": 0
        }
        
        # Clear the current file path
        self.current_file_path = None
        
        # Refresh all tabs
        self.refresh_all_tabs()
        
        self.statusBar().showMessage("New character created", 3000)

    def set_benchmark(self, label):
        """
        Set the benchmark based on the selected dropdown label
        """
        if not label or label == "No Benchmark":
            self.selected_benchmark = None
            self.user_selected_benchmark = True
            self.update_point_total()
            return
            
        # Extract the benchmark name from the label (format: "Name (CP Range)")
        name = label.split(" (")[0]
        self.set_benchmark_by_name(name)
    
    def set_benchmark_by_name(self, name):
        # Find the benchmark by name
        for benchmark in self.benchmarks:
            if benchmark["name"] == name:
                self.selected_benchmark = benchmark
                self.user_selected_benchmark = True
                break
                
        # Update the dropdown to match
        for i in range(self.benchmark_dropdown.count()):
            if self.benchmark_dropdown.itemData(i) == name:
                self.benchmark_dropdown.setCurrentIndex(i)
                break
                
        # Update the UI to reflect the new benchmark
        self.update_point_total()

    def load_character_into_ui(self):
        # Set stat spinners
        for stat, spinner in self.stat_spinners.items():
            spinner.setValue(self.character_data["stats"].get(stat, 4))

        # Rebuild attributes list
        from tabs.attributes_tab import sync_attributes
        sync_attributes(self)
        self.update_dynamic_tabs_visibility()

        # Rebuild defects list
        from tabs.defects_tab import sync_defects
        sync_defects(self)

        # Set character info fields
        self.char_name_input.setText(self.character_data.get("name", ""))
        self.player_name_input.setText(self.character_data.get("player", ""))
        self.gm_name_input.setText(self.character_data.get("gm", ""))
        self.race_input.setText(self.character_data.get("race", ""))
        self.class_input.setText(self.character_data.get("class", ""))
        self.homeworld_input.setText(self.character_data.get("homeworld", ""))
        self.size_input.setText(self.character_data.get("size", ""))

        # Apply benchmark if one was selected
        benchmark = self.character_data.get("benchmark", None)
        if benchmark:
            self.set_benchmark_by_name(benchmark)

        # Ensure these keys exist in character data
        if "companions" not in self.character_data:
            self.character_data["companions"] = []
        if "items" not in self.character_data:
            self.character_data["items"] = []
        if "metamorphosis" not in self.character_data:
            self.character_data["metamorphosis"] = []
        if "minions" not in self.character_data:
            self.character_data["minions"] = []
        if "alternate_forms" not in self.character_data:
            self.character_data["alternate_forms"] = []
            
        # Sync all special attribute tabs
        sync_alternate_forms_from_attributes(self)
        
        from tabs.companions_tab import sync_companions_from_attributes
        from tabs.items_tab import sync_items_from_attributes
        from tabs.metamorphosis_tab import sync_metamorphosis_from_attributes
        from tabs.minions_tab import sync_minions_from_attributes
        
        sync_companions_from_attributes(self)
        sync_items_from_attributes(self)
        sync_metamorphosis_from_attributes(self)
        sync_minions_from_attributes(self)

    def update_dynamic_tabs_visibility(self):
        # Count how many of each dynamic attribute is present
        attr_counts = {name: 0 for name in self.dynamic_tabs}

        # Create a mapping for singular/plural forms
        name_mapping = {
            "Companion": "Companions",
            "Item": "Items",
            "Alternate Form": "Alternate Form",
            "Metamorphosis": "Metamorphosis",
            "Minions": "Minions"
        }

        for attr in self.character_data["attributes"]:
            base_name = attr.get("base_name", attr["name"])
            # Check if we need to map a singular form to a plural form
            if base_name in name_mapping and name_mapping[base_name] in self.dynamic_tabs:
                attr_counts[name_mapping[base_name]] += 1
            # Also check direct matches
            for tracked in self.dynamic_tabs:
                if base_name == tracked:
                    attr_counts[tracked] += 1

        for attr_name, info in self.dynamic_tabs.items():
            visible = attr_counts[attr_name] > 0
            current_index = self.tabs.indexOf(info["tab"])

            if visible and current_index == -1:
                self.tabs.addTab(info["tab"], attr_name)
            elif not visible and current_index != -1:
                self.tabs.removeTab(current_index)
                
    def update_suggestion_label(self, total_cp):
        # Always calculate the suggested benchmark based on current CP
        self.suggested_benchmark_name = None
        
        # Debug: Print total CP and benchmarks
        print(f"[DEBUG] Total CP: {total_cp}")
        print(f"[DEBUG] Benchmarks loaded: {len(self.benchmarks)}")
        if not self.benchmarks:
            print("[DEBUG] Benchmarks list is empty! No suggestion possible.")
        else:
            for i, b in enumerate(self.benchmarks):
                print(f"[DEBUG] Benchmark {i}: {b['name']} range={b['point_range']}")
        
        # Find the appropriate benchmark for the current CP
        for b in self.benchmarks:
            pr_min, pr_max = b["point_range"]
            print(f"[DEBUG] Checking benchmark '{b['name']}' with range {pr_min} to {pr_max} against CP {total_cp}")
            if pr_max is None:
                if total_cp >= pr_min:
                    print(f"[DEBUG] Matched open-ended benchmark: {b['name']}")
                    self.suggested_benchmark_name = b["name"]
                    break
            elif pr_min <= total_cp <= pr_max:
                print(f"[DEBUG] Matched closed-range benchmark: {b['name']}")
                self.suggested_benchmark_name = b["name"]
                break
        
        # Update the label if we found a suggested benchmark
        if self.suggested_benchmark_name:
            # Only show suggestion if it's different from the current selection
            current_benchmark = self.selected_benchmark["name"] if self.selected_benchmark else None
            if current_benchmark != self.suggested_benchmark_name:
                self.suggestion_label.setText(f"🧠 Suggested Benchmark: {self.suggested_benchmark_name} (Click to apply)")
                return
        
        # Clear the label if no suggestion or same as current
        self.suggestion_label.setText("")

        # No suggestion found
        self.suggestion_label.setText("No suggested benchmark found.")

    def toggle_extra_stat(self, name, enabled):
        self.extra_stats_enabled[name] = enabled
        self.update_point_total()  # Refresh stats display

    def on_suggestion_clicked(self, event):
        if self.suggested_benchmark_name:
            print(f"Clicked suggestion label. Setting benchmark to: {self.suggested_benchmark_name}")
            # Reset user selection flag to allow suggestions again
            self.user_selected_benchmark = False
            # Set the benchmark
            self.set_benchmark_by_name(self.suggested_benchmark_name)
        else:
            print("No suggested benchmark available.")
    
    def add_defect(self):
        """Open the defect builder dialog to add a new defect"""
        dialog = DefectBuilderDialog(self, self.defects)
        
        if dialog.exec_():
            defect_data = dialog.get_defect_data()
            defect_data["id"] = str(uuid.uuid4())  # Generate a unique ID
            
            # Add to character data
            if "defects" not in self.character_data:
                self.character_data["defects"] = []
            self.character_data["defects"].append(defect_data)
            
            # Update the UI
            from tabs.defects_tab import sync_defects
            sync_defects(self)
            
            # Update points
            self.update_point_total()
            
    def edit_defect_by_id(self, defect_id):
        """Edit an existing defect by ID"""
        # Find the existing defect
        defect_data = None
        for defect in self.character_data.get("defects", []):
            if defect.get("id") == defect_id:
                defect_data = defect
                break
                
        if not defect_data:
            print(f"[ERROR] Could not find defect with ID {defect_id}")
            return
            
        # Create and show the dialog
        dialog = DefectBuilderDialog(self, self.defects)
        
        # If we have a key, use it to find the correct base defect
        if "key" in defect_data:
            # Find the defect name that matches this key
            for defect_name, defect_info in self.defects.items():
                if defect_info.get("key") == defect_data["key"]:
                    defect_data["base_name"] = defect_name
                    break
        
        dialog.load_defect_data(defect_data)
        
        if dialog.exec_():
            # Get the updated defect data
            new_defect_data = dialog.get_defect_data()
            new_defect_data["id"] = defect_id  # Preserve the ID
            
            # Preserve the key if it existed
            if "key" in defect_data:
                new_defect_data["key"] = defect_data["key"]
            
            # Update the defect in the character data
            defects = self.character_data.get("defects", [])
            for i, defect in enumerate(defects):
                if defect.get("id") == defect_id:
                    defects[i] = new_defect_data
                    break
                    
            # Update the UI
            from tabs.defects_tab import sync_defects
            sync_defects(self)
            
            # Update point total
            self.update_point_total()
    
    def edit_attribute_by_id(self, attr_id):
        """Edit an attribute by its ID and keep UI/points in sync."""
        # Locate the attribute to edit
        existing_attr = next((a for a in self.character_data.get("attributes", []) if a.get("id") == attr_id), None)
        if not existing_attr:
            ui.QMessageBox.warning(self, "Error", "Attribute not found.")
            return

        # If this is Unknown Power, open its dedicated manager instead of the generic builder
        if existing_attr.get("key") == "unknown_power" or existing_attr.get("name") == "Unknown Power":
            self.open_unknown_power_manager(existing_attr)
            return

        dialog = AttributeBuilderDialog(self, existing_attr=existing_attr)

        if dialog.exec_() == ui.QDialog.Accepted:
            new_attr = dialog.get_attribute_data()
            # Ensure the ID is preserved
            new_attr["id"] = attr_id

            # Replace the old attribute with the edited one
            for i, attr in enumerate(self.character_data["attributes"]):
                if attr.get("id") == attr_id:
                    self.character_data["attributes"][i] = new_attr
                    break

            # Safely refresh the attribute list UI next event cycle
            from PyQt5 import QtCore
            QtCore.QTimer.singleShot(0, self._safe_refresh_attributes_ui)

            # Update any related special tabs, if applicable
            base_name = new_attr.get("base_name", new_attr["name"])
            if base_name == "Alternate Form":
                QtCore.QTimer.singleShot(10, lambda: sync_alternate_forms_from_attributes(self))
            elif base_name in ["Companion", "Companions"]:
                from tabs.companions_tab import sync_companions_from_attributes
                QtCore.QTimer.singleShot(10, lambda: sync_companions_from_attributes(self))
            elif base_name in ["Item", "Items"]:
                from tabs.items_tab import sync_items_from_attributes
                QtCore.QTimer.singleShot(10, lambda: sync_items_from_attributes(self))
            elif base_name == "Metamorphosis":
                from tabs.metamorphosis_tab import sync_metamorphosis_from_attributes
                QtCore.QTimer.singleShot(10, lambda: sync_metamorphosis_from_attributes(self))
            elif base_name == "Minions":
                from tabs.minions_tab import sync_minions_from_attributes
                QtCore.QTimer.singleShot(10, lambda: sync_minions_from_attributes(self))

            # Recalculate derived stats and point totals immediately
            self.update_derived_values()
            self.update_point_total()

            # Update dynamic tab visibility shortly after so counts are correct
            QtCore.QTimer.singleShot(20, self.update_dynamic_tabs_visibility)

    def remove_attribute_by_id(self, attr_id):
        """Remove an attribute by its ID and update UI/CP."""
        removed_attr = None
        base_name = None

        # Remove the attribute from character data
        for i, attr in enumerate(self.character_data.get("attributes", [])):
            if attr.get("id") == attr_id:
                base_name = attr.get("base_name", attr["name"])
                removed_attr = self.character_data["attributes"].pop(i)
                break

        if removed_attr is None:
            print(f"[DEBUG] Attribute with ID {attr_id} not found")
            return

        # Refresh attribute UI next event cycle
        from PyQt5 import QtCore
        QtCore.QTimer.singleShot(0, self._safe_refresh_attributes_ui)

        # Sync special tabs if necessary
        if base_name == "Alternate Form":
            QtCore.QTimer.singleShot(10, lambda: sync_alternate_forms_from_attributes(self))
        elif base_name in ["Companion", "Companions"]:
            from tabs.companions_tab import sync_companions_from_attributes
            QtCore.QTimer.singleShot(10, lambda: sync_companions_from_attributes(self))
        elif base_name in ["Item", "Items"]:
            from tabs.items_tab import sync_items_from_attributes
            QtCore.QTimer.singleShot(10, lambda: sync_items_from_attributes(self))
        elif base_name == "Metamorphosis":
            from tabs.metamorphosis_tab import sync_metamorphosis_from_attributes
            QtCore.QTimer.singleShot(10, lambda: sync_metamorphosis_from_attributes(self))
        elif base_name == "Minions":
            from tabs.minions_tab import sync_minions_from_attributes
            QtCore.QTimer.singleShot(10, lambda: sync_minions_from_attributes(self))

        # Update derived values and CP totals
        self.update_derived_values()
        self.update_point_total()

        # Adjust dynamic tabs shortly after
        QtCore.QTimer.singleShot(20, self.update_dynamic_tabs_visibility)

    
    def remove_defect_by_id(self, defect_id):
        """Remove a defect by its ID and update the UI"""
        # Find the defect with the given ID
        removed_defect = None
        
        # Find and remove the defect from the character data
        for i, defect in enumerate(self.character_data.get("defects", [])):
            if defect.get("id") == defect_id:
                removed_defect = self.character_data["defects"].pop(i)
                print(f"[DEBUG] Removed defect: {removed_defect.get('name', 'Unknown')}")
                break
        
        # If we didn't find the defect, nothing to do
        if removed_defect is None:
            print(f"[DEBUG] Defect with ID {defect_id} not found")
            return
        
        # Update the UI
        from tabs.defects_tab import sync_defects
        sync_defects(self)
        
        # Update point total
        self.update_point_total()
    
    def _safe_refresh_attributes_ui(self):
        """Safely refresh the attributes UI by completely rebuilding it."""
        try:
            # Import the necessary function from the attributes tab module
            from tabs.attributes_tab import populate_attributes_ui, sync_attributes
            
            # First try to use the sync_attributes function
            try:
                print("[DEBUG] Refreshing attributes UI using sync_attributes")
                sync_attributes(self)
                print("[DEBUG] Attributes UI refreshed successfully")
                return
            except Exception as e:
                print(f"[DEBUG] Error using sync_attributes: {e}")
                
            # If that fails, try populate_attributes_ui directly
            try:
                print("[DEBUG] Trying populate_attributes_ui as fallback")
                populate_attributes_ui(self)
                print("[DEBUG] Attributes UI refreshed successfully using fallback")
            except Exception as e:
                print(f"[DEBUG] Error using populate_attributes_ui: {e}")
                # Last resort: try to recreate the UI from scratch
                if hasattr(self, 'attributes_scroll_area') and self.attributes_scroll_area is not None:
                    from PyQt5.QtWidgets import QWidget, QVBoxLayout
                    from PyQt5.QtCore import Qt
                    
                    print("[DEBUG] Recreating attributes UI from scratch")
                    # Create a new container
                    self.attr_card_container = QWidget()
                    self.attributes_layout = QVBoxLayout(self.attr_card_container)
                    self.attributes_layout.setContentsMargins(8, 8, 8, 8)
                    self.attributes_layout.setSpacing(6)
                    self.attributes_layout.setAlignment(Qt.AlignTop)
                    
                    # Set the new container as the widget for the scroll area
                    self.attributes_scroll_area.setWidget(self.attr_card_container)
                    
                    # Manually rebuild the attribute cards
                    from tools.utils import create_card_widget
                    from uuid import uuid4
                    
                    for attr in self.character_data.get("attributes", []):
                        # Ensure the attribute has an ID
                        if "id" not in attr:
                            attr["id"] = str(uuid4())
                            
                        # Create handlers for this attribute
                        attr_id = attr["id"]
                        remove_handler = lambda aid=attr_id: self.remove_attribute_by_id(aid)
                        edit_handler = lambda aid=attr_id: self.edit_attribute_by_id(aid)
                        
                        # Create simple display lines
                        lines = [
                            f"Level: {attr.get('level', 0)}",
                            f"Cost: {attr.get('cost', 0)} CP"
                        ]
                        
                        # Create and add the card
                        card = create_card_widget(
                            title=attr.get("name", "Unnamed Attribute"),
                            lines=lines,
                            on_remove=remove_handler,
                            on_click=edit_handler,
                            card_type="attribute"
                        )
                        self.attributes_layout.insertWidget(0, card)
                    
                    print("[DEBUG] Attributes UI rebuilt manually")
        except Exception as e:
            print(f"[DEBUG] Critical error in _safe_refresh_attributes_ui: {e}")
        
    def create_new_character(self):
        # Clear basic fields
        self.char_name_input.clear()
        self.player_name_input.clear()
        self.gm_name_input.clear()
        self.race_input.clear()
        self.class_input.clear()
        self.homeworld_input.clear()
        self.size_input.clear()

        # Reset stats
        for stat in self.stat_spinners:
            self.stat_spinners[stat].setValue(4)

        # Clear attributes, defects, weapons
        self.character_data["attributes"].clear()
        self.character_data["defects"].clear()
        self.character_data["weapons"].clear()
        
        # Reset CP inputs
        self.starting_cp_input.setValue(0)
        self.earned_cp_input.setValue(0)

        # Reset benchmark
        self.benchmark_dropdown.setCurrentIndex(0)
        self.selected_benchmark = None
        self.user_selected_benchmark = False

        # Update UI
        from tabs.attributes_tab import sync_attributes
        sync_attributes(self)
        from tabs.defects_tab import sync_defects
        sync_defects(self)
        
        # Update points and UI
        self.update_point_total()
        self.update_dynamic_tabs_visibility()
        
        # Create automatic backup of new character
        self.backup_manager.create_backup(self.character_data, manual=False)

    def edit_alternate_form(self, uid):
        from dialogs.alternate_form_editor_dialog import AlternateFormEditorDialog

        form = self.get_alternate_form_by_id(uid)
        if not form:
            ui.QMessageBox.warning(self, "Error", f"Alternate Form with ID {uid} not found.")
            return

        dialog = AlternateFormEditorDialog(self, form_data=form)
        if dialog.exec_() == ui.QDialog.Accepted:
            updated_form = dialog.get_form_data()

            # Replace the old form (keeping the ID intact)
            for i, existing in enumerate(self.character_data["alternate_forms"]):
                if existing.get("id") == uid:
                    self.character_data["alternate_forms"][i] = updated_form
                    break
            
            # Update the corresponding attribute to match the form's level
            for attr in self.character_data["attributes"]:
                if attr.get("id") == uid:
                    # Update the attribute level and cost
                    attr["level"] = updated_form["level"]
                    attr["cost"] = attr["level"] * attr.get("cost_per_level", 4)
                    # Update the attribute name if it changed
                    if attr["name"] != updated_form["name"]:
                        attr["name"] = updated_form["name"]
                    break

            # Update the UI
            from tabs.attributes_tab import sync_attributes
            sync_attributes(self)
            from tabs.alternate_forms_tab import sync_alternate_forms_from_attributes, populate_alternate_form_ui
            populate_alternate_form_ui(self)
            
            self.update_point_total()

    def get_alternate_form_by_id(self, uid):
        for form in self.character_data["alternate_forms"]:
            if form.get("id") == uid:
                return form
        return None
    
    def edit_item(self, uid):
        from dialogs.item_builder_dialog import ItemBuilderDialog
        from tabs.items_tab import populate_items_ui
        
        # Find the item data by ID
        item_data = None
        for item in self.character_data["items"]:
            if item["id"] == uid:
                item_data = item
                break
        
        if not item_data:
            ui.QMessageBox.warning(self, "Error", "Item not found.")
            return
        
        # Open the item builder dialog
        dialog = ItemBuilderDialog(self, item_data)
        if dialog.exec_():
            # Get updated item data
            updated_data = dialog.get_item_data()
            
            # Update the item in character data
            for i, item in enumerate(self.character_data["items"]):
                if item["id"] == uid:
                    self.character_data["items"][i] = updated_data
                    break
            
            # Refresh the UI
            populate_items_ui(self)
            self.update_point_total()

    def edit_metamorphosis(self, uid):
        meta = next((m for m in self.character_data["metamorphosis"] if m.get("id") == uid), None)
        if not meta:
            ui.QMessageBox.warning(self, "Error", f"No metamorphosis found with ID {uid}")
            return

        ui.QMessageBox.information(self, "Edit Metamorphosis", f"Editing: {meta['name']}\n(Not yet implemented)")
        
    def edit_companion(self, uid):
        companion = next((c for c in self.character_data["companions"] if c.get("id") == uid), None)
        if not companion:
            QMessageBox.warning(self, "Error", f"No companion found with ID {uid}")
            return

        from dialogs.companion_builder_dialog import CompanionBuilderDialog
        dialog = CompanionBuilderDialog(self, companion)
        if dialog.exec_() == QDialog.Accepted:
            updated_companion = dialog.get_companion_data()
            for i, c in enumerate(self.character_data["companions"]):
                if c.get("id") == uid:
                    self.character_data["companions"][i] = updated_companion
                    break
            for attr in self.character_data["attributes"]:
                if attr.get("id") == uid:
                    attr["level"] = updated_companion["level"]
                    attr["cost"] = attr["level"] * attr.get("cost_per_level", 10)
                    break
            from tabs.companions_tab import populate_companions_ui
            populate_companions_ui(self)
            from tabs.attributes_tab import sync_attributes
            sync_attributes(self)
            self.update_point_total()
    
    def edit_minion(self, uid):
        minion = next((m for m in self.character_data["minions"] if m.get("id") == uid), None)
        if not minion:
            QMessageBox.warning(self, "Error", f"No minion found with ID {uid}")
            return

        from dialogs.minion_builder_dialog import MinionBuilderDialog
        dialog = MinionBuilderDialog(self, minion)
        if dialog.exec_() == QDialog.Accepted:
            updated_minion = dialog.get_minion_data()
            for i, m in enumerate(self.character_data["minions"]):
                if m.get("id") == uid:
                    self.character_data["minions"][i] = updated_minion
                    break
            for attr in self.character_data["attributes"]:
                if attr.get("id") == uid:
                    attr["level"] = updated_minion["level"]
                    attr["cost"] = attr["level"] * attr.get("cost_per_level", 10)
                    break
            from tabs.minions_tab import populate_minions_ui
            populate_minions_ui(self)
            from tabs.attributes_tab import sync_attributes
            sync_attributes(self)
            self.update_point_total()

    def edit_metamorphosis(self, uid):
        meta = next((m for m in self.character_data["metamorphosis"] if m.get("id") == uid), None)
        if not meta:
            QMessageBox.warning(self, "Error", f"No metamorphosis found with ID {uid}")
            return

        from dialogs.metamorphosis_editor_dialog import MetamorphosisEditorDialog
        dialog = MetamorphosisEditorDialog(self, metamorphosis_data=meta)
        if dialog.exec_() == QDialog.Accepted:
            updated_meta = dialog.get_metamorphosis_data()
            for i, m in enumerate(self.character_data["metamorphosis"]):
                if m.get("id") == uid:
                    self.character_data["metamorphosis"][i] = updated_meta
                    break
            for attr in self.character_data["attributes"]:
                if attr.get("id") == uid:
                    attr["level"] = updated_meta["level"]
                    attr["cost"] = attr["level"] * attr.get("cost_per_level", 10)
                    break
            from tabs.metamorphosis_tab import populate_metamorphosis_ui
            populate_metamorphosis_ui(self)
            from tabs.attributes_tab import sync_attributes
            sync_attributes(self)
            self.update_point_total()

    def open_template_dialog(self, template_type):
        """Open a dialog to select a template"""
        from templates.template_manager import TemplateDialog, apply_template_to_character
        
        dialog = TemplateDialog(self, template_type)
        if dialog.exec_() == ui.QDialog.Accepted:
            template = dialog.get_selected_template()
            if template:
                success = apply_template_to_character(self, template, template_type)
                if success:
                    ui.QMessageBox.information(self, "Template Applied", f"The {template.get('name', 'selected')} template has been applied successfully.")
                else:
                    ui.QMessageBox.warning(self, "Error", "Failed to apply template.")
    
    def manage_templates(self):
        """Open a dialog to manage applied templates"""
        from templates.template_manager import show_applied_templates_dialog
        
        # Check if there are any applied templates
        if not self.character_data.get("applied_templates"):
            ui.QMessageBox.information(self, "No Templates", "There are no templates applied to this character.")
            return
        
        show_applied_templates_dialog(self)
    
    def apply_selected_template_from_combo(self, template_type):
        """Apply a selected template from combo box on main UI."""
        from templates.template_manager import apply_template_to_character
        combo = None
        if template_type == "race":
            combo = self.race_template_combo
        if not combo:
            return
        template = combo.currentData()
        success = apply_template_to_character(self, template, template_type)
        if success:
            ui.QMessageBox.information(self, "Template Applied", f"{template_type.title()} template applied successfully.")
        else:
            ui.QMessageBox.warning(self, "Error", f"Failed to apply {template_type} template.")

    # Class variable to track unnamed character count
    _unnamed_character_count = 0
    
    def export_to_pdf(self):
        """Export the current character to a PDF file"""
        try:
            # Get character name or generate a numbered default
            char_name = self.character_data.get("name", "")
            if not char_name or char_name.strip() == "":
                # Increment the class-level counter for unnamed characters
                BESMCharacterApp._unnamed_character_count += 1
                char_name = f"Character_{BESMCharacterApp._unnamed_character_count}"
            
            # Replace spaces and special characters for filename
            safe_char_name = char_name.replace(" ", "_").replace("/", "-").replace("\\", "-")
            safe_char_name = ''.join(c for c in safe_char_name if c.isalnum() or c in "_-")
            
            default_path = os.path.join(os.path.expanduser("~"), "Desktop", f"{safe_char_name}.pdf")
            
            file_path, _ = ui.QFileDialog.getSaveFileName(
                self,
                "Export Character to PDF",
                default_path,
                "PDF Files (*.pdf)"
            )
            
            if not file_path:  # User cancelled
                return
                
            # Add .pdf extension if not present
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"
            
            # Ensure all data is in the correct format before exporting
            # Make a deep copy to avoid modifying the original data
            import copy
            export_data = copy.deepcopy(self.character_data)
            
            # Ensure stats is a dictionary
            if "stats" not in export_data or not isinstance(export_data["stats"], dict):
                export_data["stats"] = {"Body": 1, "Mind": 1, "Soul": 1}
                
            # Ensure attributes is a list
            if "attributes" not in export_data or not isinstance(export_data["attributes"], list):
                export_data["attributes"] = []
                
            # Ensure defects is a list
            if "defects" not in export_data or not isinstance(export_data["defects"], list):
                export_data["defects"] = []
                
            # Ensure skills is a list
            if "skills" not in export_data or not isinstance(export_data["skills"], list):
                export_data["skills"] = []
            
            # Export the character to PDF
            ui.QMessageBox.information(
                self,
                "Exporting to PDF",
                "Creating PDF export with improved text wrapping. This may take a moment..."
            )
            
            output_path = export_character_to_pdf(export_data, file_path)
            
            # Show success message
            ui.QMessageBox.information(
                self,
                "Export Successful",
                f"Character exported to:\n{output_path}\n\nText in tables will now properly wrap to fit columns."
            )
            
        except Exception as e:
            # Show detailed error message with traceback
            import traceback
            error_details = traceback.format_exc()
            ui.QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export character to PDF:\n{str(e)}\n\nDetails:\n{error_details}"
            )

    def open_backup_manager(self):
        """Open the backup manager dialog"""
        dialog = BackupDialog(self, self.backup_manager)
        dialog.exec_()

    def init_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = file_menu.addAction('New Character')
        new_action.triggered.connect(self.new_character)
        
        load_action = file_menu.addAction('Load Character')
        load_action.triggered.connect(self.load_character)
        
        save_action = file_menu.addAction('Save Character')
        save_action.triggered.connect(self.save_character)
        
        save_as_action = file_menu.addAction('Save Character As...')
        save_as_action.triggered.connect(self.save_character_as)
        
        export_pdf_action = file_menu.addAction('Export to PDF')
        export_pdf_action.triggered.connect(self.export_to_pdf)
        
        # Data Management menu
        data_menu = menubar.addMenu('Data Management')
        
        backup_action = data_menu.addAction('Create Backup')
        backup_action.triggered.connect(lambda: self.backup_manager.create_manual_backup())
        
        restore_action = data_menu.addAction('Restore from Backup')
        restore_action.triggered.connect(lambda: self.tabs.setCurrentIndex(self.tabs.count() - 1))  # Switch to Data Management tab
        
        validate_action = data_menu.addAction('Validate Character Data')
        validate_action.triggered.connect(self.validate_current_character)
        
        repair_action = data_menu.addAction('Repair Database')
        repair_action.triggered.connect(self.repair_database)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
        
    def validate_current_character(self):
        """Validate the current character data and show results"""
        self.tabs.setCurrentIndex(self.tabs.count() - 1)  # Switch to Data Management tab
        # The validation will be handled by the Data Management tab's validation function
        
    def repair_database(self):
        """Open the Data Management tab's repair tools"""
        self.tabs.setCurrentIndex(self.tabs.count() - 1)  # Switch to Data Management tab
        # The repair will be handled by the Data Management tab's repair function

    def show_about(self):
        """Show the About dialog"""
        QMessageBox.about(
            self,
            "About BESM Character Generator",
            "BESM Character Generator\n\n"
            "A tool for creating and managing BESM (Big Eyes, Small Mouth) characters.\n\n"
            "Version: 1.0\n"
            "Created by: LegendMasters"
        )

    def open_library_manager(self):
        """Open the Library Manager dialog"""
        from dialogs.library_manager_dialog import LibraryManagerDialog
        
        dialog = LibraryManagerDialog(self)
        dialog.exec_()

if __name__ == "__main__":
    app = ui.QApplication(sys.argv)

    try:
        with open(resource_path("style.qss"), "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Failed to load stylesheet: {e}")

    window = BESMCharacterApp()
    
    # Add backup menu item
    backup_action = window.menuBar().addAction("Backup Manager")
    backup_action.triggered.connect(window.open_backup_manager)
    
    window.show()
    sys.exit(app.exec_())
