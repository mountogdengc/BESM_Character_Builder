# BESM 4e Character Generator

![BESM 4e Logo](https://i.imgur.com/example.png) *(Replace with your own logo/screenshot)*

## Overview

The BESM 4e Character Generator is a desktop application designed to streamline character creation for the Big Eyes, Small Mouth 4th Edition role-playing game. This tool helps players and game masters quickly create, save, and export character sheets while ensuring rules compliance.

## Features

- **Intuitive Character Creation**: Step-by-step interface for creating BESM 4e characters
- **Template System**: Pre-built race, class, and size templates to speed up character creation
- **Custom Attributes & Defects**: Full support for all BESM 4e attributes and defects
- **Character Management**: Save, load, and export character data
- **PDF Export**: Generate professional character sheets ready for printing
- **Alternate Forms**: Support for characters with multiple forms
- **Companions & Minions**: Create and manage character companions and minions

## Screenshots

*(Add screenshots of your application here)*

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python besm_app.py
   ```

3. **Create a Character**:
   - Enter basic character information
   - Select race and class templates (optional)
   - Adjust stats (Body, Mind, Soul)
   - Add attributes and defects
   - Save your character

## Documentation

- [Requirements](requirements.md) - System requirements and dependencies
- [User Guide](docs/user_guide.md) - Detailed usage instructions
- [Template Documentation](docs/template_documentation.md) - How to create custom templates
- [Contributing](CONTRIBUTING.md) - Guidelines for contributors
- [Changelog](CHANGELOG.md) - Version history and updates
- [License](LICENSE) - License information

## Development Status

This application is actively maintained and developed. See the [Changelog](CHANGELOG.md) for recent updates and the [project roadmap](docs/roadmap.md) for planned features.

## Credits

Developed by Legendmasters.

BESM (Big Eyes, Small Mouth) is a trademark of Dyskami Publishing Company. This application is fan-made and not officially affiliated with or endorsed by Dyskami Publishing.

## License

This project is intended for personal use. See the [License](LICENSE) file for details.

# Enhancements and Limiters UI Improvements

This update introduces a cleaner, more intuitive UI for managing enhancements and limiters in the attribute builder.

## Changes Made

1. **Enhancement and Limiter Dialogs**: 
   - Created new dedicated dialogs for adding enhancements and limiters
   - Each dialog shows a filtered list with search functionality
   - Shows selections with counts (e.g., Area (3/6))

2. **Improved Display in Attribute Builder**:
   - New "Customization" section replaces the old multi-select lists
   - Separate buttons for adding enhancements and limiters
   - Selected items displayed in compact lists with counts

3. **Better Card Display**:
   - Attributes cards now show enhancements with (E) prefix and limiters with (L) prefix
   - Counts for each enhancement and limiter are clearly displayed
   - Example: "(E) Area (3)" and "(L) Maximum (1)"

4. **Data Storage Improvements**:
   - Enhancement and limiter counts are now stored in the attribute data
   - Maintains backward compatibility with the existing data structure

## Usage

1. To add enhancements, click the "Add Enhancements" button in the attribute builder
2. To add limiters, click the "Add Limiters" button
3. In each dialog, select items and use the +/- buttons to adjust counts
4. Selected items appear in the main attribute builder dialog
5. When viewing attributes in the main view, enhancements and limiters will show with their respective prefixes and counts

## Future Improvements

Possible future enhancements:
- Allow reordering of enhancements and limiters in the lists
- Add ability to search all enhancements and limiters at once
- Create customized displays for different attribute types
