        # Debug output
        print("[DEBUG INIT] Loaded Attribute:", attr_name)
        print("[DEBUG INIT] Dynamic Cost Map:", self.dynamic_cost_map)
        print("[DEBUG INIT] Dynamic Key:", self.dynamic_cost_category_key)
        if self.dynamic_cost_category_key in self.custom_input_widgets:
            print("[DEBUG INIT] Found widget for key")
            widget = self.custom_input_widgets[self.dynamic_cost_category_key]
            if isinstance(widget, QComboBox):
                print("[DEBUG INIT] Initial category value:", widget.currentText())
            elif isinstance(widget, QTextEdit):
                print("[DEBUG INIT] Initial category value:", widget.toPlainText())
            elif isinstance(widget, QLineEdit):
                print("[DEBUG INIT] Initial category value:", widget.text())
            else:
                print("[DEBUG INIT] Initial category value: [Unknown widget type]", type(widget)) 