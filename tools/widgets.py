# widgets.py
from PyQt5.QtWidgets import QWidget, QListWidget, QLabel, QHBoxLayout, QFormLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeyEvent

class ClickableCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()

class AttributeListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.delete_callback = None  # Set externally

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete and self.delete_callback:
            self.delete_callback()
        else:
            super().keyPressEvent(event)

class LabeledRowWithHelp(QWidget):
    def __init__(self, label_text, widget, help_text="", parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setFixedWidth(150)

        help_icon = QLabel("❓")
        help_icon.setToolTip(help_text)
        help_icon.setStyleSheet("color: gray; font-weight: bold;")
        help_icon.setFixedWidth(20)
        help_icon.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        layout.addWidget(help_icon)
        layout.addWidget(widget)

        self.setLayout(layout)
        self.row_label = label
        self.help_icon = help_icon
        self.content_widget = widget