# BESM 4e Character Generator User Guide

This guide provides detailed instructions for using the BESM 4e Character Generator application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Main Interface](#main-interface)
3. [Character Creation](#character-creation)
4. [Using Templates](#using-templates)
5. [Managing Attributes](#managing-attributes)
6. [Managing Defects](#managing-defects)
7. [Alternate Forms](#alternate-forms)
8. [Companions and Minions](#companions-and-minions)
9. [Items](#items)
10. [Saving and Loading](#saving-and-loading)
11. [Exporting to PDF](#exporting-to-pdf)
12. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

1. Ensure you have Python 3.7 or higher installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python besm_app.py
   ```

### Initial Setup

When you first launch the application, you'll see the main character creation interface. The application automatically loads the necessary data files for attributes, defects, and templates.

## Main Interface

The main interface is organized into several tabs:

- **Character**: Basic character information and stats
- **Attributes**: Character attributes and powers
- **Defects**: Character defects and weaknesses
- **Items**: Equipment and possessions
- **Alternate Forms**: Additional forms the character can take
- **Metamorphosis**: Transformation capabilities
- **Companions**: Character companions
- **Minions**: Character minions

### Navigation

Use the tab bar at the top to navigate between different sections of the character sheet. Each tab contains controls specific to that aspect of character creation.

## Character Creation

### Basic Information

In the Character tab, enter the following information:

- **Character Name**: Your character's name
- **Player Name**: Your name as the player
- **Race**: Character's race (can be selected from templates)
- **Class**: Character's class or profession (can be selected from templates)
- **Size**: Character's size category (can be selected from templates)

### Character Points

The Character Points (CP) display shows:

- **Total CP**: Total character points available
- **Spent CP**: Points spent on attributes
- **Refunded CP**: Points refunded from defects
- **Remaining CP**: Points still available to spend

### Stats

Adjust your character's primary stats:

- **Body**: Physical capabilities
- **Mind**: Mental capabilities
- **Soul**: Spiritual capabilities

Each stat costs CP to increase. The cost is displayed next to each stat.

## Using Templates

Templates provide pre-configured sets of attributes, defects, and stat adjustments based on races, classes, and sizes from the BESM 4e rulebook.

### Applying Templates

1. Click the appropriate template button:
   - **Race Templates**: For racial characteristics
   - **Class Templates**: For profession-based abilities
   - **Size Templates**: For size-related traits

2. In the template dialog, select a template from the list

3. Click "Apply Template" to add the template's attributes and defects to your character

### Template Effects

When you apply a template:

- Attributes from the template are added to your character
- Defects from the template are added to your character
- Stats may be adjusted based on the template
- Size may be set based on the template

## Managing Attributes

The Attributes tab allows you to add, edit, and remove character attributes.

### Adding Attributes

1. Click the "Add Attribute" button
2. In the attribute dialog, select an attribute from the list
3. Set the attribute level (BESM 4e uses "level" for attribute power ratings)
4. Add any enhancements, limiters, or options
5. Click "Add" to add the attribute to your character

### Editing Attributes

1. Click on an attribute in the list
2. Modify the attribute's settings in the dialog
3. Click "Save" to update the attribute

### Removing Attributes

1. Select an attribute in the list
2. Click the "Remove" button to delete it

## Managing Defects

The Defects tab allows you to add, edit, and remove character defects.

### Adding Defects

1. Click the "Add Defect" button
2. In the defect dialog, select a defect from the list
3. Set the defect rank (BESM 4e uses "rank" for defect power ratings)
4. Add any relevant details
5. Click "Add" to add the defect to your character

### Editing Defects

1. Click on a defect in the list
2. Modify the defect's settings in the dialog
3. Click "Save" to update the defect

### Removing Defects

1. Select a defect in the list
2. Click the "Remove" button to delete it

## Alternate Forms

The Alternate Forms tab allows you to create different forms for your character, such as transformations or disguises.

### Creating Alternate Forms

1. Click "Add Form" in the Alternate Forms tab
2. Enter a name for the form
3. Configure the form's attributes and defects
4. Click "Save" to add the form

### Switching Between Forms

1. Select a form from the dropdown menu
2. The character sheet will update to show the selected form's attributes and defects

## Companions and Minions

### Adding Companions

1. Navigate to the Companions tab
2. Click "Add Companion"
3. Configure the companion's attributes and abilities
4. Click "Save" to add the companion

### Managing Minions

1. Navigate to the Minions tab
2. Click "Add Minion"
3. Configure the minion's attributes and abilities
4. Click "Save" to add the minion

## Items

The Items tab allows you to manage your character's equipment and possessions.

### Adding Items

1. Click "Add Item" in the Items tab
2. Enter the item's name and description
3. Configure any special properties
4. Click "Save" to add the item

## Saving and Loading

### Saving Characters

1. Click the "Save" button in the toolbar
2. Choose a location and filename
3. Click "Save" to save the character data

### Loading Characters

1. Click the "Load" button in the toolbar
2. Navigate to the character file
3. Click "Open" to load the character

## Exporting to PDF

To create a printable character sheet:

1. Click the "Export to PDF" button
2. Choose a location and filename
3. Click "Save" to generate the PDF

The PDF will include all character information formatted as a BESM 4e character sheet.

## Troubleshooting

### Common Issues

**Issue**: Application fails to start
**Solution**: Ensure all dependencies are installed with `pip install -r requirements.txt`

**Issue**: Templates not appearing
**Solution**: Check that the template files are in the correct directories and listed in index.json

**Issue**: Character points calculation seems incorrect
**Solution**: Verify that all attributes and defects have the correct level/rank values

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the project's GitHub issues page for known problems
2. Report new issues with detailed information about the problem
3. Include steps to reproduce the issue and any error messages

## Additional Resources

- [BESM 4e Rulebook](https://dyskami.ca/besm.html) - Official rules reference
- [Template Documentation](template_documentation.md) - Guide to creating custom templates
- [Project README](../README.md) - Project overview and quick start guide
