# BESM Character Generator Architecture

This document describes the technical architecture of the BESM 4e Character Generator application.

## Overview

The BESM Character Generator is built using Python with PyQt5 for the GUI. It follows a modular design with separate components for the UI, data management, and business logic.

## Architecture Diagram

```
┌─────────────────────────────────────┐
│             besm_app.py             │
│  (Main Application & Window Setup)  │
└───────────────┬─────────────────────┘
                │
    ┌───────────┴────────────┐
    │                        │
┌───▼───────┐        ┌───────▼───────┐
│   tabs/   │        │     tools/    │
│  (UI Tabs)│        │  (Utilities)  │
└───────────┘        └───────────────┘
    │                        │
    │                        │
┌───▼───────┐        ┌───────▼───────┐
│  dialogs/ │        │     data/     │
│ (UI Dialogs)       │ (JSON Data)   │
└───────────┘        └───────────────┘
```

## Component Descriptions

### Main Application (besm_app.py)

The main application file serves as the entry point and contains:

- The `BESMCharacterApp` class which extends `QMainWindow`
- Initialization of the main window and UI components
- Loading of core data (attributes, defects)
- Character data structure management
- Main application logic

### UI Tabs (tabs/)

The tabs directory contains modules for each tab in the application:

- `attributes_tab.py` - Attribute management interface
- `stats_tab.py` - Character stats interface
- `alternate_forms_tab.py` - Alternate forms management
- `companions_tab.py` - Companion management
- `minions_tab.py` - Minion management
- `items_tab.py` - Item management
- `metamorphosis_tab.py` - Metamorphosis management

Each tab module contains functions for:
- Initializing the tab UI
- Handling tab-specific events
- Updating the UI based on character data changes
- Syncing UI state with the character data model

### Dialogs (dialogs/)

The dialogs directory contains dialog windows used throughout the application:

- `attribute_builder_dialog.py` - Dialog for creating/editing attributes
- Template dialogs for selecting race, class, and size templates

### Tools (tools/)

The tools directory contains utility functions and helper classes:

- `utils.py` - General utility functions
- `pdf_export.py` - PDF generation for character sheets
- `widgets.py` - Custom UI widgets

### Data (data/)

The data directory contains JSON files that define the game elements:

- `attributes.json` - Definitions of all attributes
- `defects.json` - Definitions of all defects
- `templates/` - Character templates
  - `classes/` - Class templates (individual JSON files)
  - `races/` - Race templates (individual JSON files)
  - `sizes/` - Size templates (individual JSON files)
  - `index.json` - Index of all templates

## Data Flow

1. The application loads attribute and defect definitions from JSON files
2. Templates are loaded from individual files in the templates directory
3. When a template is applied, its attributes and defects are added to the character
4. UI components display and allow editing of character data
5. Changes to the character are stored in the character data structure
6. Character data can be saved to and loaded from JSON files
7. Character data can be exported to PDF for printing

## Key Classes and Their Responsibilities

### BESMCharacterApp

- Main application window
- Manages the character data structure
- Coordinates between UI components and data model
- Handles file operations (save, load, export)

### TemplateDialog

- Displays available templates
- Allows selection and application of templates
- Handles template loading from the file system

### AttributeBuilderDialog

- Interface for creating and editing attributes
- Handles attribute configuration (level, enhancements, limiters)
- Validates attribute settings

## Data Model

The character data is stored in a nested dictionary structure:

```python
character_data = {
    "name": str,
    "player": str,
    "race": str,
    "class": str,
    "size": str,
    "stats": {
        "Body": int,
        "Mind": int,
        "Soul": int
    },
    "attributes": [
        {
            "id": str,
            "name": str,
            "key": str,
            "level": int,
            "user_description": str,
            "enhancements": [],
            "limiters": [],
            "options": [],
            "cost": int
        }
    ],
    "defects": [
        {
            "id": str,
            "name": str,
            "key": str,
            "rank": int,
            "user_description": str,
            "cost": int
        }
    ],
    "alternate_forms": [],
    "companions": [],
    "minions": [],
    "items": []
}
```

## Template System

Templates are loaded from individual JSON files in the templates directory. The template system:

1. Reads the index.json file to get a list of available templates
2. Loads individual template files based on the selected template
3. Applies the template's attributes, defects, and stat adjustments to the character

Templates follow a consistent structure with type-specific variations:

- Race templates use "race_name" for the display name
- Class templates use "class_name" for the display name
- Size templates use "name" for the display name
- All templates use "key" for lookups
- Attributes use "level" for their power rating (BESM 4e terminology)
- Defects use "rank" for their power rating (BESM 4e terminology)

## BESM Terminology Handling

The application maintains BESM 4e terminology distinctions:
- Attributes use "level" for their power rating
- Defects use "rank" for their power rating

This distinction is preserved throughout the codebase for consistency with the game system.

## Attribute and Defect Lookup

The application uses two methods for looking up attributes and defects:
1. By name using dictionaries (`self.attributes` and `self.defects`)
2. By key using dictionaries (`self.attributes_by_key` and `self.defects_by_key`)

The key-based lookup is preferred as it's more consistent, especially when handling singular/plural forms.

## Future Architecture Considerations

Potential improvements to the architecture include:

1. **Model-View-Controller (MVC) Pattern**: More clearly separate data, UI, and logic
2. **Event System**: Implement a more robust event system for UI updates
3. **Plugin System**: Allow for extensibility through plugins
4. **Database Backend**: Replace JSON files with a database for better performance with large datasets
5. **Unit Testing**: Add comprehensive test coverage
