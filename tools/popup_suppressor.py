from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

class PopupSuppressor:
    """
    Utility class to hide any top-level windows that might appear
    as orphaned widgets during template application.
    """
    @staticmethod
    def install():
        """Install the popup suppressor"""
        # Create a timer to periodically check for and hide orphaned top-level windows
        timer = QTimer()
        timer.timeout.connect(PopupSuppressor.hide_orphaned_windows)
        timer.start(100)  # Check every 100ms
        
        # Store the timer as an application property to prevent garbage collection
        QApplication.instance().popup_suppressor_timer = timer
    
    @staticmethod
    def hide_orphaned_windows():
        """Hide any top-level windows that might be orphaned attribute cards"""
        for widget in QApplication.topLevelWidgets():
            # If it's small and has no parent, it's likely an orphaned card
            if widget.width() < 400 and widget.height() < 400 and not widget.parentWidget():
                # Hide it immediately
                widget.setVisible(False)
                # Schedule it for deletion
                widget.deleteLater()
