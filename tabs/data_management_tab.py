import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QSpinBox, QCheckBox, QProgressBar,
    QTextEdit, QScrollArea, QFrame, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer

def init_data_management_tab(app):
    """Initialize the data management tab"""
    tab = QWidget()
    layout = QVBoxLayout()
    
    # Create sub-tabs for different data management features
    tab_widget = QTabWidget()
    
    # Add Backup Management sub-tab
    backup_tab = create_backup_tab(app)
    tab_widget.addTab(backup_tab, "Backup Management")
    
    # Add Sync Settings sub-tab
    sync_tab = create_sync_tab(app)
    tab_widget.addTab(sync_tab, "Sync Settings")
    
    # Add Data Validation sub-tab
    validation_tab = create_validation_tab(app)
    tab_widget.addTab(validation_tab, "Data Validation")
    
    # Add Recovery Tools sub-tab
    recovery_tab = create_recovery_tab(app)
    tab_widget.addTab(recovery_tab, "Recovery Tools")
    
    layout.addWidget(tab_widget)
    tab.setLayout(layout)
    
    # Add the tab to the main application
    app.tabs.addTab(tab, "Data Management")
    return tab

def create_backup_tab(app):
    """Create the backup management sub-tab"""
    tab = QWidget()
    layout = QVBoxLayout()
    
    # Backup Settings Group
    settings_group = QGroupBox("Backup Settings")
    settings_layout = QFormLayout()
    
    # Auto-backup interval
    auto_backup_interval = QSpinBox()
    auto_backup_interval.setRange(1, 60)
    auto_backup_interval.setValue(app.settings.value("auto_backup_interval", 15, type=int))
    auto_backup_interval.valueChanged.connect(
        lambda v: app.settings.setValue("auto_backup_interval", v)
    )
    settings_layout.addRow("Auto-backup interval (minutes):", auto_backup_interval)
    
    # Max backups to keep
    max_backups = QSpinBox()
    max_backups.setRange(1, 100)
    max_backups.setValue(app.settings.value("max_backups", 10, type=int))
    max_backups.valueChanged.connect(
        lambda v: app.settings.setValue("max_backups", v)
    )
    settings_layout.addRow("Maximum backups to keep:", max_backups)
    
    settings_group.setLayout(settings_layout)
    layout.addWidget(settings_group)
    
    # Backup Actions Group
    actions_group = QGroupBox("Backup Actions")
    actions_layout = QVBoxLayout()
    
    # Manual backup button
    backup_btn = QPushButton("Create Manual Backup")
    backup_btn.clicked.connect(lambda: create_manual_backup(app))
    actions_layout.addWidget(backup_btn)
    
    # View backups button
    view_btn = QPushButton("View Backup History")
    view_btn.clicked.connect(app.open_backup_manager)
    actions_layout.addWidget(view_btn)
    
    actions_group.setLayout(actions_layout)
    layout.addWidget(actions_group)
    
    # Status Group
    status_group = QGroupBox("Backup Status")
    status_layout = QVBoxLayout()
    
    # Last backup info
    last_backup_label = QLabel("Last backup: Never")
    status_layout.addWidget(last_backup_label)
    
    # Next auto-backup info
    next_backup_label = QLabel("Next auto-backup: Not scheduled")
    status_layout.addWidget(next_backup_label)
    
    status_group.setLayout(status_layout)
    layout.addWidget(status_group)
    
    # Add stretch to push everything up
    layout.addStretch()
    
    tab.setLayout(layout)
    return tab

def create_sync_tab(app):
    """Create the sync settings sub-tab"""
    tab = QWidget()
    layout = QVBoxLayout()
    
    # Sync Settings Group
    settings_group = QGroupBox("Sync Settings")
    settings_layout = QFormLayout()
    
    # Enable cloud sync
    cloud_sync = QCheckBox()
    cloud_sync.setChecked(app.settings.value("cloud_sync_enabled", False, type=bool))
    cloud_sync.stateChanged.connect(
        lambda state: app.settings.setValue("cloud_sync_enabled", bool(state))
    )
    settings_layout.addRow("Enable Cloud Sync:", cloud_sync)
    
    # Sync frequency
    sync_interval = QSpinBox()
    sync_interval.setRange(1, 60)
    sync_interval.setValue(app.settings.value("sync_interval", 5, type=int))
    sync_interval.valueChanged.connect(
        lambda v: app.settings.setValue("sync_interval", v)
    )
    settings_layout.addRow("Sync interval (minutes):", sync_interval)
    
    settings_group.setLayout(settings_layout)
    layout.addWidget(settings_group)
    
    # Sync Status Group
    status_group = QGroupBox("Sync Status")
    status_layout = QVBoxLayout()
    
    # Last sync info
    last_sync_label = QLabel("Last sync: Never")
    status_layout.addWidget(last_sync_label)
    
    # Sync progress
    sync_progress = QProgressBar()
    sync_progress.setVisible(False)
    status_layout.addWidget(sync_progress)
    
    status_group.setLayout(status_layout)
    layout.addWidget(status_group)
    
    # Add stretch
    layout.addStretch()
    
    tab.setLayout(layout)
    return tab

def create_validation_tab(app):
    """Create the data validation sub-tab"""
    tab = QWidget()
    layout = QVBoxLayout()
    
    # Validation Settings Group
    settings_group = QGroupBox("Validation Settings")
    settings_layout = QFormLayout()
    
    # Enable auto-validation
    auto_validate = QCheckBox()
    auto_validate.setChecked(app.settings.value("auto_validate", True, type=bool))
    auto_validate.stateChanged.connect(
        lambda state: app.settings.setValue("auto_validate", bool(state))
    )
    settings_layout.addRow("Enable automatic validation:", auto_validate)
    
    settings_group.setLayout(settings_layout)
    layout.addWidget(settings_group)
    
    # Validation Results Group
    results_group = QGroupBox("Validation Results")
    results_layout = QVBoxLayout()
    
    # Results text area
    results_text = QTextEdit()
    results_text.setReadOnly(True)
    results_layout.addWidget(results_text)
    
    # Validate button
    validate_btn = QPushButton("Validate Now")
    validate_btn.clicked.connect(lambda: validate_character_data(app, results_text))
    results_layout.addWidget(validate_btn)
    
    results_group.setLayout(results_layout)
    layout.addWidget(results_group)
    
    # Add stretch
    layout.addStretch()
    
    tab.setLayout(layout)
    return tab

def create_recovery_tab(app):
    """Create the recovery tools sub-tab"""
    tab = QWidget()
    layout = QVBoxLayout()
    
    # Recovery Tools Group
    tools_group = QGroupBox("Recovery Tools")
    tools_layout = QVBoxLayout()
    
    # Repair database button
    repair_btn = QPushButton("Repair Database")
    repair_btn.clicked.connect(lambda: repair_database(app))
    tools_layout.addWidget(repair_btn)
    
    # Verify file integrity button
    verify_btn = QPushButton("Verify File Integrity")
    verify_btn.clicked.connect(lambda: verify_file_integrity(app))
    tools_layout.addWidget(verify_btn)
    
    # Import from backup button
    import_btn = QPushButton("Import from Backup")
    import_btn.clicked.connect(lambda: import_from_backup(app))
    tools_layout.addWidget(import_btn)
    
    tools_group.setLayout(tools_layout)
    layout.addWidget(tools_group)
    
    # Recovery Log Group
    log_group = QGroupBox("Recovery Log")
    log_layout = QVBoxLayout()
    
    # Log text area
    log_text = QTextEdit()
    log_text.setReadOnly(True)
    log_layout.addWidget(log_text)
    
    log_group.setLayout(log_layout)
    layout.addWidget(log_group)
    
    # Add stretch
    layout.addStretch()
    
    tab.setLayout(layout)
    return tab

def create_manual_backup(app):
    """Create a manual backup of the character data"""
    success, path, error = app.backup_manager.create_backup(app.character_data, manual=True)
    if success:
        app.statusBar().showMessage(f"Backup created successfully at {path}", 5000)
    else:
        app.statusBar().showMessage(f"Backup failed: {error}", 5000)

def validate_character_data(app, results_text):
    """Validate the character data and display results"""
    results = []
    
    # Check required fields
    required_fields = ["name", "stats", "attributes", "defects"]
    for field in required_fields:
        if field not in app.character_data:
            results.append(f"ERROR: Missing required field '{field}'")
    
    # Check stats
    stats = app.character_data.get("stats", {})
    for stat in ["Body", "Mind", "Soul"]:
        if stat not in stats:
            results.append(f"ERROR: Missing required stat '{stat}'")
        elif not isinstance(stats[stat], (int, float)):
            results.append(f"ERROR: Invalid value for stat '{stat}'")
    
    # Check attributes
    attributes = app.character_data.get("attributes", [])
    if not isinstance(attributes, list):
        results.append("ERROR: 'attributes' must be a list")
    else:
        for i, attr in enumerate(attributes):
            if not isinstance(attr, dict):
                results.append(f"ERROR: Attribute at index {i} is not a valid object")
            elif "name" not in attr or "level" not in attr:
                results.append(f"ERROR: Attribute at index {i} missing required fields")
    
    # Check defects
    defects = app.character_data.get("defects", [])
    if not isinstance(defects, list):
        results.append("ERROR: 'defects' must be a list")
    else:
        for i, defect in enumerate(defects):
            if not isinstance(defect, dict):
                results.append(f"ERROR: Defect at index {i} is not a valid object")
            elif "name" not in defect or "cost" not in defect:
                results.append(f"ERROR: Defect at index {i} missing required fields")
    
    # Display results
    if results:
        results_text.setTextColor(Qt.red)
        results_text.setText("\n".join(results))
    else:
        results_text.setTextColor(Qt.green)
        results_text.setText("✓ Character data is valid")

def repair_database(app):
    """Attempt to repair the character database"""
    try:
        # Implementation would go here
        app.statusBar().showMessage("Database repair not yet implemented", 5000)
    except Exception as e:
        app.statusBar().showMessage(f"Database repair failed: {str(e)}", 5000)

def verify_file_integrity(app):
    """Verify the integrity of character files"""
    try:
        # Implementation would go here
        app.statusBar().showMessage("File integrity verification not yet implemented", 5000)
    except Exception as e:
        app.statusBar().showMessage(f"File integrity verification failed: {str(e)}", 5000)

def import_from_backup(app):
    """Import character data from a backup file"""
    try:
        # Implementation would go here
        app.statusBar().showMessage("Backup import not yet implemented", 5000)
    except Exception as e:
        app.statusBar().showMessage(f"Backup import failed: {str(e)}", 5000) 