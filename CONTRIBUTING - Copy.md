# Contributing to BESM 4e Character Generator

Thank you for your interest in contributing to the BESM 4e Character Generator! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Development Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/Legendmasters_Character_Generator.git
   cd Legendmasters_Character_Generator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python besm_app.py
   ```

## Code Style Guidelines

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused on a single responsibility
- Use consistent indentation (4 spaces, not tabs)

## Project Structure

- `besm_app.py` - Main application entry point
- `data/` - JSON data files
- `tabs/` - UI tab implementations
- `tools/` - Utility functions
- `dialogs/` - Dialog implementations
- `docs/` - Documentation files

## Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** and test them thoroughly
3. **Update documentation** if necessary
4. **Submit a pull request** with a clear description of the changes
5. **Address any feedback** from code reviews

## Reporting Bugs

When reporting bugs, please include:

- A clear description of the issue
- Steps to reproduce the bug
- Expected behavior
- Screenshots if applicable
- Your environment (OS, Python version, etc.)

## Feature Requests

Feature requests are welcome! Please provide:

- A clear description of the feature
- Why it would be valuable to the project
- Any implementation ideas you have

## Working with Templates

When creating or modifying templates:

- Follow the JSON schema defined in the documentation
- Ensure proper use of "level" for attributes and "rank" for defects
- Test templates thoroughly before submitting
- Include a description of what the template represents

## Testing

- Test your changes thoroughly before submitting a pull request
- Ensure the application runs without errors
- Verify that your changes don't break existing functionality
- Test on different operating systems if possible

## Documentation

- Update documentation when adding or changing features
- Follow the existing documentation style
- Include examples where appropriate
- Keep documentation clear and concise

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to the BESM 4e Character Generator!
