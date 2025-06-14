# BESM 4e Character Generator Requirements

## Overview
This document outlines the requirements and dependencies for the BESM 4e Character Generator application, a tool designed to create and manage characters for the Big Eyes, Small Mouth 4th Edition role-playing game.

## System Requirements
- Windows, macOS, or Linux operating system
- Python 3.7 or higher

## Python Dependencies
The following Python packages are required to run the application:

```
PyQt5>=5.15.0
reportlab>=3.6.0
Pillow>=8.0.0
uuid>=1.30
```

## Installation Instructions

### 1. Install Python
If you don't have Python installed, download and install it from [python.org](https://python.org). Make sure to check the option to add Python to your PATH during installation.

### 2. Install Dependencies
Open a terminal or command prompt and run:

```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt file, you can install the dependencies individually:

```bash
pip install PyQt5 reportlab Pillow uuid
```

### 3. Run the Application
Navigate to the application directory and run:

```bash
python besm_app.py
```

## Application Structure

The application is organized as follows:

- `besm_app.py` - Main application entry point
- `data/` - JSON data files for attributes, defects, and templates
  - `attributes.json` - Attribute definitions
  - `defects.json` - Defect definitions
  - `templates/` - Character templates
    - `classes/` - Class templates
    - `races/` - Race templates
    - `sizes/` - Size templates
    - `index.json` - Index of all templates
- `tabs/` - UI tab implementations
- `tools/` - Utility functions and tools
- `dialogs/` - Dialog implementations
- `characters/` - Directory for saved character files

## Development Notes

### Terminology
- BESM 4e uses specific terminology:
  - Attributes use "level" for their power rating
  - Defects use "rank" for their power rating

### JSON Structure
- Templates are stored in individual files under classes, races, and sizes directories
- Each template has a corresponding entry in the index.json file
- Attributes use "custom_name", "key", and "level" fields
- Defects use "custom_name", "key", and "rank" fields

## License
This application is intended for personal use and is not affiliated with or endorsed by the publishers of BESM 4e. The Big Eyes, Small Mouth role-playing game is the property of Dyskami Publishing Company.
