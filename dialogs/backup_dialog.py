import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QMessageBox, QFileDialog, QWidget, QFormLayout
)
from PyQt5.QtCore import Qt

class BackupDialog(QDialog):
    def __init__(self, parent=None, backup_manager=None):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.setWindowTitle("Backup Manager")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self.init_ui()
        self.load_backup_history()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Backup history list
        self.backup_list = QListWidget()
        self.backup_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(QLabel("Backup History:"))
        layout.addWidget(self.backup_list)
        
        # Backup details
        details_group = QWidget()
        details_layout = QFormLayout()
        self.details_widgets = {
            "Character": QLabel(),
            "Date": QLabel(),
            "Type": QLabel(),
            "Status": QLabel()
        }
        for label, widget in self.details_widgets.items():
            details_layout.addRow(f"{label}:", widget)
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_backup_btn = QPushButton("Create Backup")
        self.create_backup_btn.clicked.connect(self.create_backup)
        button_layout.addWidget(self.create_backup_btn)
        
        self.restore_btn = QPushButton("Restore Selected")
        self.restore_btn.clicked.connect(self.restore_backup)
        self.restore_btn.setEnabled(False)
        button_layout.addWidget(self.restore_btn)
        
        self.verify_btn = QPushButton("Verify Selected")
        self.verify_btn.clicked.connect(self.verify_backup)
        self.verify_btn.setEnabled(False)
        button_layout.addWidget(self.verify_btn)
        
        self.export_btn = QPushButton("Export Backup")
        self.export_btn.clicked.connect(self.export_backup)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.backup_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.setLayout(layout)
        
    def load_backup_history(self):
        """Load and display backup history"""
        self.backup_list.clear()
        history = self.backup_manager.get_backup_history()
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        for backup in history:
            timestamp = datetime.strptime(backup["timestamp"], "%Y%m%d_%H%M%S")
            display_text = f"{backup['character_name']} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({backup['type']})"
            self.backup_list.addItem(display_text)
            
    def on_selection_changed(self):
        """Update details when selection changes"""
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            self.restore_btn.setEnabled(False)
            self.verify_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            for widget in self.details_widgets.values():
                widget.setText("")
            return
            
        index = self.backup_list.row(selected_items[0])
        history = self.backup_manager.get_backup_history()
        backup = history[index]
        
        # Update details
        self.details_widgets["Character"].setText(backup["character_name"])
        timestamp = datetime.strptime(backup["timestamp"], "%Y%m%d_%H%M%S")
        self.details_widgets["Date"].setText(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        self.details_widgets["Type"].setText(backup["type"].capitalize())
        
        # Enable buttons
        self.restore_btn.setEnabled(True)
        self.verify_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
    def create_backup(self):
        """Create a new backup"""
        success, path, error = self.backup_manager.create_backup(
            self.parent().character_data,
            manual=True
        )
        
        if success:
            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup created successfully:\n{os.path.basename(path)}"
            )
            self.load_backup_history()
        else:
            QMessageBox.critical(
                self,
                "Backup Failed",
                f"Failed to create backup:\n{error}"
            )
            
    def restore_backup(self):
        """Restore selected backup"""
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            return
            
        index = self.backup_list.row(selected_items[0])
        history = self.backup_manager.get_backup_history()
        backup = history[index]
        
        # Confirm restore
        reply = QMessageBox.question(
            self,
            "Confirm Restore",
            f"Are you sure you want to restore backup of '{backup['character_name']}'?\n"
            "This will overwrite your current character data.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            backup_path = os.path.join(self.backup_manager.backup_dir, backup["filename"])
            success, data, error = self.backup_manager.restore_backup(backup_path)
            
            if success:
                # Update parent's character data
                self.parent().character_data = data
                self.parent().load_character_into_ui()
                self.parent().update_point_total()
                
                QMessageBox.information(
                    self,
                    "Restore Complete",
                    "Character data restored successfully."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Restore Failed",
                    f"Failed to restore backup:\n{error}"
                )
                
    def verify_backup(self):
        """Verify selected backup"""
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            return
            
        index = self.backup_list.row(selected_items[0])
        history = self.backup_manager.get_backup_history()
        backup = history[index]
        
        backup_path = os.path.join(self.backup_manager.backup_dir, backup["filename"])
        success, error = self.backup_manager.verify_backup(backup_path)
        
        if success:
            QMessageBox.information(
                self,
                "Verification Complete",
                "Backup verified successfully."
            )
            self.details_widgets["Status"].setText("Verified")
        else:
            QMessageBox.warning(
                self,
                "Verification Failed",
                f"Backup verification failed:\n{error}"
            )
            self.details_widgets["Status"].setText("Failed")
            
    def export_backup(self):
        """Export selected backup to user-selected location"""
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            return
            
        index = self.backup_list.row(selected_items[0])
        history = self.backup_manager.get_backup_history()
        backup = history[index]
        
        # Get export location
        default_name = f"backup_{backup['character_name']}_{backup['timestamp']}.json"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Backup",
            default_name,
            "JSON Files (*.json)"
        )
        
        if path:
            try:
                backup_path = os.path.join(self.backup_manager.backup_dir, backup["filename"])
                shutil.copy2(backup_path, path)
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Backup exported to:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export backup:\n{str(e)}"
                ) 