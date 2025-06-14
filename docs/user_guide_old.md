# BESM 4e Character Builder User Documentation

## Table of Contents
- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Launching the Application](#launching-the-application)
- [User Interface Overview](#user-interface-overview)
  - [Sidebar](#sidebar)
  - [Main Content Area](#main-content-area)
  - [Tabs](#tabs)
- [Character Management](#character-management)
  - [Creating a New Character](#creating-a-new-character)
  - [Loading a Character](#loading-a-character)
  - [Saving a Character](#saving-a-character)
  - [Exporting to PDF](#exporting-to-pdf)
- [Editing Character Details](#editing-character-details)
  - [Basic Information](#basic-information)
  - [Attributes](#attributes)
  - [Defects](#defects)
  - [Weapons, Items, and Minions](#weapons-items-and-minions)
- [Templates](#templates)
  - [Applying Templates](#applying-templates)
  - [Managing Templates](#managing-templates)
- [Dynamic Tabs](#dynamic-tabs)
  - [Alternate Forms](#alternate-forms)
  - [Companions](#companions)
  - [Metamorphosis](#metamorphosis)
  - [Minions](#minions)
- [Character Points and Benchmarks](#character-points-and-benchmarks)
  - [Managing Character Points](#managing-character-points)
  - [Using Benchmarks](#using-benchmarks)
- [Advanced Features](#advanced-features)
  - [Custom Rules and Fields](#custom-rules-and-fields)
  - [Derived Values](#derived-values)
- [Troubleshooting](#troubleshooting)
- [About](#about)

## 1. Introduction
The BESM 4e Character Builder is a tool designed to help players and game masters create and manage characters for the BESM (Big Eyes, Small Mouth) 4th Edition tabletop role-playing game. It provides an intuitive interface for managing stats, attributes, defects, and other character details.

## 2. Getting Started

### Installation
1. Ensure you have Python 3.8+ installed on your system.
2. Install the required dependencies using:
   ```bash
   pip install -r requirements.txt
   ```
3. Place the application files in a directory of your choice.

### Launching the Application
Run the application using:
   ```bash
   python main.py
   ```

## 3. User Interface Overview

### Sidebar
The sidebar contains buttons for common actions:
- **New Character**: Create a new character.
- **Load Character**: Load an existing character from a file.
- **Save Character**: Save the current character to a file.
- **Export to PDF**: Export the character to a PDF file.
- **Options**: Access additional settings and features.

### Main Content Area
The main content area displays character details, attributes, defects, and other information. It is divided into tabs for easy navigation.

### Tabs
The application includes the following tabs:
- **Stats**: Manage base stats like Body, Mind, and Soul.
- **Attributes**: Add, edit, or remove character attributes.
- **Defects**: Manage character defects.
- **Dynamic Tabs**: Additional tabs for Alternate Forms, Companions, Items, Metamorphosis, and Minions.

## 4. Character Management

### Creating a New Character
1. Click the **New Character** button in the sidebar.
2. Fill in the character's basic details and stats.

### Loading a Character
1. Click the **Load Character** button.
2. Select a JSON file containing the character data.

### Saving a Character
1. Click the **Save Character** button.
2. Choose a location to save the character as a JSON file.

### Exporting to PDF
1. Click the **Export to PDF** button.
2. Choose a location to save the PDF file.

## 5. Editing Character Details

### Basic Information
Edit fields like:
- Character Name
- Player Name
- Game Master Name
- Race/Species
- Class/Occupation
- Home World/Habitat
- Size/Height/Weight/Gender

### Attributes
1. Click **Add Attribute** to open the Attribute Builder dialog.
2. Fill in the attribute details and click **OK**.
3. Use the **Edit** or **Remove** options to modify or delete attributes.

### Defects
1. Click **Add Defect** to open the Defect Builder dialog.
2. Fill in the defect details and click **OK**.
3. Use the **Edit** or **Remove** options to modify or delete defects.

### Weapons, Items, and Minions
1. Add new weapons, items, or minions using the respective buttons.
2. Edit or remove them as needed.

## 6. Templates

### Applying Templates
1. Click a template button (e.g., **Race Templates**).
2. Select a template from the dialog and apply it to the character.

### Managing Templates
1. Click **Manage Templates**.
2. View or remove applied templates.

## 7. Dynamic Tabs

### Alternate Forms
Manage alternate forms for the character, including stats and attributes.

### Companions
Add and manage companions with their own stats and abilities.

### Metamorphosis
Track transformative states with unique stats and abilities.

### Minions
Add and manage minions that assist the character.

## 8. Character Points and Benchmarks

### Managing Character Points
1. Adjust starting and earned CP using the input fields.
2. View spent and unspent CP in the summary section.

### Using Benchmarks
1. Select a benchmark from the dropdown to guide character creation.
2. Suggested benchmarks are displayed based on total CP.

## 9. Advanced Features

### Custom Rules and Fields
Add custom rules or fields to tailor the character to your campaign.

### Derived Values
The app calculates derived values like Combat Value (CV), Health Points (HP), and Energy Points (EP) based on stats and modifiers.

## 10. Troubleshooting

### Issue: Missing benchmarks
**Solution**: Ensure `benchmarks.json` is in the data folder.

### Issue: UI not updating
**Solution**: Restart the application or refresh the UI.

## 11. About
- **Version**: 0.1
- **Developer**: Legendmasters
- **Description**: A character generator for BESM 4e.