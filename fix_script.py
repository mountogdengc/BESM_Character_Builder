import re

with open('dialogs/attribute_builder_dialog.py', 'r', encoding='utf-8') as file:
    content = file.readlines()

# Print line number where "Initial category value:" appears
for i, line in enumerate(content):
    if "Initial category value:" in line and "currentText" in line and not "isinstance" in content[i-1]:
        print(f"Found problematic line at {i+1}: {line.strip()}")

# Manually identify the problematic section
problematic_section = []
fix_applied = False

for i in range(len(content)):
    if "Initial category value:" in content[i] and "currentText" in content[i]:
        # Check if this is already a fixed section with isinstance check
        if i > 0 and "isinstance" in content[i-1]:
            continue
        
        # We found the problematic section, replace the next few lines
        print(f"Found issue at line {i+1}")
        
        # Get the indentation level
        indent = len(content[i]) - len(content[i].lstrip())
        indent_str = ' ' * indent
        
        # Replace with fixed code
        replacement = [
            f"{indent_str}widget = self.custom_input_widgets[self.dynamic_cost_category_key]\n",
            f"{indent_str}if isinstance(widget, QComboBox):\n",
            f"{indent_str}    print(\"[DEBUG INIT] Initial category value:\", widget.currentText())\n",
            f"{indent_str}elif isinstance(widget, QTextEdit):\n",
            f"{indent_str}    print(\"[DEBUG INIT] Initial category value:\", widget.toPlainText())\n",
            f"{indent_str}elif isinstance(widget, QLineEdit):\n",
            f"{indent_str}    print(\"[DEBUG INIT] Initial category value:\", widget.text())\n",
            f"{indent_str}else:\n",
            f"{indent_str}    print(\"[DEBUG INIT] Initial category value: [Unknown widget type]\", type(widget))\n"
        ]
        
        # Modify the list by replacing the problematic line
        content[i] = replacement[0]  # Replace current line with widget assignment
        
        # Insert the remaining lines after the current position
        for j, line in enumerate(replacement[1:]):
            content.insert(i + j + 1, line)
        
        fix_applied = True
        break  # Only fix the first occurrence for safety

if fix_applied:
    with open('dialogs/attribute_builder_dialog.py', 'w', encoding='utf-8') as file:
        file.writelines(content)
    print("File updated successfully!")
else:
    print("No changes made to the file.") 